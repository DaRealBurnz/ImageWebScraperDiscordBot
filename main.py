# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
from discord.ext import tasks
import os
import requests
from bs4 import BeautifulSoup
import yaml
import json
from dotenv import load_dotenv

client = discord.Client(intents=discord.Intents.default())
html = requests.get('https://www.bigwatermelon.com.au/dailyspecials/')
soup = BeautifulSoup(html.text, 'html.parser')
with open('config.yml', 'r') as f:
  config = yaml.safe_load(f)
ignoreLst = config['ignoreList']
load_dotenv()

@tasks.loop(hours=1)
async def checkImgUpdate(guild: discord.Guild):
  print(f'checking img update for guild {guild.id}')
  imgs = soup.select(config['selector'])
  # Load data from guild_info file. If it doesn't exist or the json does not decode, consider it empty
  try:
    with open('guild_info.json', 'r') as f:
      guildInfo = json.load(f)
  except:
    guildInfo = {}
  if str(guild.id) in guildInfo.keys():
    g = guildInfo[str(guild.id)]
    imgLink = ""
    for img in imgs:
      if img['src'] not in ignoreLst:
        imgLink = imgLink + img['src'] + "\n"
    if imgLink and imgLink != g['last_img']:
      chnl = guild.get_channel(g['channel'])
      await chnl.send(imgLink)
      g['last_img'] = imgLink
      with open('guild_info.json', 'w') as f:
        json.dump(guildInfo, f)
  else:
     print(f"cannot find guild info for guild {guild.id}")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkImgUpdate.start(client.get_guild(487606526098538497))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # if message.content.startswith('$force'):
    #     await uploadImg(db["img"])

try:
    client.run(os.getenv("BOT_TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e