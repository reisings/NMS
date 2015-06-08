#!/usr/bin/python
# Written by: Scott Reisinger
# Date: 06062015
# Purpose: Grab information from JUNOS devices and capture to a file
import pexpect 
import array
import getpass
import sys
import time
import getopt
import os
import exceptions
import logging

mytime = time.strftime("%m%d%y%H%M%S")

print "START TIME", mytime

def get_password():
        os.system("stty -echo")
        local_password = raw_input( username + "'s password> ")
        os.system("stty echo")
        print "\n"

        return local_password

def rewind(f):
    f.seek(0)

print "Do you want to run this for a (S)ingle IP or a (L)ist of IPs (S/L)?: ",
ipSource = raw_input("> ")

if ipSource == 'S' or ipSource == 's':
        print "\nPlease enter the IP address you want to query (e.g. 192.168.1.1): ",
        ipAddress = raw_input("> ")
	hosts = []
	hosts.append(ipAddress)
elif ipSource == 'L' or ipSource == 'l':
        print "\nPlease enter the filename of the IP List (e.g. /home/scott/IPLIST): ",
        ipList = raw_input("> ")
	addresses = open(ipList, 'r')
	hosts = addresses.readlines()
else:
        print "\t ERROR: S and L are the only valid responses for this prompt"


print "\n\nDo you want to run a (S)ingle command or a (L)ist of commands (S/L): ",
cmdSource = raw_input("> ")

if cmdSource == 'S' or cmdSource == 's':
        print "\nPlease enter the command you want to run on the device(s): "
        command = raw_input("> ")
	COMMANDS = []
	COMMANDS.append(command)
elif cmdSource == 'L' or cmdSource == 'l':
        print "\nPlease enter the filename of the command List (e.g. /home/scott/JUNOSCMDS): ",
        cmdFile = raw_input("> ")
        COMMANDS = open(cmdFile, 'r')
else:
        print "\t ERROR: S and L are the only valid responses for this prompt"

# Lets grab the SSH credentials right from the start
print "\n\nPlease enter your username: :",
username = raw_input("> ")

print "\nPlease enter your password: :",
password = get_password()

ssh_newkey = 'Are you sure you want to continue connecting'

prompt = username + '@' + '.*>'
print "PROMPT IS: ", prompt

for host in hosts:
	host = host.replace("\n", '')
	mytime = time.strftime("%m%d%y%H%M%S")
	rewind(COMMANDS)
	fout = file(host + '_' + mytime + '.txt','w')

	ssh = pexpect.spawn ("ssh " + username + "@" + host)
	bufsize=-1

	i=ssh.expect([ssh_newkey,'.*assword:.*',pexpect.EOF,pexpect.TIMEOUT],5)
	if i==0:
		print "Accepting Key"
		ssh.sendline('yes')
		i=ssh.expect([ssh_newkey,'.*assword:.*',pexpect.EOF,pexpect.TIMEOUT],5)	
	if i==1:
		#print "\npassword sent\n"
		ssh.sendline(password)
	elif i==2:
		#print "\nhmmmm - need to check this..\n "
		pass
	elif i==3:
		print "\ntimeout has occured\n"
		pass


	# NOTE: For CRON jobs you don't need to see the output on the screen as you are running it
	#       To stop the screen output comment out the ssh.logfile_read = sys.stdout line

	#This should be the standard start
	ssh.stdout.flush()
	ssh.expect(prompt)
	ssh.sendline("\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 2 )

	for cmds in COMMANDS:
		ssh.expect(prompt)
		ssh.sendline(cmds)
		ssh.logfile_read = sys.stdout
		ssh.logfile = fout
		time.sleep( 7 )
	
	#This should be the standard start
	ssh.stdout.flush()
	ssh.expect(prompt)
	ssh.sendline("exit\n")

	ssh.close()
	#ssh.terminate()
	#print "\nfinished with this device lets move on...\n"


sys.exit()
