___Version___="0.0.6"
___Author___ ="Dexter Shepherd"
from SHEP import AI
import time
#import the internet connection libraries
try:
       import httplib
except:
       import http.client as httplib
from urllib.request import urlopen
from wifi import Cell, Scheme
#clear up type errors
from subprocess import Popen, STDOUT, PIPE
from subprocess import *
import subprocess
import os
import re
#eye
import time
import colorsys
from pixels import Pixels #found in folder
#import serial.tools.list_ports as prtlst
#speech recognition lib
import speech_recognition as sr
pixels = Pixels()

myBot = AI("SHEP", "user","knowledge.xml") #SHEP is called in
system_pathway = "/home/pi/AI/Python_coursework/"
myBot.setpath(system_pathway)

def audioCheck():
       global rec
       global m
       try:
              #variables to listen to audio with
              rec = sr.Recognizer() 
              #Typlcal sample rates are 44.1 kHz (CD), 48 kHz, 88.2 kHz, or 96 kHz.
              m = sr.Microphone()
       except:
              OUTPUT("Problem connecting to microphone")
              error_pixels()
def internet():
       conn = httplib.HTTPConnection("www.google.com", timeout=5) #attempt connection
       try:
           conn.request("HEAD", "/")
           conn.close()
           return True #show there is a connection
       except:
           conn.close()
           error_pixels()
           return False #show there is not a connection
def error_pixels():
       #the pixels desplayed for an error
       pixels.off()
       pixels.wakeup()
       time.sleep(0.2)

           
def update():
       try:
              file = open(system_pathway+"test.txt","w")
              for line in urlopen("https://shepai.github.io/code/main.py"):
                     #decode the file and write it to the Pi
                     s = line.decode('utf-8')
                     #print(s)
                     file.write(s)
              file.close()
              file = open(system_pathway+"eye.txt","w")
              for line in urlopen("https://shepai.github.io/code/eye.txt"):
                     #decode the file and write it to the Pi
                     s = line.decode('utf-8')
                     print(s)
                     file.write(s)
              file.close()
              file = open(system_pathway+"test.txt","r")
              r = file.read()
              file.close()
              current = open(system_pathway+"main.py","r")
              r2 = current.read()
              current.close()
              if(r == r2):#same
                     print("No update needed")
              else:
                     #update
                     OUTPUT("updating...")
                     current = open(system_pathway+"main.py","w")
                     current.write(r)
                     current.close()
                     os.system("sudo reboot")    #restart with new
       except:
              print("Error finding update")
              
def OUTPUT(string):#output method
    #locate the arduino port
    try:
       #output using onboard TTS
       pixels.speak() #coulourful look
       string = string.replace("'","") #prevent an apostriphe messing it up.
       os.system("espeak '"+string+"' 2>/dev/null")
       
    except:
           #no connection
           print(string)
           error_pixels()
           
