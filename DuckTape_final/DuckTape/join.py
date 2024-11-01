from multiprocessing import Process
import subprocess
def notification_service():
    subprocess.run(["python", "notifications.py"])

def run_activity_update():
    subprocess.run(["python", "activity.py"])

#def run_pygame_gui():
    #subprocess.run(["python", "refresh_test.py"])
def run_pygame_gui():
    subprocess.run(["python", "refresh_test2.py"])

if __name__ == "__main__":
    process1 = Process(target=run_activity_update)
    process2 = Process(target= run_pygame_gui)
    #process3 = Process(target=notification_service)

    #start
    process1.start()
    process2.start()
    #process3.start()
    