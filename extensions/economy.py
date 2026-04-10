import lightbulb
import sqlite3
from decorators.decorators import *
from functions.study_related import *
import hikari

loader = lightbulb.Loader()

conn = sqlite3.connect('database.db')
cur = conn.cursor()


initialise()

@loader.command
class profile(lightbulb.SlashCommand, name="profile", description="Shows the user's profile."):
    
    @lightbulb.invoke
    async def callback(self, ctx: lightbulb.Context) -> None:
        cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,))
        inf = cur.fetchone()

        embed = hikari.Embed(title=f"{ctx.user.global_name}'s Core")
        embed.add_field("Sols [𝑠]", inf[2])
        embed.add_field("Xi [ξ]", inf[3])
        embed.set_thumbnail(ctx.user.display_avatar_url.url)
        await ctx.respond(embed=embed)
    

def load(client: lightbulb.Client):
    client.register(profile)