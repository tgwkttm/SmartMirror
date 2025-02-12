import threading
import time

def print_hello():
    print("Hello from the thread!")
    time.sleep(2)
    print("Thread is done!")

#creează un thread care rulează funcția print_hello
my_thread = threading.Thread(target=print_hello)

#pornește thread-ul
my_thread.start()

#așteaptă ca thread-ul să se termine
my_thread.join()

print("Main thread is done!")
