#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def usage():
    print("{} output_dir".format(__file__))
    exit()

if len(sys.argv) != 2:
    usage()

# paths setup
dst = Path(sys.argv[1])
src = Path(os.path.dirname(os.path.realpath(__file__))).parent

def main():
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_change
    event_handler.on_moved = on_change
    event_handler.on_modified = on_change

    observer = Observer()
    observer.schedule(event_handler, str(src / Path("res")), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

def on_change(event):
    print("reloading assets: {}".format(time.strftime("%H:%M:%S", time.localtime())))
    subprocess.run([str(src / Path("scripts", "export.py")), str(dst)])

if __name__ == "__main__":
    on_change(None)
    main()
