import sqlite3
import random
from datetime import datetime
import lightbulb, hikari
from decorators.decorators import prettify

conn = sqlite3.connect('database.db')
cur = conn.cursor()

def initialise():
    """
    Initialises the database to ensure that the database exists.
    """
    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY UNIQUE NOT NULL, userid INTEGER UNIQUE NOT NULL, ' \
            'sols INTEGER NOT NULL DEFAULT 0, xi INTEGER NOT NULL DEFAULT 0, study TEXT NOT NULL DEFAULT "NONE", study_start NUMERIC)')
    cur.execute('CREATE TABLE IF NOT EXISTS statuses(id INTEGER PRIMARY KEY UNIQUE NOT NULL, userid INTEGER UNIQUE NOT NULL, ' \
                'dev BOOL NOT NULL DEFAULT 0)')
    cur.execute('CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY UNIQUE NOT NULL, userid INTEGER NOT NULL, ' \
    'study_type TEXT NOT NULL, start NUMERIC, end NUMERIC, sols_acc INTEGER, xi_acc INTEGER)')
    
class StudyCalculate:

    """
    A class dedicated to study-related stuffs.
    """

    def calculate_earnings(self, data, locked_in: bool=None):
        """
        Calculates earnings for Sols and Xi.
        """

        sols, xi = 0, 0 # Initialise sols and xi as 0 to start things off

        SOL_INTERVAL = 300
        XI_INTERVAL = 1800
        XI_GRACE = 1500
        # CRITERIA: 
        # for every 25-30 minutes, reward 1 xi
        # for every 5 minutes, reward 50 sols
        # for every second, just do nothing really.

        if len(data) == 3:
            h, m, s = data
        elif len(data) == 2:
            m, s = data
            h = 0
        else:
            h = m = s = 0

        total_seconds = h*3600 + m*60 + s

        # if total_seconds < XI_GRACE:
        #     return 0, 0

        sols = (total_seconds // SOL_INTERVAL) * 50 # 300 seconds = 5 minutes
        xi = total_seconds // XI_INTERVAL # 1800 seconds = 30 minutes

        remainder = total_seconds % XI_INTERVAL # find the remaining remainder

        if remainder >= XI_GRACE: # if remainder is more than / equal to 1500 seconds (aka 25 or more minutes), add one xi
            xi += 1
        
        if locked_in:
            sols = round(sols*1.25)
            xi = round(xi*1.25)

        return sols, xi

    def update_earnings(self, ctx, sols, xi):
        """
        Process earnings for Sols and Xi.
        """
        cur.execute("UPDATE users SET sols = sols + ?, xi = xi + ? WHERE userid = ?", (sols, xi, ctx.user.id))

async def stop_studying(event, usrid):
    now = int(datetime.now().timestamp())
    cur.execute("SELECT * FROM users WHERE userid = ?", (usrid,))
    res = cur.fetchone()
    eco = StudyCalculate()

    
    cur.execute("SELECT * FROM statuses WHERE userid = ?", (usrid,))
    resx = cur.fetchone()

    cur.execute("SELECT * FROM history WHERE userid = ? AND end IS NULL ORDER BY start DESC LIMIT 1", (usrid,))
    history = cur.fetchone()

    if not history:
        print("No active session.")
        return
    
    if res:
        Δt = now - history[3]
        beautified, raw = prettify(Δt, raw_formatting=True)
        sols, xi = eco.calculate_earnings(raw)
        cur.execute('UPDATE users SET study = "NONE", sols = sols + ?, xi = xi + ? WHERE userid = ?', (sols, xi, usrid))
        cur.execute('UPDATE history SET end = ?, sols_acc = ?, xi_acc = ? WHERE id = ?', (now, sols, xi, history[0]))

        embed = hikari.Embed(title="Study session broken!", description="Your study session has been broken because you either did not chat in `#study` or you started chatting in `locked-in` mode.")
        embed.add_field("Total Study time", f"{beautified}{f" (raw: {raw})" if resx[2] == 1 else ""}", inline=True)
        embed.add_field("Earnings", f"`{sols}`𝑠 | `{xi}`ξ")
        dev = "Dev Mode Enabled. " if resx[2] == 1 else ""
        session = " 1.25x bonus (locked-in session). " if res[4] == 'li' else "Regular earning (standard-session). "
        embed.set_footer(f"{dev}{session}Take a rest!")
        await event.message.respond(embed=embed)
        conn.commit()

        return embed

class StudyChecker:
    """
    A class dedicated for deep searching user's message habit. Mainly used for checking if user is lacking off from study sessions.
    """

    async def deepcheck(self, event, author_id: int, channel_name):
        cur.execute("SELECT study FROM users WHERE userid = ?", (author_id,))
        pos = cur.fetchone()
        if pos[0] == "st":
            if channel_name == "study":
                pass
            else:
                await stop_studying(event, author_id)
        elif pos[0] == "li":
            await stop_studying(event, author_id)
        else:
            pass # Skip checking because user is not studying.

    