import time
import datetime
import winsound
import json
import csv
import os

# =========================
# CONFIGURATION HANDLING
# =========================
CONFIG_FILE = "config.json"
LOG_TXT = "log.txt"
LOG_CSV = "log.csv"

DEFAULT_CONFIG = {
    "beep_frequency": 1000,
    "beep_duration": 500,
    "beep_repeat": 3
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

CONFIG = load_config()

# =========================
# LOGGING SYSTEM
# =========================
def log_event(task, action, duration=0):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_TXT, "a") as f:
        f.write(f"[{now}] Task: {task}, Action: {action}, Duration: {duration} sec\n")
    with open(LOG_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now, task, action, duration])

# =========================
# ALERT SYSTEM
# =========================
def beep_alert():
    for i in range(CONFIG["beep_repeat"]):
        winsound.Beep(CONFIG["beep_frequency"], CONFIG["beep_duration"])
        time.sleep(0.15)

def ascii_alert(task):
    print("\n" + "="*50)
    print("⏰ TIME'S UP!")
    print(f"Task Completed: {task}")
    print("="*50 + "\n")

# =========================
# TIMER CLASS
# =========================
class CountdownTimer:
    def __init__(self, seconds, task="Unnamed Task"):
        self.seconds = seconds
        self.task = task
        self.paused = False
        self.cancelled = False

    def start(self):
        log_event(self.task, "Started", self.seconds)
        while self.seconds > 0 and not self.cancelled:
            if not self.paused:
                mins, secs = divmod(self.seconds, 60)
                timer = f"{mins:02d}:{secs:02d}"
                print(f"[{self.task}] {timer}", end="\r")
                time.sleep(1)
                self.seconds -= 1
            else:
                time.sleep(1)
        if not self.cancelled:
            beep_alert()
            ascii_alert(self.task)
            log_event(self.task, "Completed")
            self.snooze_option()

    def pause(self):
        self.paused = True
        log_event(self.task, "Paused")

    def resume(self):
        self.paused = False
        log_event(self.task, "Resumed")

    def cancel(self):
        self.cancelled = True
        log_event(self.task, "Cancelled")

    def snooze_option(self):
        choice = input("Do you want to snooze? (y/n): ")
        if choice.lower() == "y":
            print("Choose snooze input type:")
            print("1. Minutes")
            print("2. Seconds")
            try:
                opt = int(input("Enter choice (1/2): "))
                if opt == 1:
                    snooze_minutes = int(input("Enter snooze time in minutes: "))
                    snooze_seconds = snooze_minutes * 60
                elif opt == 2:
                    snooze_seconds = int(input("Enter snooze time in seconds: "))
                else:
                    print("Invalid choice. Snooze cancelled.")
                    return
                log_event(self.task, "Snoozed", snooze_seconds)
                snoozed_timer = CountdownTimer(snooze_seconds, self.task + f" (Snoozed)")
                snoozed_timer.start()
            except ValueError:
                print("Invalid input. Snooze cancelled.")

# =========================
# STATISTICS REPORT
# =========================
def show_statistics():
    total_tasks = 0
    completed = 0
    snoozed = 0
    cancelled = 0
    paused = 0

    if os.path.exists(LOG_CSV):
        with open(LOG_CSV, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3: 
                    continue
                total_tasks += 1
                action = row[2]
                if action == "Completed":
                    completed += 1
                elif action == "Snoozed":
                    snoozed += 1
                elif action == "Cancelled":
                    cancelled += 1
                elif action == "Paused":
                    paused += 1

    print("\n--- Statistics Report ---")
    print(f"Total Events: {total_tasks}")
    print(f"Completed: {completed}")
    print(f"Snoozed: {snoozed}")
    print(f"Cancelled: {cancelled}")
    print(f"Paused: {paused}")
    print("-------------------------\n")

# =========================
# MENU SYSTEM
# =========================
def menu():
    while True:
        print("\n--- Countdown Timer Menu ---")
        print("1. Set timer in seconds")
        print("2. Set timer in minutes")
        print("3. Set timer in HH:MM:SS format")
        print("4. Show statistics")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            try:
                sec = int(input("Enter seconds: "))
                task = input("Enter task name: ")
                timer = CountdownTimer(sec, task)
                timer.start()
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "2":
            try:
                mins = int(input("Enter minutes: "))
                task = input("Enter task name: ")
                timer = CountdownTimer(mins * 60, task)
                timer.start()
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            try:
                time_str = input("Enter time (HH:MM:SS): ")
                h, m, s = map(int, time_str.split(":"))
                total_sec = h*3600 + m*60 + s
                task = input("Enter task name: ")
                timer = CountdownTimer(total_sec, task)
                timer.start()
            except Exception as e:
                print("Invalid format. Please use HH:MM:SS.")
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            print("Exiting Countdown Timer. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()


