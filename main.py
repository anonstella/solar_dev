import hikari
from dotenv import load_dotenv
import os
import lightbulb
import sqlite3
from functions.study_related import initialise

load_dotenv()

########################################################### NOTE ##################################################################
#                                                                                                                                 #
#   ChatGPT is used for debugging purposes, such as troubleshooting error. Anything else is done by me. More on that in README.md #
#                                                                                                                                 #
########################################################### END ###################################################################

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = hikari.GatewayBot(DISCORD_TOKEN, intents=hikari.Intents.ALL)
client = lightbulb.client_from_app(bot)

bot.subscribe(hikari.StartingEvent, client.start)

conn = sqlite3.connect('database.db')
cur = conn.cursor()

initialise()

@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    for filename in os.listdir('./extensions'):
        if filename.endswith('.py'):
            await client.load_extensions(f'extensions.{filename[:-3]}')
            print(f"Initialised extensions.{filename[:-3]}!")

    await client.sync_application_commands()

bot.run()