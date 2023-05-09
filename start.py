import os
import time
print('starting...')
while True:
    os.system("python3 telegram_bot.py")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open("log.txt", "a") as f:
        f.write(f"/!\{timestamp} | Bot crashed, restarting.../!\\\n")
    print("Bot crashed, restarting in 10 seconds. Press ctrl+c to stop.")

