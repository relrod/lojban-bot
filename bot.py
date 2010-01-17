#!/usr/bin/env python
from BeautifulSoup import BeautifulStoneSoup as BSS
import socket, select, re, sys

print "[*] bevri lojban datni // loading lojban data"
soup = BSS(open("realdb.xml").read())

lojban = re.compile("!! ?(.+)")

IRC_NICKNAME = "lojban"
IRC_SERVER = "irc.eighthbit.net"
IRC_CHANNELS = ("#codeblock",)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((IRC_SERVER, 6667))

irca = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irca.connect(("irc.freenode.net", 6667))

slist = [irc, irca]

def send(msg, which):
   if which == 2: # Global
      for server in slist:
         server.send(msg + "\r\n")
   else:
      which.send(msg + "\r\n")
   print "{SENT} " + msg
   return

def msg(user, msg, which):
   send("PRIVMSG " + user + " :" + msg, which)
   return

def processline(line, which):
   parts = line.split(' :',1)
   args = parts[0].split(' ')
   if (len(parts) > 1):
      args.append(parts[1])
   
   if args[0] == "PING":
      send("PONG :" + args[1], which)
      return

   try:
      if args[3] == "!workplox":
         msg(args[2], "no.")
         return
      elif str(re.match(lojban, args[3])) != "None":
         # We have a regex match!!!
         
         m = re.search(lojban, args[3]).groups()

         word = soup.find('nlword', word=m[0])
         response = ""
         try:
            response += "Translation (" + m[0] + "): " + word['valsi']
         except:
            # Try a valsi...
            word = soup.find('valsi', word=m[0])
            try:
               response += "Definition (type: " + str(word['type']) + "): " \
                     + str(word.definition.contents[0])
            except:
               msg(args[2], "No translation or definition could be found.", which)
               return

         try:
            response += "  (sense: " + word['sense'] + ")"
         except:
            response += ""

         msg(args[2], response, which)
         return
            

   except IndexError:
      return

   # When we're done, remember to return.
   return
   

send("USER " + (IRC_NICKNAME + " ")*4, 2)
send("NICK " + IRC_NICKNAME, 2)
for channel in IRC_CHANNELS:
   send("JOIN " + channel, 2)

while True:
   # EXIST
   inputready,outputready,exceptready = select.select(slist,[],[])
   for server in inputready:
      line = server.recv(1024).rstrip()
      if "\r\n" in line:
         linesep = line.split()
         for l in linesep:
            processline(l, server)
         continue
      processline(line, server)




