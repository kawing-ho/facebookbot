#!/usr/bin/python2

#Helper script to cleanup / delete any test posts run as bot 

import requests, json, random, sys
#------REMEMBER TO REDACT IT LATER-------
token = ""
#----------------------------------------

myBase = "https://graph.facebook.com/v2.11/me/feed"
removal = []

#Get list of all postIDs
getPosts = myBase + "?access_token=" + token
r = requests.get(getPosts)
if(r.status_code != 200): sys.exit("Error in retrieving seed post")
else:
   response = json.loads(r.content)
   for post in response["data"]:
      #print post["id"]
      removal.append(post["id"])


for post in removal:
   payload = "https://graph.facebook.com/v2.11/" + str(post) + "?access_token=" + token
   print "removing",payload
   reply = requests.delete(payload)
   print "Delete successful" if reply.status_code == 200 else "Delete failed"


