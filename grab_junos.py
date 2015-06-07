#!/usr/bin/python
# Author: Scott Reisinger
# Date: 06062015
# Purpose: Automate config grab for JUNOS devices (Or any other vendor but Juniper is the best so..)
#
# You will need to install the SSH utilities from paramiko 
# If you are on a mac there is an easy tutorial here:
# http://osxdaily.com/2012/07/10/how-to-install-paramiko-and-pycrypto-in-mac-os-x-the-easy-way/

#Import some good tools this so reminds me of C++
from sys import argv
import os
import getpass
import exceptions
import logging
import subprocess
import time
logging.basicConfig()

#These are needed for the paramiko routine
import sys
import socket
import pprint
import paramiko

mytime = time.strftime("%m%d%y%H%M%S")

print "START TIME", mytime

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Sub routine get_password
def get_password():
        #print "Please enter your password:"
        os.system("stty -echo")
        #local_password = raw_input( getpass.getuser() + "'s password")
        local_password = raw_input( username + "'s password> ")
        os.system("stty echo")
        print "\n"

        return local_password
# Check TCP 22 connection
def Check_SSH(IP):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
                s.connect((IP, 22))
                s.shutdown(2)
                return True
        except:
                print "%s SSH connection failed" % (IP)
                return False

def IPCMD(ipAddress, command, username, password):
    if Check_SSH(ipAddress):
        try:
                buff_size = 2048
                print "Running: %s on %s" % (command, ipAddress)
                ssh.connect(ipAddress, username=username, password=password, timeout=3)
                stdin, stdout, stderr = ssh.exec_command(command)

                if len(stderr.readlines()) > 0:
                        print stderr.readlines()

                # For verbose print, if not desired, comment out next 3 lines
                #output = stdout.readlines()
                #output = sys.stdout
                #output = map(lambda s: s.strip().encode("utf-8"), output)

                #filename
                fout = str(ipAddress + '_' + mytime + '.txt')

                ssh.close()

        except paramiko.AuthenticationException:
                print "%s Authentication failed" % (ipAddress)

        finally:
                with open(fout, 'w') as output:
                        output.write(''.join(stdout))
                with open('Error_Log.txt', 'w') as output:
                        output.write(''.join(stderr))           


# Lets grab the SSH credentials right from the start
print "Please enter your username: :",
username = raw_input("> ")

print "Please enter your password: :",
password = get_password()

# Now lets figure out if this is going to be a single ip or a list and a single command or a list
print "Do you want to run this for a (S)ingle IP or a (L)ist of IPs (S/L)?: ",
ipSource = raw_input("> ")

if ipSource == 'S' or ipSource == 's':
        print "Please enter the IP address you want to query: ",
        ipAddress = raw_input("> ")
elif ipSource == 'L' or ipSource == 'l':
        print "Please enter the filename of the IP List (e.g. /home/scott/IPLIST): ",
        ipList = raw_input("> ")
else:
        print "\t ERROR: S and L are the only valid responses for this prompt"


# What is our source for the coammnds single or file
print "\n\nDo you want to run a (S)ingle command or a (L)ist of commands (S/L)?: ",
cmdSource = raw_input("> ")

if cmdSource == 'S' or cmdSource == 's':
        print "Please enter the command you want to run on the device(s): "
        command = raw_input("> ")
elif cmdSource == 'L' or cmdSource == 'l':
        print "Please enter the filename of the command List (e.g. /home/scott/JUNOSCMDS): ",
        cmdFile = raw_input("> ")
        COMMANDS = open(cmdFile, 'r')
else:
        print "\t ERROR: S and L are the only valid responses for this prompt"

def IP1CMDS(ipAddress, cmdFile):
        fcmds = open(cmdFile, 'r')
        for CMD in fcmds.readlines():
                CMD = CMD.rstrip()
                IPCMD(ipAddress, CMD, username, password)

def IPSCMD1(ipList, command):
        ip = open(ipList, 'r')
        for ip in ip.readlines():
                ip = ip.rstrip()
                IPCMD(ip, command, username, password)
def rewind(f):
    f.seek(0)

def IPSCMDS(ipList, cmdFile):
        ip = open(ipList, 'r')
        fcmds = open(cmdFile)
        for ip in ip.readlines():
                ip = ip.rstrip()
                rewind(fcmds)
                for CMD in fcmds.readlines():
                        CMD = CMD.rstrip()
                        print ip
                        print CMD

                        IPCMD(ip, CMD, username, password)


if ((ipSource == 'S' or ipSource == 's') and (cmdSource == 'S' or cmdSource == 's')):
        IPCMD(ipAddress, command, username, password)
elif ((ipSource == 'S' or ipSource == 's') and (cmdSource == 'L' or cmdSource == 'l')):
        IP1CMDS(ipAddress, cmdFile)
elif ((ipSource == 'L' or ipSource == 'l') and (cmdSource == 'S' or cmdSource == 's')):
        IPSCMD1(ipList, command)
elif ((ipSource == 'L' or ipSource == 'l') and (cmdSource == 'L' or cmdSource == 'l')):
        IPSCMDS(ipList, cmdFile)
else:
        print "You entered some weird combo. S and L are the only valid choices"
