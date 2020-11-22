import sys, menus, cli, mdatabase
from sys import argv
from pymongo import MongoClient

if __name__ == "__main__":
    #if (len(argv) < 2 or not argv[1].isdigit()):
    #    print("No database port given, exiting...")
    #    exit()
    client = MongoClient('localhost', 27017#int(argv[1]))
    )
    db = client['291db']
    database = mdatabase.Database(db)

    uid = cli.login() #asks user for uid
    if uid != '':
        menus.user_report(database, uid) #shows user report, if not anonymous user
    
    while True: #until the user quits the system
        choice = cli.master_menu_select()

        if choice == 'Post a question': #can either post a new question
            menus.write_post(database, uid, "question")
        elif choice == 'Search for questions': #or search for posts. More can be done from there
            menus.search_and_act(database, uid)
        else:
            sys.exit(0)




