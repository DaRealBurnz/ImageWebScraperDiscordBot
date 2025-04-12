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

# Post image to given guild
async def postImage(imgLink: str, guild: discord.Guild):
    guildInfo = loadGuildInfo()
    g = guildInfo[str(guild.id)]
    chnl = guild.get_channel(g["channel"])
    await chnl.send(imgLink)
    g["last_img"] = imgLink
    saveGuildInfo(guildInfo)


# Return the latest image
def checkImgUpdate() -> str:
    print(f"Checking for an update at {config['url']} using CSS selector {config['selector']}")
    html = requests.get(config["url"])
    soup = BeautifulSoup(html.text, "html.parser")
    imgs = soup.select(config["selector"])
    imgLink = ""
    for img in imgs:
        if img["src"] not in ignoreLst:
            imgLink = imgLink + img["src"] + "\n"
    return imgLink


# Post images in guilds that don't have the new image
@tasks.loop(hours=1)
async def updateGuilds() -> list:
    guildInfo = loadGuildInfo()
    updatedGuilds = []
    imgLink = checkImgUpdate()
    if imgLink != "":
        for guild in client.guilds:
            if str(guild.id) in guildInfo.keys():
                g = guildInfo[str(guild.id)]
                if imgLink != g["last_img"]:
                    await postImage(imgLink, guild)
                    updatedGuilds.append(str(guild.id))
    return updatedGuilds


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
    updateGuilds.restart()


@client.tree.command(
    name="checkupdate",
    description="Force check for an update. This will also reset the time until the next automatic check",
)
async def forceCheck(interaction: discord.Interaction):
    guildInfo = loadGuildInfo()
    if str(interaction.guild_id) in guildInfo.keys() and guildInfo[str(interaction.guild_id)]["channel"]:
        updatedGuilds = await updateGuilds()
        if str(interaction.guild_id) in updatedGuilds:
            await interaction.response.send_message(
                "New images were found and have been posted",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "No new images found",
                ephemeral=True,
            )
        updateGuilds.restart()
    else:
        await interaction.response.send_message(
            "Please set a channel to post updates in first", ephemeral=True
        )


@client.tree.command(
    name="forceupdate",
    description="Force post the latest image, regardless if it was posted already",
)
async def forcePost(interaction: discord.Interaction):
    guildInfo = loadGuildInfo()
    if str(interaction.guild_id) in guildInfo.keys() and guildInfo[str(interaction.guild_id)]["channel"]:
        await interaction.response.send_message(
            "Posting the latest image...", ephemeral=True
        )
        updatedGuilds = await updateGuilds()
        if str(interaction.guild_id) not in updatedGuilds:
            imgLink = checkImgUpdate()
            await postImage(imgLink, interaction.guild)
        updateGuilds.restart()
    else:
        await interaction.response.send_message(
            "Please set a channel to post updates in first", ephemeral=True
        )


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.tree.sync()
    updateGuilds.start()


@client.event
async def on_guild_join(guild: discord.Guild):
    c = guild.system_channel
    embed = discord.Embed(color=discord.Colour.blue)
    embed.add_field(
        name="Thanks for adding the Big Watermelon bot to your server",
        value="To start using the bot, please use /setchannel to set a channel to post updates",
    )
    await c.send(embed=embed)


@client.event
async def on_guild_remove(guild: discord.Guild):
    guildInfo = loadGuildInfo()
    guildInfo.pop(str(guild.id), None)
    saveGuildInfo(guildInfo)


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
