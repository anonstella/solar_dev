import hikari
from dotenv import load_dotenv
import os
import lightbulb
import sqlite3
from functions.economy import initialise

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = hikari.GatewayBot(TOKEN)
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