def getVoice():#input method
    
    try:
           
           voiceReply = ""
           connection = internet()
           if connection == True:  #connection found
               connection_errors = 0 #show there is a strong connection
               #r.pause_threshold = 0.6
               
               print("setting...")
               rec.dynamic_energy_threshold = False #set ackground noise to silence
               t0 = 0 #set the timer
               with m as source:    #listen audio
                  audio = rec.adjust_for_ambient_noise(source) #adjust audio
                  print ("Speak Now")
                  t0 = time.time() #start a timer to prevent the search going on too long
                  pixels.listen()    #output eye to the user
                  audio = rec.listen(source,timeout=5)                   # listen for the first phrase and extract it into audio data
               t1 = time.time() #take a second reading of the time
               total = t1-t0 #work out how long it took
               pixels.off() #stop the LEDs
               print(">>")
               timer = 0
               if total < 15: #it will take too long to convert otherwise
                      try:
                             voiceReply = (rec.recognize_google(audio,language = "en-GB"))
                             print("you said "+str(voiceReply))
                             if "could not understand" in voiceReply.lower(): #prevent annoying output
                                    voiceReply = ""
                      except sr.UnknownValueError:    #unkown reply
                             #OUTPUT("Could not understand")
                             voiceReply = ""
                      except sr.RequestError as e:
                             print("error: {0}".format(e))
                             #OUTPUT("error understanding")
                             voiceReply = ""
                      except KeyError:
                             #OUTPUT("I do not understand what you are saying")   #no reply
                             #pixels.think()
                             voiceReply = ""
                      except ValueError:
                             #no reply
                             #OUTPUT("Sorry, I did not get that")
                             voiceReply = ""
                      except LookupError:
                             #no reply
                             #OUTPUT("sorry, I did not get that")
                             voiceReply = ""
                             
                      
               else:
                      print("Took too long to respond...")
                      
           else:   #no connection
               connection_errors += 1
               if connection_errors == 4:
                      OUTPUT("There is an error connecting to the internet")
                      #voiceReply = input(": ")   #alternate method
                      connection_errors = 0 #reset check
    except:
           #no microphone or internet error
           audioCheck()
           #OUTPUT("There was an error connecting to microphone")
           error_pixels()
    return voiceReply #return voice

def INPUT(string):
    OUTPUT(string)#method of output
    string = ""
    string = getVoice() #get voice input
    if "robot" in string and "cancel" not in string:
           print("----------------------------------")
           file=open(system_pathway+"action/input.txt",'w')
           file.write(string)
           file.close()
           if "robot keyboard" in string:
                     string = input("Please type: ")#type mode
           else:
                     string = (string.replace("robot ","",1))#getrid of call sign
           pixels.think()   #show the user it is thinking
           
           if "robot" == string:
                  string = ""
           words = string.split()
           title=""
           
           ######################################################
           #if a name of a place is mentioned it is checked and added to data
           middlewords=""
           for i in range(len(words)):#find all the capital letters
                  if (words[i])[0].isupper():
                         title+=(words[i])+middlewords+" "#gather subject
                         middlewords=""
                  elif title != "":#get words between words
                         middlewords+=words[i]+" "
           if myBot.find_term(title.lower(),"subject") == "#@false" and title != None and title != "":#the word is not a subject
                  if len(title.lower()[:-1]) >= 2:
                         myBot.addWord(title.lower()[:-1],"subject")
                         print("Adding new word",title.lower()[:-1])
           #######################################################
           return string.lower()   #return voice  #return input
    else:
           print("---nothing")
           return "" #nothing said to robot
def pickPhrase(phrase):
    OUTPUT("Your sentence is "+phrase)
    print("---")
    phrase = phrase.split() #make it a list
    word = "" #the word to save
    i = 0
    while i <(len(phrase)): #loop round all the words
           currentSearch = phrase[i]
           print(currentSearch)
           OUTPUT("Is. "+currentSearch+". Your word, or in your word") #ask if that is the users word
           choice = getVoice() #does not require "robot"
           if "yes" in choice or "yep" in choice: #different answers
                  OUTPUT("Great! Adding it")
                  word += phrase[i] +" " #get the word to save, and lots of them if it is a big sentence         
           elif "no" in choice or "nope" in choice: #different answers
                  print("No word")
                  OUTPUT("Okay, next")
           elif "cancel" in choice or "exit" in choice: #user does not want to add
                  OUTPUT("Exiting.")
                  word = ""
                  break
           elif "finished" in choice or "finish" in choice:
                  OUTPUT("Saving your word")
                  break
           else:
                  OUTPUT("Sorry, I did not get that")
                  i=i-1 #go back to prior position
           i=i+1 #increase iteration
           time.sleep(1)
    #add word to correct file
    if word != "":
        return word
    else:
        OUTPUT("aborted")
        return "ABORTED"

