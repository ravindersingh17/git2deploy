import subprocess
import os

class retdata: pass

class executer:
    def run(command):
        ret = retdata()
        ret.returncode = subprocess.call(command, shell=True)
        return ret

    def runwithoutput(command):
        ret = subprocess.call(command, stdout=subprocess.PIPE, shell=True)
        ret.output = ret.stdout.decode('utf-8')
        return ret
