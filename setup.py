from subprocess import check_call
from sys import executable, argv
from phase1 import build_database

def install(package):
    check_call([executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install("PyInquirer")

    # Handle execution of phase1
    if (len(argv) >= 2 and argv[1].isdigit()):
        print("A valid database port was given, running phase 1")
        build_database(int(argv[1]))
    else:
        print("Packages installed, please build database using phase1.py")
