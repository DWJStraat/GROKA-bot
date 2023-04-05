from subprocess import run
from time import sleep

file_path = "telegram_bot.py"

restart_timer = 2

def start_script():
    try:
        run(f"python{file_path}", check=True)
    except Exception as e:
        print(f"Error while starting script:\n{e}")
        handle_crash()

def handle_crash():
    print(f"Restarting script in {restart_timer} seconds")
    sleep(restart_timer)
    start_script()

start_script()