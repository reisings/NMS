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
        #print "Please enter your password:"
        os.system("stty -echo")
        local_password = raw_input( username + "'s password> ")
        os.system("stty echo")
        print "\n"

        return local_password

print "Do you want to run this for a (S)ingle IP or a (L)ist of IPs (S/L)?: ",
ipSource = raw_input("> ")

#print "Log file will be the ipAddress.date.txt"

if ipSource == 'S' or ipSource == 's':
        print "Please enter the IP address you want to query (e.g. 192.168.1.1): ",
        ipAddress = raw_input("> ")
	hosts = []
	hosts.append(ipAddress)
elif ipSource == 'L' or ipSource == 'l':
        print "Please enter the filename of the IP List (e.g. /home/scott/IPLIST): ",
        ipList = raw_input("> ")
	addresses = open(ipList, 'r')
	hosts = addresses.readlines()
else:
        print "\t ERROR: S and L are the only valid responses for this prompt"


# Lets grab the SSH credentials right from the start
print "Please enter your username: :",
username = raw_input("> ")

print "Please enter your password: :",
password = get_password()

ssh_newkey = 'Are you sure you want to continue connecting'

prompt = username + '@' + '.*>'
print "PROMPT IS: ", prompt

for host in hosts:
	host = host.replace("\n", '')
	fout = file(host + '_' + mytime + '.txt','w')
	ssh = pexpect.spawn ("ssh " + username + "@" + host)
	buffer=2048

	check=ssh.expect([ssh_newkey,'.*assword:.*',pexpect.EOF,pexpect.TIMEOUT],5)
	if check==0:
		print "Accept Key"
		ssh.sendline('yes')
		i=ssh.expect([ssh_newkey,'.*assword:.*',pexpect.EOF,pexpect.TIMEOUT],5)	
	if check==1:
		print "expect gave your password"
		ssh.sendline(password)
	elif check==2:
		print "hmmmm - need to check this.. "
		pass
	elif check==3:
		print "connection timed out"
		pass

	print host
	time.sleep( 1 )

	# NOTE: For CRON jobs you don't need to see the output on the screen as you are running it
	#       To stop the screen output comment out the ssh.logfile_read = sys.stdout line

	#This should be the standard start
	ssh.expect(prompt)
	ssh.sendline("\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 1 )
	#

	#version
	ssh.expect(prompt)
	ssh.sendline("show version | no-more\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 1 )
	#

	#configuration
	ssh.expect(prompt)
	ssh.sendline("show configuration | display set | no-more\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 1 )
	#

	#interfaces
	ssh.expect(prompt)
	ssh.sendline("show interfaces terse | no-more\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 2 )
	#

	#interfaces
	ssh.expect(prompt)
	ssh.sendline("show chassis routing-engine | no-more\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	time.sleep( 2 )
	#

	#we always want to exit nicely (is it nice or nicely?)
	ssh.expect(prompt)
	ssh.sendline("exit\n")
	ssh.logfile_read = sys.stdout
	ssh.logfile = fout
	ssh.terminate()
	#
	
	print "\nfinished with this device lets move on...\n"

sys.exit()
