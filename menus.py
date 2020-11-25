import cli

def user_login(database):
    """Logins a user

    Args:
        database (Database): db to use
    """
    uid = cli.login()
    if uid != '':
        user_report(database, uid)
        database.use_uid(uid)

def user_report(database, uid):
    """Shows a report of a user

    Args:
        database (Database): db to use
        uid (str): user id
    """
    #done
    print("\nUser Report")
    print("User: " + str(uid))
    report = database.get_user_report(uid) #fetches the posts posted by this user

    print("Questions Posted: {}".format(report['qcount']))
    print("Question Average Score: {}".format(report['qavg']))
    print("Answers Posted: {}".format(report['acount']))
    print("Answer Average Score: {}".format(report['aavg']))
    print("Votes Registered: {}{}".format(report['vcount'], '\n'))

def write_question(database):
    """Prompts the user for questions and inserts into database

    Args:
        database (Database): db to use
    """
    database.post_question(cli.write_question())

def write_answer(database, qid):
    """Writes an answer

    Args:
        database (Database): db to us
        qid (str): question id
    """
    post = cli.write_answer()
    post['qid'] = str(qid)
    database.post_answer(post) 

def find_questions(database):
    """Finds questions

    Args:
        database (Database): db to use
    """
    #done
    keywords = cli.get_keywords() #asks for keywords to base search off of
    questions = database.find_questions(keywords)
    if len(questions) == 0:
        print("No questions found matching given keywords")
        return
    qid = choose_post(questions, True)
    action_menu(database, qid) 

def action_menu(database, pid, is_question=True):
    """Choose an action for a pid

    Args:
        database (Database): Database to us
        pid (str): post id
        is_question (bool, optional): if post is question. Defaults to True.
    """
    display_post(database, pid)

    response = cli.action_menu_select(is_question)
    if response == 'Answer question':
        write_answer(database, pid)

    elif response == 'List answers':
        list_answers(database, pid)

    elif response == 'Upvote':
        database.up_vote(database, pid)
        print("You upvoted this post!\n")

def list_answers(database, pid):
    """Lists all the answers for a post

    Args:
        database (Database): Database to use
        pid (str): Question id
    """
    #done
    answers_found = database.find_answers(pid)

    a_found_list = []
    for answer in answers_found:
        a_found_list.append(answer)

    if a_found_list is None:
        print('This question has no answers\n')
    else:
        #finds all answers and puts accepted answer at front of list
        question = database.get_post(pid)
        if 'AcceptedAnswerId' in question.keys():
            accepted_answer = database.get_post(question['AcceptedAnswerId'])
            a_found_list.remove(accepted_answer)
            accepted_answer['is_acc_ans'] = True
            a_found_list.insert(0, accepted_answer)
        
        aid = choose_post(a_found_list, False)

        action_menu(database, aid, False)

def display_post(database, pid):
    """Displays the contents of a post

    Args:
        database (Database): Database to use
        pid (str): Post id
    """
    post = database.get_post(pid)

    print("\nShowing Post " + post['Id'] + ":")
    for key in post:
        if key != "_id" and key != 'Id':
            print(key + ": " + str(post[key]))

    print('')
    
def choose_post(posts, is_question):
    """Chooses a post from a list

    Args:
        posts (list(dict)): posts
        is_question (bool): if posts are questions

    Returns:
        str: post id 
    """
    PAGE_SIZE = 10
    page_index = 0
    response = '+'
    while response != '+' or response != '-':
        show_next = (page_index + 1)*PAGE_SIZE <= len(posts)
        show_prev = page_index > 0

        if is_question:
            response = cli.choose_question(posts[page_index*PAGE_SIZE:(page_index + 1)*PAGE_SIZE], show_next, show_prev)
        else:
            response = cli.choose_answer(posts[page_index*PAGE_SIZE:(page_index + 1)*PAGE_SIZE], show_next, show_prev)

        if response == '+':
            page_index = page_index + 1
        elif response == '-':
            page_index = page_index - 1
        else:
            return response

def master_menu(database):
    """Shows the master menu

    Args:
        database (Database): Database to use
    """
    while True: #until the user quits the system
        choice = cli.master_menu_select()
        if choice == 'Post a question': #can either post a new question
            write_question(database)
        elif choice == 'Search for questions': #or search for posts. More can be done from there
            find_questions(database)
        else:
            break

