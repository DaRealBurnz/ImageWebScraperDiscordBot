# Web Scraper Discord Bot
This is a Discord bot that scrapes images from a given website and CSS selector. The website is checked every hour (on a per guild basis) and if a new image is found it will post the link to the photo(s) to the designated channel.

## Getting Started
To get set up, you'll need to follow [these bot account setup instructions](https://discordpy.readthedocs.io/en/stable/discord.html), and then copy the token for your bot and add it to an .env file with the key `BOT_TOKEN` (see example.env)

After that, copy the config_example.yml file as config.yml and enter in the details of the website you want to scrape from.

Before running the bot itself, make sure you run the following command to install dependencies:

    pip install -r requirements.txt


## Bot Commands
This bot has three slash commands that can be used on Discord:
- /setchannel - Use this to configure the channel that you want updates posted to
- /checkupdate - Force the bot to check for new images. This will reset the hour timer.
- /forceupdate - Force the bot to post the latest image(s), regardless of if it has already been posted. This will reset the hour timer.


## To-do
- Functionality for each guild to customise how often the bot checks for new images


## FAQ

If you get the following error message while trying to start the server: `429 Too Many Requests` (accompanied by a lot of HTML code), try the advice given in this Stackoverflow question: https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests