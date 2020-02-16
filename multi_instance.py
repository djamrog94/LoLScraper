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
