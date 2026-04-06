import lightbulb
import hikari
import sqlite3
from lightbulb import Choice
from datetime import datetime
from functions.economy import initialise
from decorators.decorators import registerStatus

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

def load(client: lightbulb.Client):
    client.register(settings)