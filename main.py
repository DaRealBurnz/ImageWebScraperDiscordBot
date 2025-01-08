# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
from discord.ext import tasks, commands
import os
import requests
from bs4 import BeautifulSoup
import yaml
import json
from dotenv import load_dotenv

client = commands.Bot(command_prefix="!", intents=discord.Intents.default())
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
ignoreLst = config["ignoreList"]
html = requests.get(config["url"])
soup = BeautifulSoup(html.text, "html.parser")
load_dotenv()


# Load data from guild_info file. If it doesn't exist consider it empty
def loadGuildInfo() -> dict:
    try:
        with open("guild_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Save data to guild_info file. Will create if it does not exist
def saveGuildInfo(guildInfo: dict):
    with open("guild_info.json", "w") as f:
        json.dump(guildInfo, f)


# @tasks.loop(hours=1)
async def checkImgUpdate(guild: discord.Guild, force: bool = False) -> bool:
    print(f"checking img update for guild {guild.id}")
    imgs = soup.select(config["selector"])
    guildInfo = loadGuildInfo()
    if str(guild.id) in guildInfo.keys():
        g = guildInfo[str(guild.id)]
        imgLink = ""
        for img in imgs:
            if img["src"] not in ignoreLst:
                imgLink = imgLink + img["src"] + "\n"
        if imgLink and (force or imgLink != g["last_img"]):
            chnl = guild.get_channel(g["channel"])
            await chnl.send(imgLink)
            g["last_img"] = imgLink
            saveGuildInfo(guildInfo)
            return True 
    else:
        print(f"cannot find guild info for guild {guild.id}")
    return False


runningTasks = []


def startTask(guild: discord.Guild):
    # If task is already running, don't do anything
    for task in runningTasks:
        if task.get_task().get_name() == str(guild.id):
            return
        
    # Create new task and add it to the list
    t = tasks.loop(name=str(guild.id),hours=1)(checkImgUpdate)
    runningTasks.append(t)
    t.start(guild)

def restartTask(guild: discord.Guild) -> bool:
    for task in runningTasks:
        if task.get_task().get_name() == str(guild.id):
            task.restart(guild)
            return True
    return False


@client.tree.command(
    name="setchannel", description="Set this channel to receive updates from the bot"
)
async def setChannel(interaction: discord.Interaction):
    guildInfo = loadGuildInfo()
    if str(interaction.guild_id) not in guildInfo.keys():
        guildInfo[str(interaction.guild_id)] = {"last_img": ""}
    guildInfo[str(interaction.guild_id)]["channel"] = interaction.channel_id
    saveGuildInfo(guildInfo)
    await interaction.response.send_message(
        "The bot will post updates to this channel", silent=True
    )
    startTask(interaction.guild)


@client.tree.command(name="checkupdate", description="Force check for an update. This will also reset the time until the next automatic check")
async def forceCheck(interaction: discord.Interaction):
    guildInfo = loadGuildInfo()
    if restartTask(interaction.guild) or (str(interaction.guild_id) in guildInfo.keys() and guildInfo[str(interaction.guild_id)]["channel"]):
        await interaction.response.send_message("Checking for an update. Nothing will be posted if the last post is up to date", ephemeral=True)
        await checkImgUpdate(interaction.guild)
    else:
        await interaction.response.send_message("Please set a channel to post updates in first", ephemeral=True)


@client.tree.command(name="forceupdate", description="Force post the latest image, regardless if it was posted already")
async def forcePost(interaction: discord.Interaction):
    guildInfo = loadGuildInfo()
    if str(interaction.guild_id) in guildInfo.keys() and guildInfo[str(interaction.guild_id)]["channel"]:
        if await checkImgUpdate(interaction.guild, True):
            await interaction.response.send_message("Posting the latest image...", ephemeral=True)
        else:
            await interaction.response.send_message("Unable to find an image, or the latest image is in the ignore list", ephemeral=True)
        restartTask(interaction.guild)
    else:
        await interaction.response.send_message("Please set a channel to post updates in first", ephemeral=True)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.tree.sync()
    guildInfo = loadGuildInfo()
    for guild in guildInfo:
        startTask(client.get_guild(int(guild)))

@client.event
async def on_guild_join(guild: discord.Guild):
    print("this ran")
    c = guild.system_channel
    embed = discord.Embed()
    embed.add_field(name="Thanks for adding the Big Watermelon bot to your server", value="To start using the bot, please use /setchannel to set a channel to post updates")
    await c.send(embed=embed)


try:
    client.run(os.getenv("BOT_TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
