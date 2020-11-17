from subprocess import check_call
from sys import executable

def install(package):
    check_call([executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install("PyInquirer")
    install("simplejson")