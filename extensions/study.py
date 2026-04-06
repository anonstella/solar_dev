import lightbulb
from lightbulb import Choice
import sqlite3
from datetime import datetime
from decorators.decorators import registerStatus, prettify
from functions.economy import initialise, EconomyCalculate

loader = lightbulb.Loader()

conn = sqlite3.connect('database.db')
cur = conn.cursor()

initialise()

@loader.command
class start(lightbulb.SlashCommand, name="start", description="Starts a study session."):
    session_type = lightbulb.string("type", "session type (standard/locked-in)", 
                                    choices=
                                    [
                                        Choice('standard', 'st'),
                                        Choice('locked-in', 'li')
                                    ]
                                    )

    @lightbulb.invoke
    @registerStatus
    async def callback(self, ctx: lightbulb.Context) -> None:
        now = int(datetime.now().timestamp())
        st = self.session_type
        if cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,)).fetchone()[4] != "NONE":
            await ctx.respond(f"You already have an active study session. Please stop current session before running this again.", ephemeral=True)
        else:
            if st == 'st':
                mode = 'standard'
                cur.execute("UPDATE users SET study = 'st' WHERE userid = ?", (ctx.user.id,))
                cur.execute("UPDATE users SET study_start = ? WHERE userid = ?", (now, ctx.user.id))
                conn.commit()
            elif st == 'li':
                mode = 'locked-in'
                cur.execute("UPDATE users SET study = 'li' WHERE userid = ?", (ctx.user.id,))
                cur.execute("UPDATE users SET study_start = ? WHERE userid = ?", (now, ctx.user.id))
                conn.commit()
            await ctx.respond(f"Study session started in `{mode}` mode! To stop, run `/stop`.")

@loader.command
class stop(lightbulb.SlashCommand, name="stop", description="Stops a study session."):
    
    @lightbulb.invoke
    @registerStatus
    async def callback(self, ctx: lightbulb.Context) -> None:
        now = int(datetime.now().timestamp())
        cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,))
        res = cur.fetchone()
        if res[4] in ('st', 'li'): # <---- res[4] resembles "study" column.
            cur.execute("UPDATE users SET study = 'NONE' WHERE userid = ?", (ctx.user.id,))
            conn.commit()
            if res[5] is None:
                await ctx.respond("Study start time missing.")
                return
            Δt = now - res[5]
            beautified, raw = prettify(Δt)
            eco = EconomyCalculate()
            sols, xi = eco.calculate_earnings(raw)
            eco.update_earnings(ctx, sols, xi)
            resx = cur.execute("SELECT * FROM statuses WHERE userid = ?", (ctx.user.id,)).fetchone()
            await ctx.respond(f"Your study session has been stopped :) Go take a rest.\nTotal study time: `{beautified}` {f" (raw = `{raw}`)" if resx[2] == 1 else ""}.\nEarnings: {sols}𝑠 | {xi}ξ") #{timeΔ} 
        else:
            await ctx.respond("You're not currently on a study session! Make sure to start it first!", ephemeral=True)

def load(client: lightbulb.Client):
    client.register(start)
    client.register(stop)