from subprocess import check_call
from sys import executable, argv
from phase1 import build_database
from setuptools import setup
from Cython.Build import cythonize

def install(package):
    check_call([executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install("PyInquirer")
    install("Cython")

    # Handle execution of phase1
    if (len(argv) >= 2 and argv[1].isdigit()):
        print("A valid database port was given, running phase 1")
        setup(ext_modules = cythonize("phase1.pyx"))
        build_database(int(argv[1]))
    else:
        print("Packages installed, please build database using phase1.py")
        setup(ext_modules = cythonize("phase1.pyx"))
