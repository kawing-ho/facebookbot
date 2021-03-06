#!/usr/bin/python3

import requests, json, random, sys, urllib, os, re
from datetime import datetime as dt

'''
  23rd November 2017 Ka Wing Ho (finished 7th Dec coz I'm lazy)
  All communications to Facebook done using Page Access Token & Facebook Graph API

  [Refactored for Python3 on 29th Jan 2019]
'''

#------REMEMBER TO REDACT IT LATER-------
token = ""
#----------------------------------------
# Debug : https://stackoverflow.com/a/28418469

base = "https://graph.facebook.com/v2.11/"
meBase = "https://graph.facebook.com/v2.11/me/feed"
path = os.path.dirname(os.path.abspath(__file__))   #cron cant use relative pathing

# Dictionary of news pages (expand if necessary)
source = {
          110032161104:"Daily Telegraph",
          5550296508:"CNN",
          228735667216:"BBC",
          5281959998:"New York Times",
          10513336322:"The Guardian",
          6250307292:"The Washington Post",
          15704546335:"Fox News",
          18468761129:"HuffPost",

          155869377766434:"NBC",
          47298465905:"MalaysiaKini",
          129011692114:"The Straits Times Singapore",
          11450527254:"The Star Online",

          104598631263:"The Sydney Morning Herald"
         }

def checkHistory(id):
   with open(os.path.join(path,"history.txt"),'r') as f: history = f.readlines()
   history = [ x.rstrip() for x in history ]
   return 0 if(id in history) else 1

def alterMessage(message):
   success = 0

   # =====find/replace names=====
   with open(os.path.join(path,"names.txt"),'r') as f:
      names = f.readlines()
   names = [x.rstrip() for x in names]

   matches = re.findall("(?: *[A-Z][a-z]+ ){2,3}", message)
   for n in matches:
      success = 1
      if('the' in n or 'The' in n): continue
      n = n.lstrip().rstrip()
      randomName = random.choice(names)     
      message = message.replace(n,randomName)

   # =====find/replace special=====
   with open(os.path.join(path,"special.txt"),'r') as f:
      special = f.readlines()
   special = [x.rstrip() for x in special]
   matches = re.findall("[tT]he (?: *[A-Zo][a-z]+ *)+",message)
   for s in matches:
      success = 1
      s = s.lstrip().rstrip()
      s = re.sub("^ *[tT]he *",'',s)
      randomSpecial = random.choice(special)
      message = message.replace(s,randomSpecial)
   

   # =====find/replace quotes/sentences=====
   with open(os.path.join(path,"spoken.txt"),'r') as f:
      spoken = f.readlines()
   spoken = [x.rstrip() for x in spoken]
   
   quotes = re.findall("\"[^\"]+\"",message)
   for q in quotes:
      success = 1
      randomQuote = random.choice(spoken)
      message = message.replace(q,"\""+randomQuote+"\"")


   # =====random substitution if others were unsuccessful=====
   if(success == 0):
      
      with open(os.path.join(path,"random.txt"),'r') as f:
         randomList = f.readlines()
      randomList = [x.rstrip() for x in randomList]
      randomWord = random.choice(randomList)

      # split message by space/punctutation
      words = re.findall(r"[\w']+|[^\w\s]",message, re.UNICODE)

      # find a random word to replace
      while(1):
         target = random.choice(words)
         if(re.match("^[a-zA-Z]+$",target)): 
            break

      # reconstruct message
      message = re.sub(r'\b'+target+r'\b',randomWord,message)

      # 2nd substitution for longer messages
      if(len(words) > 40):
         randomWord = random.choice(randomList)
         while(1):
            target = random.choice(words)
            if(re.match("^[a-zA-Z]+$",target)): 
               break

         # reconstruct message
         message = re.sub(r'\b'+target+r'\b',randomWord,message)
      
   return message

while(1):
   # Pick a random news source
   chosen = random.choice(list(source.keys()))

   # Get the most recent post (id and message)
   getPost = base + str(chosen) + "/feed?limit=5" + "&access_token=" + token
   try:
      r = None
      r = requests.get(getPost)
   except Exception as e: print(str(e))
   if(r is None or r.status_code != 200): sys.exit("Error in retrieving seed post\n"+r.text)
   else:
      response = json.loads(r.content)
      data = response["data"][random.randint(0,4)]  # pick random post out of top 5
      postID = data["id"]
      if(checkHistory(postID) and 'message' in data.keys()):

         # comment this for debugging 
         with open(os.path.join(path,"history.txt"),'a') as f: f.write(postID+"\n")

         # replace quotes so that we can find special strings to replace on
         postMessage = data["message"]
         postMessage = postMessage.replace(u'\u201c','\"')
         postMessage = postMessage.replace(u'\u201d','\"')
         postMessage = postMessage.replace(u'\u2019','\'')

         #postMessage = postMessage.encode('utf-8')  #crucial step to avoid unicode issues
         break

sourceURL = "https://facebook.com/"+str(postID)
sourceString = "Source [{}]:\n{}".format(source[chosen], sourceURL)
logtime = str(dt.now().strftime("%A %I:%M %p (%d/%m)")) 
print("========================== {} ===========================".format(logtime))
print(sourceString,"\n")
print("Original Message:\n{}".format(postMessage))
alter = alterMessage(postMessage)   # alter the message
alter += "\n\n\n"
alter += sourceString               # add in source string
print("``````````````````````````````````````````````````````````````````````````````")
print("New Message:\n{}".format(alter))

payload = meBase + "?message=" + urllib.parse.quote(alter) + "&access_token=" + token

# comment out this part for debugging
#==================================================================================
response = requests.post(payload)
if response.status_code != 200: print("Posting failed %d") % response.status_code
#==================================================================================
