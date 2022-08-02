from alive_progress import alive_bar
import time

from random import randrange


def aliveBar(x, sleepSpeed=0.05, title='', spinner='twirls'):
    with alive_bar(int(x), title=str(title)) as bar:   # default setting
        for i in range(int(x)):
            time.sleep(float(sleepSpeed))
            bar()

#aliveBar(100)

# 5 seconds = 100

instanceName = ['i-03e54b3f4919619ae', 'i-078d9fc4875dcf98e']

for i in instanceName:
    aliveBar(100 + randrange(100, 200), 0.05,
             "Terminating " + i, spinner='twirls')


# 2 mins 30 seconds = delete total 2 connect peers
# 180

# 3600 for 2 tgw connect