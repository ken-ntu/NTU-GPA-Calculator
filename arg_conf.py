import argparse

class ArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("path", help="path/to/your/ntu/etranscript")
        self.add_argument("--ignore-warnings", action='store_true', help="ignore warnings from pdfplumber")
        self.add_argument("-d", "--debug", action="store_true", help="use debug mode. Debug message will be print")