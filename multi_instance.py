"""
This function allows the simultaneous running of numerous instances of driver.py
This is useful because can easily manipulate the index of the game to be parsed.
This allows multi parsing to happen with less of a chance of parsing same game numerous times
"""

from driver import *
count = 0
variance = int(input('Enter variance: '))
while count < 3:

    try:
        main(variance)
        count = 0
    except:
        time.sleep(300)
        count += 1
