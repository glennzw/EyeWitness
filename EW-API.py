from flask import Flask
from subprocess import Popen, call, PIPE
import shlex
import string
import random
import json
from shutil import copyfile
import glob
import os

TMP="/tmp/"
SAVEDIR = "/root/EyeWitness/screenies/"
EW_EXE = "/root/EyeWitness/EyeWitness.py"

app = Flask(__name__)


@app.route('/getImage/<image>')
def getImage(image):
    if not image or image == "":
        return """{"status" : "error", "reason" : "Bad URL"}"""
    return send_file(SAVEDIR + filename, mimetype='image/gif')

@app.route('/snapshotSite/<url>')
def snapshot(url):
    if not url or url == "":
      return """{"status" : "error", "reason" : "Bad URL"}"""

    uidd = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    savePath = SAVEDIR + uidd + "/"
    tmpPath = TMP + uidd

    rcmd = "python " + EW_EXE + " --single " + url + " --web -d " + tmpPath
    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options=cmd[1:]   

    proc  = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
    response_stdout, response_stderr = proc.communicate()
    print response_stdout
    print response_stderr
    if proc.wait() != 0:
      return """{"status" : "error", "reason" : "Unable to screenshot site"}"""
    if "Report written in the" not in response_stdout:
      return """{"status" : "error", "reason" : "Unable to save screenshot to disk"}"""
    os.mkdir(savePath)

    for file in glob.glob(r"%s/screens/*" % tmpPath):
        print file                                                                                                                                        
        copyfile(file, savePath + file.split("/")[-1])

    rtn = "http://178.62.120.37/%s/%s" %(uidd, file.split("/")[-1])
    return """{"status" : "success", "screenshot" : "%s"}""" % rtn

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