def add(to_add):
    #get the type to add
    if to_add == "action" or to_add == "an action":
        valid=">failed to add"
        add=True
        while valid == ">failed to add":
            userInput = INPUT("What is the file name")
            if "cancel" == userInput or "exit" == userInput:
                #allow the user to change their mind and not add
                valid = ">added"
                OUTPUT("I shall not add an action")
            else:
                while (userInput[len(userInput)-1] == " "):
                       userInput = userInput[:-1]
                valid = myBot.addAction(userInput)#check the filename and add
                to_add = valid
                
                                    
    
    return to_add
def wifi():
#wifi connection function
       batcmd="nmcli dev wifi"
       result = subprocess.check_output(batcmd,shell = True)
       result = result.decode('utf-8') # needed in python 3
       if result == "":
           print("No network found")
       else:
           print(result)
           
           ls = re.split("\n |  |\t ",result) #clear of waste
           new = []
           for i in range(len(ls)): #sort waste
               if ls[i] != "" and ls[i] != " ":
                   new.append(ls[i])    
           new = new[8:] #sort more waste
           ssids = []
           x = 0
           y = 1
           while x < len(new)-1: #create list of things
               ssids.append(new[x])
               print(str(y)+") "+new[x])
               x += 7
               y += 1
           num = len(ssids)+1
           while num > len(ssids) or num <= 0:
                  try:
                         num = int(input("Which number would you like: "))
                  except:
                         print("Invalid input:")
                  num = num - 1 #equalize it with list numbers
                  if num < 0:
                      num = len(ssids) +1 #loop bigger than the array
           ID = ssids[num]
           passkey = input("Password: ")
           try:
                print("Connecting... ")
                handle = Popen('nmcli device wifi con '+ID+' password '+passkey, shell=True, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
                #sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
                sleep(5) # wait for the password prompt to occur (if there is one, i'm on Linux and sudo will always ask me for a password so i'm just assuming windows isn't retarded).
                print ((handle.stdout.readline().strip()).decode('utf-8'))
                

           except:
                  print (handle.stdout.readline().strip())
                  print("Couldn't connect to the network... ")
def listUSB():
           list = os.popen("lsblk").read()
           print(list)
           list = list.split()
           i=7
           errors=[]
           devices=[]
           pathway=[]
           
           list = os.popen("lsblk").read()
           list = list.split()
           while i < (len(list)):
               
               i+=6
               if i < (len(list)):
                       
                   if "/" not in list[i]: #no pathway so in fact
                       errors.append(list[i-6]) #make list of bad one's
                       
                       
                   else: #pathway
                       devices.append(list[i-6])
                       pathway.append(list[i])
                       i+=1
           #show to user
           print("Bad devices:")
           for i in range(len(errors)-1):
               print(errors[i])
               os.system("sudo mount -t vfat -o rw /dev/"+errors[i]+" /media/usbstick/")
               #create a mount
               if "└─" in errors[i+1]:
                   errors[i+1] = errors[i+1].replace("└─","")
                   os.system("sudo mount -t vfat -o uid=pi,gid=pi /dev/"+errors[i]+" /media/usbstick/")
               
               try:
                   copyFiles("/media/usbstick/AI/actions",system_pathway+"/action")
                   myAI.out("Files copied")
                   copyFiles(system_pathway,pathway[i]+"/AI/data")

               except:
                   print("Cannot be done!")
           print("\nGood devices:")
           for i in range(len(devices)):
               print(devices[i]+"---"+pathway[i])
               try:
                   copyFiles(pathway[i]+"/AI/actions","/home/pi/AI/Python_coursework/action")
                   out("Files copied")
                   copyFiles("/home/pi/AI/Python_coursework/",system_pathway,pathway[i]+"/AI/data")
               except:
                   print("Cannot be done!")

def copyFiles(directory,to):
           # copy subdirectory example
           fromDirectory = directory
           toDirectory = to

           copy_tree(fromDirectory, toDirectory)
def checkInfo():
       #check the users info and type any if not found.
       y=0
       while y <= 4:
              if internet() == False:
                     time.sleep(1) #give time to connect
              y += 1
       while internet() == False: #loop till a network is found
              while internet() == False: #prevent wrong IDs
                     wifi()
                     time.sleep(0.5)
       check = ["name","title","birthday"]
       print("Your name is what I will know you as, and your title is how I will address you. For example: hello, sir. or hello, madam")
       to_output_once = "Your name is what I will know you as, and your title is how I will address you. For example: hello, sir. or hello, madam"
       for i in range(len(check)):
           try: #if file is a thing it will read and be fine
                  file = open(system_pathway+check[i]+".txt","r") 
                  r = file.read()
                  file.close()
                  
                  if r == "":      #there is no data    
                         OUTPUT(to_output_once)
                         to_output_once = ""
                         OUTPUT("Please type your "+check[i])
                         string = "Please type your "+check[i]+": "
                         data = input(string)
                         file = open(system_pathway+check[i]+".txt","w")
                         r = file.write(data)
                         file.close()
           except: #the file is not found and needs to be added
                #print("No file found")
                OUTPUT(to_output_once)
                to_output_once = ""
                string = "Please type your "+check[i]+": "
                data = input(string)
                file = open(system_pathway+check[i]+".txt","w")
                r = file.write(data)
                file.close()
checkInfo()
update()
myBot.update()
exit = False #exit decider
add_mode = True #defines whether the AI should ADD or not
while exit == False:
    User = INPUT("")
    
    if User == "edit": #edit a sentence
        sentence = ""
        to_add = ""
        replace = ""
        while sentence == "": #get a valid input
               sentence = INPUT("Say the sentence that I shall edit ")
        while to_add == "": #get a valid input
               to_add = INPUT("What shall I replace it with? ")
        replace = add(to_add) #get the replacement (action or...)
        toOut= myBot.edit(sentence,replace)
        OUTPUT(toOut)
    elif User == "add action" or User == "and action" or User == "addaction" or User == "add actions" or User == "and actions": #add an action
        listUSB()
        OUTPUT("Copying files!")
    elif User == "exit": #exit the program
        exit=True
    elif User == "":
        r = ""
    elif User != None:
        myBot.addSubject(User) #add words which are leftover
        r = myBot.search(User+" ") #check the AI
        if add_mode == True:
            if r == "No trigger": #add phrases to make word
                OUTPUT("No trigger found")
                phrase = pickPhrase(User)
                if phrase != "ABORTED":
                    myBot.addWord(phrase,"trigger")
                r = ""
            elif r == "No subject": #add phrases to make word
                OUTPUT("No subject found")
                phrase = pickPhrase(User)
                if phrase != "ABORTED":
                    myBot.addWord(phrase,"subject")
                r = ""
            elif r == "No command": #add phrases to make word
                OUTPUT("No command found")
                phrase = pickPhrase(User)
                if phrase != "ABORTED":
                    myBot.addWord(phrase,"command")
                r = ""
            elif r == "/actions/": #an action has just been played.
                print("Action played")
                r = ""
            elif r == "/00/00/00": #no action is fond
                OUTPUT("Learning... a moment please")
                word_to_add = myBot.findWiki(myBot.subject,myBot.command) #check wiki
                to_add = ""
                if word_to_add != "": #if something is found
                        myBot.learn(myBot.trigger,myBot.subject,myBot.command,word_to_add)
                        to_add = word_to_add
                        
                if word_to_add == "":
                    #the wiki is not going to be added
                    
                    while to_add == "":
                           to_add = INPUT("Nothing in my data, What shall I add?")
                    to_add = add(to_add)
                    print(to_add)
                    if to_add != ">action" or to_add != "action" or to_add != "an action":
                        
                        myBot.learn(myBot.trigger,myBot.subject,myBot.command,to_add)
                r = to_add
        
    OUTPUT(r)


