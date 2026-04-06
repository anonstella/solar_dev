import sqlite3
from functools import wraps

"""
A module used to register custom decorators and/or functions.
"""

conn = sqlite3.connect('database.db')
cur = conn.cursor()

def registerStatus(func):
    """
    Checks the registration status of a user. If the user is registered to the database, then skip the registration process, otherwise create the user's database first, then continue.
    """
    @wraps(func)
    async def wrapper(self, ctx):
        result = cur.execute("SELECT * FROM users WHERE userid = ?", (ctx.user.id,)).fetchone()

        statuses = cur.execute("SELECT * FROM statuses WHERE userid = ?", (ctx.user.id,)).fetchone()

        if result is None:
            cur.execute("INSERT INTO users(userid) VALUES(?)", (ctx.user.id,))
            cur.execute("INSERT INTO statuses(userid) VALUES(?)", (ctx.user.id,))
            conn.commit()
        elif statuses is None:
            cur.execute("INSERT INTO statuses(userid) VALUES(?)", (ctx.user.id,))
            conn.commit()
        
        return await func(self, ctx)
    return wrapper

def prettify(seconds: int=None, time: bool=None) -> str:
    """
    converts seconds into readable format.
    """
    if seconds is not None:
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60

        data = []
        raw = []

        if hrs > 0:
            data.append(f"{hrs}h")
            raw.append(hrs)
        if mins > 0:
            data.append(f"{mins}m")
            raw.append(mins)
        
        data.append(f"{secs}s")
        raw.append(secs)

        return " ".join(data), raw
   #  else:
    return " ".join(data), raw 
