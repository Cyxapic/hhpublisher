import time
import argparse
from datetime import datetime

from daemon import Daemon
from hh_api import DataAPI, Resume


class PublisherDaemon(Daemon):

    def __init__(self, **kwargs):
        data_api = DataAPI().handler()
        self.resume = Resume(data_api)
        super().__init__(**kwargs)

    def run(self):
        while True:
            self.resume.send_request()
            time.sleep(self._time_to_wait())

    def quit(self):
        with open('stop.log', 'w') as f:
            f.write(f'Daemon stoped at {datetime.now()}')

    def _time_to_wait(self, next_publish_at=None):
        '''next_publish_at=None Need to findout what they send'''
        return 60*60*24 # per day

def get_publisher_args():
    description = (
        "Publisher daemon for publish resume at HeadHunter service\n"
    )
    usage =  ("\n"
        "\t - publisher.py start - start daemon\n"
        "\t - publisher.py stop - stop daemon\n"
        "\t - publisher.py restart - restart daemon\n"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.usage = usage
    parser.add_argument(
        "command",
        type=str,
        nargs='?',
        default=None,
        help="start, stop or restart"
    )
    args = parser.parse_args()
    return args.command


def main():
    publisher = PublisherDaemon()
    DAEMON_METHODS = {
        'start': publisher.start,
        'stop': publisher.stop,
        'restart': publisher.restart,
    }
    arg = get_publisher_args()
    command = DAEMON_METHODS.get(arg)
    if command:
        print(f"{arg.title()}ing daemon ... To help use publisher.py -h")
        command()
    else:
        print("Don't know command!")


if __name__ == '__main__':
    main()
