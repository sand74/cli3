import argparse
import logging
import os
import resource
import sys
import time
from time import sleep

from PyQt5.QtWidgets import QDialog
from pyupdater.client import Client

import cli3
from cli3.app import Cli3App
from cli3.main_window import MainWindow
# from cli3update.client_config import ClientConfig
from cli3.update_dialog import UpdateDialog, Downloader
from updates.client_config import ClientConfig


class MemoryMonitor:
    def __init__(self):
        self.keep_measuring = True

    def measure_usage(self):
        max_usage = 0
        while self.keep_measuring:
            max_usage = max(
                max_usage,
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            )
            print('Memory usage:', max_usage)
            sleep(10)

        return max_usage


logger = logging.getLogger(__name__)
STDERR_HANDLER = logging.StreamHandler(sys.stderr)
STDERR_HANDLER.setFormatter(logging.Formatter(logging.BASIC_FORMAT))


class UpdateStatus(object):
    """Enumerated data type"""
    # pylint: disable=invalid-name
    # pylint: disable=too-few-public-methods
    UNKNOWN = 0
    NO_AVAILABLE_UPDATES = 1
    UPDATE_DOWNLOAD_FAILED = 2
    EXTRACTING_UPDATE_AND_RESTARTING = 3
    UPDATE_AVAILABLE_BUT_APP_NOT_FROZEN = 4
    COULDNT_CHECK_FOR_UPDATES = 5
    UPDATE_IGNORED = 6


UPDATE_STATUS_STR = \
    ['Unknown', 'No available updates were found.',
     'Update download failed.', 'Extracting update and restarting.',
     'Update available but application is not frozen.',
     'Couldn\'t check for updates.', 'Update ignored']


def parse_args(argv):
    """
    Parse command-line args.
    """
    usage = ("%(prog)s [options]\n"
             "\n"
             "You can also run: python setup.py nosetests")
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("--version", action='store_true',
                        help="displays version")
    return parser.parse_args(argv[1:])


def initialize_logging(debug=False):
    """
    Initialize logging.
    """
    logger.addHandler(STDERR_HANDLER)
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger.setLevel(level)
    #    logging.getLogger("wxupdatedemo.fileserver").addHandler(STDERR_HANDLER)
    #    logging.getLogger("wxupdatedemo.fileserver").setLevel(level)
    logging.getLogger("pyupdater").setLevel(level)
    logging.getLogger("pyupdater").addHandler(STDERR_HANDLER)


__version__ = '0.0.1'


def check_for_updates(debug):
    """
    Check for updates.
    Channel options are stable, beta & alpha
    Patches are only created & applied on the stable channel
    """
    #    assert CLIENT_CONFIG.PUBLIC_KEY is not None
    client = Client(ClientConfig, refresh=True)
    appUpdate = client.update_check(ClientConfig.APP_NAME,
                                    cli3.__version__,
                                    channel='alpha')
    downloader = Downloader(client, appUpdate)
    update_dialog = UpdateDialog(downloader)
    status = UpdateStatus.NO_AVAILABLE_UPDATES
    if appUpdate:
        if debug or hasattr(sys, "frozen"):
            ret = update_dialog.exec()
            if ret == QDialog.Accepted:
                if debug:
                    logger.debug('Extracting update and restarting...')
                    time.sleep(10)
                else:
                    appUpdate.extract_restart()
                status = UpdateStatus.EXTRACTING_UPDATE_AND_RESTARTING
            elif ret == QDialog.Rejected:
                status = UpdateStatus.UPDATE_IGNORED
            else:
                status = UpdateStatus.UPDATE_DOWNLOAD_FAILED
        else:
            status = UpdateStatus.UPDATE_AVAILABLE_BUT_APP_NOT_FROZEN
    return status


def display_version_and_exit():
    """
    Display version and exit.
    In some versions of PyInstaller, sys.exit can result in a
    misleading 'Failed to execute script run' message which
    can be ignored: http://tinyurl.com/hddpnft
    """
    sys.stdout.write("%s\n" % __version__)
    sys.exit(0)


def main(argv):
    args = parse_args(argv)
    if args.version:
        display_version_and_exit()
    print('DEBUG', os.environ.get('DEBUG', 0))
    initialize_logging(os.environ.get('DEBUG', 0) == '1')
    app = Cli3App(argv)
    status = check_for_updates(os.environ.get('DEBUG', 0) == '1')
    print('Update status', UPDATE_STATUS_STR[status])
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception as e:
        print('Exception:', e)
