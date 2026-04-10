from functools import wraps
import sqlite3
import lightbulb
import hikari
import numpy as np
import matplotlib.pyplot as plt
import PIL
from PIL import Image, ImageDraw, ImageFont
from decorators.decorators import prettify

conn = sqlite3.connect('database.db')
cur = conn.cursor()

def analyse(userid, display_advanced: str=None):
    categories = ["≤1h", "2h", "3h", "4h", "5h+"]
    times = []
    categs = [0, 0, 0, 0, 0] # accordingly to categories variable
    cur.execute("SELECT study_type, start, end, sols_acc, xi_acc FROM history WHERE userid = ?", (userid,))
    typelist = cur.fetchall()
    for type in typelist: # incrementation for datas
        calct = type[2] - type[1]
        res = prettify(calct, raw_formatting=True)
        pos = res[1][0]
        if pos >= 1:
            if pos >= 5:
                categs[4] += 1
                times.append(calct)
            else:
                categs[pos-1] += 1
                times.append(calct)
        else:
            categs[0] += 1
            times.append(calct)
    values = np.array(categs)

    colours = ["cyan", "green", "yellow", "orange", "red"]
    plt.pie(values, labels=categories, colors=colours)
    plt.title("Average Study Session Duration")

    plt.savefig('assets/session_average.png')

    # Time calculations
    time_sum = sum(times)
    average = (time_sum) / (len(times))
    resx = prettify(int(average))
    compute_avg = resx
    raw_times = []
    for time in times:
        res = prettify(time)
        raw_times.append(res)


    cur.execute("SELECT sols, xi FROM users WHERE userid = ?", (userid,))
    sols, xi = cur.fetchone()


    MAX = max(categs)
    most = categs.index(MAX)
    ins = ["around 1 hour", "2 hours", "3 hours", "4 hours", "5 or more hours"]
    insights = ins[most]

    # Image processing
    image = Image.open('assets/session_average.png')
    if not display_advanced:
        # 213, 130 - Insights box
        # 68, 867 - coordinates for corner of average session
        # 1059, 747 - coords for corner of total sols accumulated
        # 1059, 817 - same but for xi
        background = Image.open('assets/background.png')
        draw = ImageDraw.Draw(background)
        background.paste(image, (320, 187))
        font = ImageFont.truetype('assets/Montserrat-Medium.ttf', size=55)
        font_para = ImageFont.truetype('assets/Montserrat-Medium.ttf', size=35)
        draw.text((68, 867), compute_avg, fill=(255, 255, 255), font=font)
        draw.text((1059, 747), str(sols), fill=(255, 255, 255), font=font_para)
        draw.text((1059, 817), str(xi), fill=(255, 255, 255), font=font_para)
        draw.text((213, 130), f"Most of your sessions are {insights}.", fill=(255, 255, 255), font=font_para)
        
        background.save('assets/out.png')
        img = 'assets/out.png'
    elif display_advanced:
        # 348, 179 - Insight bar corner
        # 87, 360 - Pie chart corner
        # 933, 510 - Longest study session corner
        # 1428, 510 - Average Study Session corner
        # 1427, 675 - Sols corner
        # 1427, 765 - Xi corner
        # 1377, 873 = Total study time corner
        background = Image.open('assets/background-advanced.png')
        background.paste(image, (87, 360))
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype('assets/Montserrat-Medium.ttf', size=55)
        font_alt = ImageFont.truetype('assets/Montserrat-Medium.ttf', size=45)

        LONG = times.index(max(times))

        longest = prettify(times[LONG])
        
        total_time = prettify(time_sum)

        draw.text((348, 179), f"Most of your sessions are {insights}.", fill=(255, 255, 255), font=font)
        draw.text((933, 510), longest, fill=(255, 255, 255), font=font_alt)
        draw.text((1428, 510), compute_avg, fill=(255, 255, 255), font=font_alt)
        draw.text((1427, 675), str(sols), fill=(255, 255, 255), font=font_alt)
        draw.text((1427, 765), str(xi), fill=(255, 255, 255), font=font_alt)
        draw.text((1377, 873), total_time, fill=(255, 255, 255), font=font)

        background.save('assets/out-adv.png')
        img = 'assets/out-adv.png'
    else:
        img = '404.png'

    return img, compute_avg, raw_times