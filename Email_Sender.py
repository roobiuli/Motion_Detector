#!/usr/bin/python
import os
import sys
import smtplib
from shutil import copy2
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from subprocess import Popen, PIPE
import argparse

parser = argparse.ArgumentParser(description="Wrapper to send emails for Motion ")
parser.add_argument('-s', dest='S', help="The source location where you want to store all generated images", required=True)
parser.add_argument('-i', dest="I",  help="The Input path where all the images will be generated or pmotion config file", required=True)
parser.add_argument('-D', dest="D", help="Target / Destination email address where all generated pictures will be sent", required=True)
args = parser.parse_args()

TEMP = []

def bash(command):
    com = Popen(command,  shell=True, stdout=PIPE,stderr=PIPE)
    out, err = com.communicate()
    return out, err, com.returncode

def send_email(sender, reciver, lis):
    msg = MIMEMultipart()
    msg['Subject'] = 'New Capture from'
    msg['From'] = sender
    msg['To'] = reciver
    msg.preamble = 'Capture Message'

    if len(lis) == 0:
        sys.exit(1)
    else:
        for pic in lis:
            command = "ls -lah " +  pic + " | awk  '{print $6, $7, $8}' | tr ' ' '_' "
            try:
                created = bash(command)[0]
            except OSError:
                print "Could not read picture {}".format(pic)
            fp = open(pic, 'rb')
            img = MIMEImage(fp.read(), _subtype="jpeg")
            img.add_header('Content-Disposition', "attachment; filename= {}".format(created))
            fp.close()

            msg.attach(img)
            s = smtplib.SMTP('localhost')
            s.sendmail(sender, reciver, msg.as_string())
            s.quit()

try:
    OLD = os.listdir(args.S)
    NEW = os.listdir(args.I)
except OSError:
    print "Could not Open on of the directories"
    sys.exit(0)

for item in NEW:
    if item not in OLD:
        print "Found new item {}".format(item)
        try:
            copy2(args.I + item, args.S )
        except OSError:
            print "Could not copy {} to /var/local/work/iulian".format(item)
            sys.exit(0)
        TEMP.append("/var/local/work/iulian/" + item)

send_email("robert@centuriondecisions.com", args.D, TEMP)


