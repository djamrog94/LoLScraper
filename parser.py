import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from historic_parse import parse
import pandas as pd

class Watcher:
    DIRECTORY_TO_WATCH = "/Users/davidjamrog/PycharmProjects/LoL/data/live"

    def __init__(self):
        self.observer = Observer()
        self.file = ''

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        self.file = event_handler.on_created
        process_data()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    def on_created(self, event):
        file = event.src_path
        with open(file, 'r') as f:
            data = json.load(f)
        df = parse(data, 'live', 'error.txt')
        try:
            master = pd.read_excel('master.xlsx')
        except:
            master = pd.DataFrame()
        master.append(df)
        master.to_excel('master.xlsx')

def process_data():
    print('Hi')

if __name__ == '__main__':
    master = pd.DataFrame()
    w = Watcher()
    w.run()


