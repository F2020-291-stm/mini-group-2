import build
from sys import argv

if __name__ == "__main__":
    if len(argv) < 2 or not argv[1].isdigit():
        print("No valid database port given, exiting...")
        exit()
    
    build.build_database(int(argv[1]))