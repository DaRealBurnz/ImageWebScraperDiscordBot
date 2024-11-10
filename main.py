# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
from discord.ext import tasks
import os
import requests
from bs4 import BeautifulSoup
from replit import db

client = discord.Client()
ignoreLst = ['https://www.bigwatermelon.com.au/wp-content/uploads/2021/12/check-back-later-for-promoted-specials.png', 
             'https://www.bigwatermelon.com.au/wp-content/uploads/2022/05/Retail-Trading-Hours-1.jpg',
             'https://www.bigwatermelon.com.au/wp-content/uploads/2023/04/Trading-Hours.png']

def targetClass(cssClass):
    #CSS Class of img starts with 'wp-image'
    return cssClass is not None and cssClass.startswith('wp-image')

async def uploadImg(imgLink):
  guild = client.get_guild(487606526098538497)
  chnl = guild.get_channel(918504914576113715)
  await chnl.send(imgLink)

html = requests.get('https://www.bigwatermelon.com.au/dailyspecials/')
soup = BeautifulSoup(html.text, 'html.parser')

if not db.prefix("img"):
  db["img"] = ""

@tasks.loop(hours=1)
async def checkImgUpdate():
  imgs = soup.find_all('img', class_=targetClass)
  imgLink = ""
  for img in imgs:
    if img['src'] in ignoreLst:
      imgLink = db['img']
      break
    imgLink = imgLink + img['src'] + "\n"
  if imgLink != db['img']:
    await uploadImg(imgLink)
    db["img"] = imgLink

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkImgUpdate.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$force'):
        await uploadImg(db["img"])

try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e