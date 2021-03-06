#!/usr/bin/python3

import json
import sys
import os
import ntpath
import telebot
from telebot import types
import requests
import time
from lxml import html
import swarfarm
import thread
from flask import Flask
print ('running...')
swarfarm = swarfarm.Swarfarm()

scriptPath = ntpath.dirname(sys.argv[0])

pageUrl = 'http://summonerswar.wikia.com/wiki/'
elements = ['light','dark','fire','water','wind']
print ('running...')
# Run python svResponseBot.py <configfile> voor je eigen configfile ipv config.json
# Token in config_example.json is voor test bot (@sumwarbot)
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as configFile:
        config = json.load(configFile)
    configFile.close()
    bot = telebot.TeleBot(config['token'])
else:
    #prolly running on horoku
    try:
        token = str(os.environ.get('token'))
        bot = telebot.TeleBot(token)
    except Exception as e:
        print ('prolly running local, use config file as sys arg')
        sys.exit()


print ('running...')
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.send_message(message.chat.id,"""
/mon <monname> of /monster <monname> - Monster info
/summon <methode> - Summon methode info
""")

#used for scraping the page
def scrapePage(mon):
    #build the page info and pull data
    page = requests.get(pageUrl + str(mon))
    #structure data into tree
    tree = html.fromstring(page.text)
    #check if we found a no article page;
    noArticleFound = tree.find(".//div[@class='noarticletext']")
    #check what we have found
    if noArticleFound != None:
        return None
    else:
        return tree

#used for finding the element
def rebuildMonElement(monString):
    monString = monString.split('_')
    element = ''
    #check if there is an element given:
    for splittedText in monString:
        #if it's in the list
        if splittedText.lower() in elements:
            element = splittedText.title()
            monString.remove(splittedText)
            continue
    if element != '':
        updatedMon = '_'.join(monString) + '_('+element+')'
        return updatedMon
    else:
        return None

def notFound(message):
    bot.send_message(message.chat.id,'... nothing found. soz!')
    return

def insertMon(message):
    markup = types.ForceReply(selective=True)
    reply = bot.reply_to(message, "voer mon in:", reply_markup=markup)
    bot.register_next_step_handler(reply, monPrepare)
    return

def monPrepare(message):
    message.text = message.text.replace(message.text,"/mon "+message.text)
    monReturn(message)
    return

@bot.message_handler(commands=['summon'])
def summonInfo(message):
    if message.text.strip() == '/summon':
        markup = types.ReplyKeyboardMarkup(selective=True,one_time_keyboard=True,resize_keyboard=True)
        markup.row('Mystical scroll','Crystals')
        markup.row('Fire scroll','Water scroll','Wind scroll')
        markup.row('LightDark Scroll','Legendary scroll','Summon stones')
        markup.row('LightDark pieces','Legendary pieces')
        reply = bot.reply_to(message, "selecteer summon methode of /close mij", reply_markup=markup)
        bot.register_next_step_handler(reply, summonInfo)
    elif message.text == '/close':
        markup = types.ReplyKeyboardRemove(selective=True)
        bot.send_message(message.chat.id,'maybe next time buddy',reply_markup=markup)
    else:
        scrolltype = message.text.replace("/summon ", "")
        markup = types.ReplyKeyboardRemove(selective=True)
        bot.send_message(message.chat.id,swarfarm.getSummonInfo(scrolltype.lower()),reply_markup=markup)


@bot.message_handler(commands=['mon','Mon','MON','monster','Monster'])
def monReturn(message):
    inputtedMon = message.text.split(' ')
    #format the single items in the list
    inputtedMon = [name.title() for name in inputtedMon]
    monString = '_'.join(inputtedMon[1:])

    #check if we have an empty input
    if monString == '':
        insertMon(message)
        return

    #scrape the page
    tree = scrapePage(monString)
    if tree == None:
        #retry with an element (if any)
        monString = rebuildMonElement(monString)
        tree = scrapePage(monString)
        #still found nothing, return a not found
        if tree == None:
            notFound(message)
            return

    #found the correct page
    skillPage = pageUrl + monString +'#skills'+'\n'
    infoList = []
    #build the mon name, based on the header-title
    monTitle = tree.find(".//div[@class='header-column header-title']/h1").text+'\n'
    infoList.extend((monTitle,skillPage))
    #loop trough information and add it to a list
    for foundValues in tree.find(".//div[@id='common_info']/*"):
        infostring = str((foundValues.text_content())).lower()
        if 'type: ' in infostring or 'awakened bonus: ' in infostring:
            infoList.append('\n'+infostring.replace('\n',''))

    returnString = ''.join(infoList)
    bot.send_message(message.chat.id,str(returnString),disable_web_page_preview=1)


@bot.message_handler(commands=['buffs'])
def buffslist(message):
    bot.send_message(message.chat.id,str('http://summonerswar.wikia.com/wiki/Skills#Buffs'),disable_web_page_preview=1)
    return

@bot.message_handler(commands=['debuffs'])
def debufflist(message):
    bot.send_message(message.chat.id,str('http://summonerswar.wikia.com/wiki/Skills#Debuffs'),disable_web_page_preview=1)
    return





def runflask():
    app = Flask(__name__)
    app.run(port=os.environ.get('PORT'), host='0.0.0.0')

def polltoflask():
    while True:
        requests.get("https://swmonbot.herokuapp.com/")
        time.sleep(900)

if not len(sys.argv) > 1:
    thread.start_new_thread(runflask, ())
    thread.start_new_thread(polltoflask, ())

bot.polling()
