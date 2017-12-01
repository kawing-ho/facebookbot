#!/usr/bin/python2

import requests, json, random, sys

'''
  1st December 2017 Ka Wing Ho
  All communications to Facebook done using Page Access Token and Facebook Graph API
  Usage/Setup can be found in USAGE.md
'''

#------REMEMBER TO REDACT IT LATER-------
token = ""
#----------------------------------------

base = "https://graph.facebook.com/v2.11/"
meBase = "https://graph.facebook.com/v2.11/me/feed"

#Dictionary of news pages (expand if necessary)
source = {110032161104:"Daily Telegraph",
          5550296508:"CNN",
          228735667216:"BBC",
          5281959998:"New York Times",
          10513336322:"The Guardian",
          6250307292:"The Washington Post"
         }

#Pick a random news source
chosen = random.choice(source.keys())

#Get the most recent post (id and message)
getPost = base + str(chosen) + "/feed?limit=1" + "&access_token=" + token
r = requests.get(getPost)
if(r.status_code != 200): sys.exit("Error in retrieving seed post")
else:
   response = json.loads(r.content)
   data = response["data"][0]
   postID = data["id"]
   postMessage = data["message"]

   sourceURL = "https://facebook.com/"+str(postID)
   print "Media Company:",source[chosen]
   print "Source:",sourceURL
   print "Message:",postMessage




