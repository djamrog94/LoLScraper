import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from test import parse

class Watcher:
    DIRECTORY_TO_WATCH = "/Users/davidjamrog/PycharmProjects/LoL/data"

    def __init__(self):
        self.observer = Observer()
        self.file = ''

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        self.file = event_handler.on_any_event

        print('Watching for new game files...')
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        game = {}

        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            directory = event.src_path.split('/')
            directory = directory[-2]
            # first time started
            if game_file == '':
                game_file = directory
                try:
                    with open(f'data/{directory}/game.txt', 'r') as f:
                        game = json.load(f)
                except:
                    game = {'event': {}, 'data': {}}

            # switch games
            elif directory != game_file:
                with open(f'data/{directory}/game.txt', 'w') as file_out:
                    json.dump(game, file_out)
                    print('Saved parsed file')
                    game = {'event': {}, 'data': {}}
                    game_file = directory

            # a file from the parser
            if 'game.txt' not in event.src_path:
                with open(f'{event.src_path}', 'r') as file_in:
                    parse_data = json.load(file_in)

                    time, blue_team, red_team = parse(parse_data)
                    game['data'][time] = {}
                    game['data'][time] = {}
                    game['data'][time]['blue team'] = blue_team
                    game['data'][time]['red team'] = red_team
                    print(f'Parsed: Game @ {time} time.')


if __name__ == '__main__':
    w = Watcher()
    w.run()
