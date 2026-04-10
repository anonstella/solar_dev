import lightbulb
from lightbulb import Choice
import sqlite3
from datetime import datetime
import hikari
from decorators.decorators import registerStatus, prettify
from functions.study_related import initialise, StudyCalculate, StudyChecker

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
                cur.execute("INSERT INTO history(userid, study_type, start) VALUES(?, ?, ?)", (ctx.user.id, "st", now))
                conn.commit()
            elif st == 'li':
                mode = 'locked-in'
                cur.execute("UPDATE users SET study = 'li' WHERE userid = ?", (ctx.user.id,))
                cur.execute("UPDATE users SET study_start = ? WHERE userid = ?", (now, ctx.user.id))
                cur.execute("INSERT INTO history(userid, study_type, start) VALUES(?, ?, ?)", (ctx.user.id, "li", now))
                conn.commit()
            else:
                await ctx.respond("Invalid study type.")
                return
            await ctx.respond(f"Study session started in `{mode}` mode! To stop, run `/stop`.")

@loader.command
class stop(lightbulb.SlashCommand, name="stop", description="Stops a study session."):
    
    @lightbulb.invoke
    @registerStatus
    async def callback(self, ctx: lightbulb.Context) -> None:
        now = int(datetime.now().timestamp())
        cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,))
        res = cur.fetchone()
        if not res:
            await ctx.respond("You're not in the database!")
            return
        if res[4] in ('st', 'li'): # <---- res[4] resembles "study" column.
            if res[5] is None:
                await ctx.respond("Study start time missing.")
                return
            resx = cur.execute("SELECT * FROM statuses WHERE userid = ?", (ctx.user.id,)).fetchone()

            if not resx:
                await ctx.respond("You're not in the status database (somehow). Contact staff to resolve this issue.")
                return

            cur.execute("SELECT * FROM history WHERE userid = ? AND end IS NULL ORDER BY start DESC LIMIT 1", (ctx.user.id,))
            history = cur.fetchone()

            if not history:
                await ctx.respond("No active study session.")
                return

            Δt = now - history[3]
            beautified, raw = prettify(Δt)
            eco = StudyCalculate()
            sols, xi = eco.calculate_earnings(raw)
            cur.execute("UPDATE history SET end = ?, sols_acc = ?, xi_acc = ? WHERE id = ?", (now, sols, xi, history[0]))
            cur.execute("UPDATE users SET study = 'NONE' WHERE userid = ?", (ctx.user.id,))
            embed = hikari.Embed(title="Study Session Wraps Up!", description="Your study session has been completed.")
            embed.add_field("Total Study time", f"{beautified}{f" (raw: {raw})" if resx[2] == 1 else ""}", inline=True)
            embed.add_field("Earnings", f"`{sols}`𝑠 | `{xi}`ξ")
            dev = "Dev Mode Enabled. " if resx[2] == 1 else ""
            session = " 1.25x bonus (locked-in session). " if res[4] == 'li' else "Regular earning (standard-session). "
            embed.set_footer(f"{dev}{session}Take a rest!")
            cur.execute("UPDATE users SET sols = sols + ?, xi = xi + ? WHERE userid = ?", (sols, xi, ctx.user.id))
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("You're not currently on a study session! Make sure to start it first!", ephemeral=True)
        
        conn.commit()

@loader.command
class elapse(lightbulb.SlashCommand, name="elapse", description="Check how long has study session elapsed."):
    
    @lightbulb.invoke
    @registerStatus
    async def callback(self, ctx: lightbulb.Context) -> None:
        study = cur.execute("SELECT study FROM users WHERE userid = ?", (ctx.user.id,)).fetchone()
        if study is None or study[0] not in ("li", "st"):
            await ctx.respond("You haven't start studying yet! Do so by running `/study [type]`,")
        else:
            alloc = cur.execute("SELECT study_start FROM users WHERE userid = ?", (ctx.user.id,)).fetchone()
            now = int(datetime.now().timestamp())
            calc = now - alloc[0]
            elapse, raw = prettify(calc)
            resx = cur.execute("SELECT * FROM statuses WHERE userid = ?", (ctx.user.id,)).fetchone()
            await ctx.respond(f"Total time elapsed: `{elapse}`{f" (raw = `{raw}`)" if resx[2] == 1 else ""}.")

@loader.listener(hikari.MessageCreateEvent)
async def lockedInCheck(event: hikari.MessageCreateEvent) -> None:
    if event.is_bot:
        return
    sc = StudyChecker()
    channel = await event.app.rest.fetch_channel(event.channel_id)
    await sc.deepcheck(event, event.author.id, channel.name)
    

def load(client: lightbulb.Client):
    client.register(start)
    client.register(stop)