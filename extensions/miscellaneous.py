import lightbulb
import hikari
import sqlite3
from lightbulb import Choice
from datetime import datetime
from functions.economy import initialise
from decorators.decorators import registerStatus
from dotenv import load_dotenv
import os, requests

load_dotenv()

QAPI = os.getenv("QAPI")

loader = lightbulb.Loader()

conn = sqlite3.connect('database.db')
cur = conn.cursor()

initialise()

@loader.command
class settings(lightbulb.SlashCommand, name="settings", description="Opens the settings menu."):

    boolean = lightbulb.boolean("status", "enable / disable", default=None)
    option = lightbulb.string("option", "options to modify", 
                              choices=[
                                  Choice("Dev mode","dev")
                              ], default=None)

    @lightbulb.invoke
    @registerStatus
    async def callback(self, ctx: lightbulb.Context) -> None:
        
        boolean = self.boolean
        option = self.option
        if boolean != None and option != None:
            if option == "dev":
                cur.execute("UPDATE statuses SET dev = ? WHERE userid = ?", (boolean, ctx.user.id))
                await ctx.respond(f"Dev mode has been `{"enabled" if boolean else "disabled"}`!")
                conn.commit()
        elif (boolean is not None and option is None) or (boolean is None and option is not None):
            await ctx.respond("Both `status` and `option` must be valid!")
            return


        embed = hikari.Embed(title="Solar's Control Panel", description="This is where you modify the bot's settings!")
        cur.execute("SELECT * FROM statuses WHERE userid = ?", (ctx.user.id,))
        res = cur.fetchone()
        embed.add_field("Developer Mode", f"{"Yes" if res[2] else "No"}", inline=True)
        embed.set_footer("© 2026 Solar Development. All Rights Reserved.")

        await ctx.respond(embed=embed)

@loader.command
class analytics(lightbulb.SlashCommand, name="analytics", description="Shows the user's study analytics and more."):
    
    @lightbulb.invoke
    async def callback(self, ctx: lightbulb.Context):
        # TODO: allocate some amount of work into making a chart that displays the average analytics of the users' study session and more.
        out = 1
        ctx.respond(attachment=out)

@loader.command
class rquote(lightbulb.SlashCommand, name="rquotes", description="Sends a random quote."):

    @lightbulb.invoke
    async def callback(self, ctx: lightbulb.Context):
        api = "https://api.api-ninjas.com/v2/randomquotes"
        stat = requests.get(api, headers={
            'X-Api-Key': QAPI
        })
        

        if stat.status_code == 200:
            data = stat.json()
            if data and "quote" in data[0]:
                get_quote = data[0]["quote"]
                get_author = data[0]["author"]
            else:
                get_quote = "No quote found."
                get_author = "No author found."
        else:
            get_quote = "API request failed."
            get_author = "API request failed."
        
        embed = hikari.Embed(title="Quote")
        embed.add_field(f"\"{get_quote}\" - {get_author}")
        await ctx.respond(embed=embed)

# @loader.command
# class help(lightbulb.SlashCommand, name="help", description="Opens a help menu."):
    
#     @lightbulb.invoke
#     async def callback(self, ctx: lightbulb.Context):
#         commands = ctx.client.slash_

def load(client: lightbulb.Client):
    client.register(settings)
    client.register(rquote)