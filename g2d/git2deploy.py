import socket
import threading
import sys, os
import logging
import time
import requests
from g2d.daemon import Daemon
from hashlib import sha1
from hashlib import md5
import hmac
import shutil
import json
from g2d.executer import executer
from urllib.parse import parse_qs

SOCK_ADDR = "/tmp/git2deploy.sock"
LOG_FILE = "/var/log/git2deploy.log"

class client(threading.Thread):
    def __init__(self, conn, repodata):
        super(client, self).__init__()
        self.conn = conn
        self.data = b""
        self.repodata = repodata

    def run(self):
        logging.info("In client process")
        while True:
            data = self.conn.recv(1024)
            if not data:
                break
            self.data = self.data + data
            if self.data.endswith(b"\r\n"):
                self.process()
                self.conn.close()

    def send_dev_message(self, payload):
        data = json.loads(parse_qs(payload.decode("utf-8"))["payload"][0])
        send = "<b>{} updated</b>\n".format(data["repository"]["name"])
        send += "Diff: {}\n".format(data["compare"])
        for c in data["commits"]:
            send += "Commit: {}\n".format(c["url"])
            send += "Message: {}\n".format(c["message"])
            send += "Author: {}\n".format(c["author"]["name"])
            for f in c["added"]: send += "A: {}\n".format(f)
            for f in c["removed"]: send += "D: {}\n".format(f)
            for f in c["modified"]: send += "M: {}\n".format(f)
        hangouts_port = 16000
        headers = {"content-type": "application/json"}
        r = requests.post("https://localhost:16000/1",data=json.dumps(send),headers=headers, verify=False)

    def process(self):
        # Break data into repo name, secret and payload
        try:
            repo, signature, payload = self.data.strip().split(b" ", 2)
        except Exception as e:
            logging.info("Invalid data")
            return
        repo = repo.decode("utf-8")
        if repo not in self.repodata:
            logging.info("Repo data not added. Add repo data for {0}". format(repo))
            return
        signature = signature.decode("utf-8")
        logging.debug("REPO:" + repo)
        logging.debug("SIGNATURE: " + signature)
        try:
            calculatedSignature = hmac.new(self.repodata[repo]["secret"].encode("utf-8"), payload, sha1).hexdigest()
            logging.info("Calculated signature {0}".format(calculatedSignature))
        except Exception as e:
            logging.info("Exception occured while calculating signature {0}".format(str(e)))
        if "sha1=" + calculatedSignature != signature:
            return
        logging.info("Sending message to registered developers")
        self.send_dev_message(payload)
        if self.repodata[repo]["deploydir"] != "":
            tmpPath = "/root/g2dfiles/{}".format(repo)
            if os.path.exists(tmpPath):
                shutil.rmtree(tmpPath)
            os.mkdir(tmpPath)
            os.chdir(tmpPath)
            logging.info("Cloning repository: " + "git clone https://github.com/{0}/{1}.git {2}".format(self.repodata[repo]["user"], repo, tmpPath))
            executer.run("git clone https://github.com/{0}/{1}.git {2}".format(self.repodata[repo]["user"], repo, tmpPath))
            logging.info("Copying files")
            os.chdir(tmpPath)
            executer.run("git archive master | tar -x -C {0}".format(self.repodata[repo]["deploydir"]))


    def send_msg(self,msg):
        self.conn.send(msg)

    def close(self):
        self.conn.close()

class connectionThread(threading.Thread):
    def __init__(self, sock_addr, repodata):
        self.repodata = repodata
        super(connectionThread, self).__init__()
        try:
            os.unlink(sock_addr)
        except FileNotFoundError:
            pass
        try:
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.s.bind(sock_addr)
            self.s.listen(5)
        except socket.error as e:
            logging.critical('Failed to create socket: {0}'.format(str(e)))
            sys.exit()
        self.clients = []

    def run(self):
        while True:
            logging.info("Waiting for connection..")
            conn, address = self.s.accept()
            logging.info("Client connected")
            c = client(conn, self.repodata)
            c.start()
            self.clients.append(c)

class G2dDaemon(Daemon):

    def __init__(self, pidfile, repodata):
        self.repodata = repodata
        super(G2dDaemon, self).__init__(pidfile)
    def run(self):
        logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
        get_conns = connectionThread(SOCK_ADDR, self.repodata)
        get_conns.start()
        while True:
            time.sleep(.1)
