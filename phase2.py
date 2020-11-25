import menus, mdatabase
from sys import argv

if __name__ == "__main__":
    if (len(argv) < 2 or not argv[1].isdigit()):
        print("No database port given, exiting...")
        exit()
    database = mdatabase.Database(int(argv[1]))
    menus.user_login(database)
    menus.master_menu(database)





