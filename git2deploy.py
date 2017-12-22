import socket
import threading
import sys, os
import logging
import time
from daemon import Daemon
SOCK_ADDR = "/tmp/git2deploy.sock"

class client(threading.Thread):
    def __init__(self, conn):
        super(client, self).__init__()
        self.conn = conn
        self.data = b""

    def run(self):
        while True:
            self.data = self.data + self.conn.recv(1024)
            if self.data.endswith(b"\r\n"):
                logging.info(self.data.decode("utf-8"))
                self.data = b""

    def send_msg(self,msg):
        self.conn.send(msg)

    def close(self):
        self.conn.close()

class connectionThread(threading.Thread):
    def __init__(self, sock_addr):
        super(connectionThread, self).__init__()
        try:
            os.unlink(sock_addr)
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.s.bind(sock_addr)
            self.s.listen(5)
        except socket.error:
            logging.critical('Failed to create socket')
            sys.exit()
        self.clients = []

    def run(self):
        while True:
            logging.info("Waiting for connection..")
            conn, address = self.s.accept()
            logging.info("Client connected")
            c = client(conn)
            c.start()
            self.clients.append(c)

class G2dDaemon(Daemon):
    def run(self):
        logging.basicConfig(filename="/var/log/git2deploy.log", level=logging.DEBUG)
        get_conns = connectionThread(SOCK_ADDR)
        get_conns.start()
        while True:
            time.sleep(.1)



def main(arg):
    daemon = G2dDaemon("/var/run/git2deploy.pid")
    if arg == "start":
        daemon.start()
    elif arg == "stop":
        daemon.stop()
    elif arg == "restart":
        daemon.restart()
    else:
        print("Invalid option")

if __name__ == '__main__':
    main(sys.argv[1])
