import subprocess
import os

class retdata: pass

class executer:
    def run(command):
        ret = retdata()
        ret.returncode = subprocess.call(command, shell=True)
        return ret

    def runwithoutput(command):
        ret = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        ret.output = ret.stdout.read().decode('utf-8')
        return ret
