
__author__ = 'Dexter Shepherd'
__version__ = '0.0.5'
__license__ = 'none'

#for Python version 3 or above
import sys
import os
import re
import time
#import the internet connection library
try:
       import httplib
except:
       import http.client as httplib

#data handling library
import xml.etree.ElementTree as ET
#serial communication library
import serial
import serial.tools.list_ports as prtlst
#speech recognition lib
import speech_recognition as sr
#global variables
global rec
global m
global system_pathway
system_pathway = "/home/pi/Documents/applications/AI/"

#initialize microphone
def audioCheck():
    #variables to listen to audio with
    rec = sr.Recognizer()
    #Typlcal sample rates are 44.1 kHz (CD), 48 kHz, 88.2 kHz, or 96 kHz.
    m = sr.Microphone(device_index = 1, sample_rate = 44100, chunk_size = 512)

audioCheck()
def find_usb(string,media):   #find the USB path to my code
    #this function is purely to make the developers life easier
    breaker = 0
    subfolders = [f.path for f in os.scandir(string) if f.is_dir() ]#find all the files
    for i in range(len(subfolders)):
        if media in str(subfolders[i]):    #till it finds my memory stick
            string = subfolders[i]/speech

            breaker = 1
    if breaker == 1:
        return string
    else:
        #print(string)
        return find_usb(subfolders[0],media)
def update():
    #update the system to the newest code
    media = input("Name of drive route: ")
    #usbpath = find_usb("/media",media)
    media = "/media/pi/DEXTER/Python coursework/"
    choice = input("Write in or out? ")
    if choice == "in":
        f = open(media+"main.py",'r')
        r = f.read()
        f.close()
        out("Updating...")
        current = open(system_pathway+"main.py",'w')
        current.write(r)
        current.close()
    else:
        current = open(system_pathway+"main.py",'r')
        r=current.read()
        current.close()
        f = open(media+"main.py",'w')
        f.write(r)
        f.close()
#system_pathway = "sudo python3 /home/pi/Documents/applications/AI/main.py"
def displayEye():
    #the display of the eye
    f = open(system_pathway+"eye.txt",'r')
    r = f.read()
    f.close()
    print(r)    #output on screen the eye in file
def callback(recognizer, audio):
    #turn the audio into speech
    global voiceReply
    voiceReply = ""
    try:
        voiceReply = (rec.recognize_google(audio))
        print("you said "+str(voiceReply))
    except sr.UnknownValueError:    #unkown reply
        out("Could not understand")
    except sr.RequestError as e:
        out("error: {0}".format(e))
    except KeyError:
        out("I don't understand what you are saying")   #no reply
    except ValueError:
        out("Sorry, I didn't get that") #no reply
    except LookupError:
        out("sorry, I didn't get that")

def getVoice():
    #get a voice input
    global voiceReply
    voiceReply = ""
    connection = internet()
    if connection == True:  #connection found
        with m as source:
            rec.adjust_for_ambient_noise(source)
        
        stop_listening = rec.listen_in_background(m,callback)#listen for audio in background
        print("say something")
        while voiceReply == "":
            time.sleep(1)#listen for 1 seconds
        stop_listening()    #stop listening
        
        
    else:   #no connection
        out("There is an error conencting to the internet")
    return voiceReply.lower()   #return voice
def PutIn(string):  #use fundtion so method of output can be changed for hardware
    out(string)#method of output
    string = ""
    while(string == ""):
        try:
            string = input()
        except EOFError:    #exlude errors from raspberry pi OS
            string = ""
    if string == "/speech":
        string = getVoice() #get voice input
    
    return string  #return input
def validate(): #get a valid speech input from the user
    string = ""
    while string == "": #loop till something
        string = PutIn("Please tell me") #get voice or text input
        if string == None:
            string = ""
        if '[' in string:
            string = ""
        if "/speech" in string and string != "/speech":
            out("Invalid ")
            string = ""
    return string
def internet():
       conn = httplib.HTTPConnection("www.google.com", timeout=5)
       try:
           conn.request("HEAD", "/")
           conn.close()
           return True
       except:
           conn.close()
           return False
def out(string):    #use fundtion so method of output can be changed for hardware
    #locate the arduino port
    pts= prtlst.comports()
    string1 = pts[0]
    #print(string1[0])
    hardware_port = string1[0]
    for pt in pts:
        #print(pt)
        if 'USB' in pt[1]: #check 'USB' string in device description
            #print(pt)
            COMs.append(pt[0])
    #output to com
    #print(string)#method of output  
    ser = serial.Serial(hardware_port, 9600)
    a = 0
    #print("opening :"+hardware_port)
    if string == None:
        string = ""
    string+= '/'  #tells the board to output
    
    while a < len(string):  #send message through
                ser.write(string[a].encode('ascii'))
                a += 1
    ser.close() #close ports
    
