# Web Scraper Discord Bot
This is a Discord bot that scrapes images from a given website and CSS selector.

## Getting Started
To get set up, you'll need to follow [these bot account setup instructions](https://discordpy.readthedocs.io/en/stable/discord.html), and then copy the token for your bot and add it to an .env file with the key `BOT_TOKEN` (see example.env)

After that, copy the config_example.yml file as config.yml and enter in the details of the website you want to scrape from.

Before running the bot itself, make sure you run the following command to install dependencies:

    pip install -r requirements.txt

## FAQ

If you get the following error message while trying to start the server: `429 Too Many Requests` (accompanied by a lot of HTML code), try the advice given in this Stackoverflow question: https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests