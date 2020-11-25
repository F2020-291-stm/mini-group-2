import build
from sys import argv
import time

if __name__ == "__main__":
    if len(argv) < 2 or not argv[1].isdigit():
        print("No valid database port given, exiting...")
        exit()
    starttime = time.time()
    build.build_database(int(argv[1]))
    print("------process takes " + time.time() - starttime)