def search(sentence):   #search through data to find if in
    print("searching '"+sentence+"'")
    trigger=find_term(sentence,"t")  #search string for trigger word in database
    if trigger!="#@false":
        subject = find_term(sentence,"s") #search message for subject
        if subject!="#@false":
            command = find_term(sentence,"c") #search message for command
            if command!="#@false":
                #all words needed found
                print(trigger)
                print(subject)
                print(command)
                AI = find(trigger,subject,command)  #search database
                out(AI)
                
            else:   #no command word found
                out("No command found")
        else:   #no subject found
            out("No subject found")
    else:   #no trigger found
        out("No trigger found")

def find_term(message,Stype):
        #find the word and its type
        file = open(system_pathway+Stype+".txt",'r')   #search vocab file
        r = file.read() 
        file.close()
        x = -1
        array= []
        string =""
        for i in range(len(r)):
            if r[i] == ',':  #break up each phrase or word
                string = string.replace("\n","")
                string = string.replace(",","")
                array.append(string)
                string = ""
                
            string += r[i]
        #print(array)
        for i in range(len(array)):
            if array[i] in message:  #if word in file
                #x can be added to and a list of subjects is compiled
                #for future versions
                x = i
                break
        if x >= 0:
            return array[x] #return the keyword
        else:
            return "#@false" #the command to say nothing found
        
def add_command():  #add a command word to the data
    print("add command")
    value=PutIn("Input your command word")
    file = open(system_pathway +"c.txt",'a')
    file.write(value)
    file.write(',')
    file.close()
def add_subject():  #add a subject to the data
    print("add subject")
    value=PutIn("Input your subject word")
    file = open(system_pathway +"s.txt",'a')
    file.write(value)
    file.write(',')
    file.close()
    
def add_trigger():    #add a trigger word to the data
    print("add vocabulary")
    value=PutIn("Input your trigger word")
    file = open(system_pathway +"t.txt",'a')
    file.write(value)
    file.write(',')
    file.close()
def find(trigger, subject, command):
    tree = ET.parse(system_pathway+'knowledge.xml')
    root = tree.getroot()
    output = "none"
    num = 1
    for i in root.findall('phrase'): #finds all the things to do with this
        trig = i.find('trigger').text
        sub = i.find('subject').text
        com = i.find('command').text
        if trig == trigger and sub == subject and com == command:   #locates data
            output = i.find('output').text  #find the saved output
        #print(trig+sub+com)
        num += 1
    if output == "none":    #nothing found in data
        out("Nothing in my data... Please tell me, how, you, would like, me to respond")
        say = validate() #get a valid user input
        file = open(system_pathway+"knowledge.xml",'r')    #open database
        r = file.read() #read data
        file.close()
        r = r.replace("</data>","") #remove end
        r = r + '\t<phrase name="command'+str(num)+'">\n'
        r = r + '\t<trigger>'+trigger+'</trigger>\n'
        r = r + '\t<subject>'+subject+'</subject>\n'
        r = r + '\t<command>'+command+'</command>\n'
        r = r + '\t<output>'+say+'</output>\n'
        r = r + "</phrase>\n"
        r = r + '</data>'
        #write to file in format
        #print(r)
        #time.sleep(4)
        file = open(system_pathway+"knowledge.xml",'w')    #open database
        file.write(r) #write to file
        file.close()
        output = say
    return output

def add_layer():    #add a layer to the data network
    print("adding layer")
    #nothing here
def search_layer(): #search for a layer
    print("adding layer")
    #nothing here
def add_variable(vocab):
    value = PutIn("Input a variable")
    print(value)
    value = value.replace(" ","_")
    file = open(system_pathway +"variables.txt",'a')
    file.write(value)
    file.write(' ')
    file.close()
    words1 = Umessage.split()   #send users message to a list
    file.close()
    #write to the file
    file = open(system_pathway +vocab+'/' +"start.txt",'w')
    file.write(stri)
    file.write("*")
    file.write(vocab+".txt")
    file.write("/")
    file.close()

exit = 0

while(exit ==0):
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    displayEye()    #output eye to the user
    print("User: ")
    user_message = PutIn("") #get userinput
    if user_message == "/add trigger":  #add trigger word command
        add_trigger()
    elif user_message == "/add subject":    #add subject word command
        add_subject()
    elif user_message == "/add command":    #add command word command
        add_command()
    elif user_message == "/add layer":  #add layer command
        add_layer()
    elif user_message == "/add variable":   #add variable command
        add_variable()
    elif user_message == "/exit":   #leave program
        exit = 1
    elif user_message == "":    #no data
        print("")
    elif user_message == "/update":
        update()
    else:
        search(user_message)
    
sys.exit()  #stop the program