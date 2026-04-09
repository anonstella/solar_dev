import lightbulb
import sqlite3
from decorators.decorators import *
from functions.economy import *
import hikari

loader = lightbulb.Loader()

conn = sqlite3.connect('database.db')
cur = conn.cursor()


initialise()

@loader.command
class balance(lightbulb.SlashCommand, name="balance", description="Shows the balance of the user."):
    
    @lightbulb.invoke
    async def callback(self, ctx: lightbulb.Context) -> None:
        #TODO: Make it respond an embed of a user's wallet balance.
        cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,))
        inf = cur.fetchone()

        embed = hikari.Embed(title=f"{ctx.user.global_name}'s Core")
        embed.add_field("Sols [𝑠]", inf[2])
        embed.add_field("Xi [ξ]", inf[3])
        embed.set_thumbnail(ctx.user.display_avatar_url.url)
        await ctx.respond(embed=embed)
    

def load(client: lightbulb.Client):
    client.register(balance)