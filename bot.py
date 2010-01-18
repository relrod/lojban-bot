#!/usr/bin/env python
from BeautifulSoup import BeautifulStoneSoup as BSS
import socket, select, re, ConfigParser
from string import split

print "[*] bevri lojban datni // loading lojban data"
soup = BSS(open("realdb.xml").read())


lojban = re.compile("!! ?(.+)")
slist = []
cp = ConfigParser.ConfigParser()
cp.readfp(open("config.ini"))
for section in cp.sections():
   # So long as section is *not* 'general':
   if section != "global":
      # .. connect to it.
      con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      con.connect((cp.get(section,"server"), int(cp.get(section,"port"))))
      con.send("USER " + (cp.get(section,"nickname") + " ")*4 + "\r\n")
      con.send("NICK " + cp.get(section, "nickname") + "\r\n")
      for channel in split(cp.get(section, "channels"), " "):
         con.send("JOIN " + channel + "\r\n")
      slist.append(con)


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
   
   try:
      if args[0] == "PING":
         send("PONG :" + args[1], which)
         return
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




