import sqlite3
import random

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
    
class EconomyCalculate:

    """
    A class dedicated to economy-related stuffs.
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
        conn.commit()