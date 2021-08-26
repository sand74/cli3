import sys

from memory_profiler import profile

from app import Cli3App
from main_window import MainWindow

@profile
def main():
    app = Cli3App(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()