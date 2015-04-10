#Code taken from http://www.pythonforbeginners.com/code-snippets-source-code/commandlinefu-with-python/,
#with some modifications

import urllib2
import base64           #<<<<<<<<LINE 4>>>>>>>>
import json 
import os               
import sys              #<<<<<<<LINE 5>>>>>>>>
import re

def Banner(text):
    print("=" * 70)
    print(text)
    print("=" * 70)
    sys.stdout.flush()                  #<<<<<<<LINE 8>>>>>>>>

#sorts votes for all time               #<<<<<<<<LINE 1>>>>>>>>
def sortByVotes():
    Banner('Sort By Votes')
    url = "http://www.commandlinefu.com/commands/browse/sort-by-votes/json"
    request = urllib2.Request(url)
    response = json.load(urllib2.urlopen(request))
    #print json.dumps(response,indent=2)
    for c in response:
        print("-" * 60)
        print(c['command'])

def sortByVotesToday():
    Banner('Printing All commands the last day (Sort By Votes) ')
    url = "http://www.commandlinefu.com/commands/browse/last-day/sort-by-votes/json"
    request = urllib2.Request(url)
    response = json.load(urllib2.urlopen(request))
    for c in response:
        print("-" * 60)
        print(c['command'])

def sortByVotesWeek():
    Banner('Printing All commands the last week (Sort By Votes) ')
    url = "http://www.commandlinefu.com/commands/browse/last-week/sort-by-votes/json"
    request = urllib2.Request(url)
    response = json.load(urllib2.urlopen(request))
    for c in response:
        print("-" * 60)
        print(c['command'])

def sortByVotesMonth():
    Banner('Printing: All commands from the last months (Sorted By Votes) ')
    url = "http://www.commandlinefu.com/commands/browse/last-month/sort-by-votes/json"
    request = urllib2.Request(url)
    response = json.load(urllib2.urlopen(request))
    for c in response:
        print("-" * 60)
        print(c['command'])

def sortByMatch():
    #import Base64
    Banner("Sort By Match")
    match = input("Please enter a search command: ")
    bestmatch = re.compile(r' ')                        #<<<<<<<LINE 6>>>>>>>>
    search = bestmatch.sub('+', match)                  #<<<<<<<LINE 7>>>>>>>>
    b64_encoded = base64.b64encode(search)              #<<<<<<<<LINE 3>>>>>>>>
    url = "http://www.commandlinefu.com/commands/matching/" + search + "/" + b64_encoded + "/json"
    request = urllib2.Request(url)
    response = json.load(urllib2.urlopen(request))
    for c in response:
        print("-" * 60)
        print(c['command'])

os.system("clear")                  
print("-" * 80)
print("Command Line Search Tool")
print("-" * 80)

print('1. Sort By Votes (All Time)')             #<<<<<<<<LINE 2>>>>>>>>
print('2. Sort By Votes (Today)')
print('3. Sort by Votes (Week)')
print('4. Sort by Votes (Month)')
print('5. Search for a command\n')
print('Press enter to quit')

while True:
  answer = input("What would you like to do?")

 if answer == "":
    sys.exit()
  
  elif answer == "1":
   sortByVotes()
 
  elif answer == "2":
   print(sortByVotesToday())
  
  elif answer == "3":
   print(sortByVotesWeek())
 
  elif answer == "4":
   print(sortByVotesMonth())
  
  elif answer == "5":
   print(sortByMatch())
 
  else:
   print("Not a valid choice")