import socket
import threading
import sys, os
import logging
import time
from g2d.daemon import Daemon
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
                return

    def process(self):
        logging.info("Data {0}".format(self.data))
        # Break data into repo name, secret and payload
        try:
            repo, secret, payload = self.data.decode("utf-8").split(" ", 2)
        except Exception as e:
            logging.info("Error {0}".format(str(e)))
        logging.info("REPO:" + repo)
        logging.info("SECRET: " + secret)
        logging.info("PAYLOAD: " + payload)


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
            c = client(conn, repodata)
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
