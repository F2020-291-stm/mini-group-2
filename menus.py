import cli

def user_report(database, uid):
    #done
    print("\nUser Report")
    print("User: " + str(uid))
    num_votes = database.get_user_received_votes(uid) #fetches number of votes received
    posts = database.get_user_posts(uid) #fetches the posts posted by this user
    num_questions = 0
    num_answers = 0
    q_avg_score = 0
    a_avg_score = 0

    #TODO This can feasibly be done in the database class... 
    #calculates above four values by going through each user's posts and counting
    for post in posts:
        if posts['PostTypeId'] == 1: #is a question
            num_questions += 1
            q_avg_score += post['Score']
        else:
            num_answers += 1
            a_avg_score += post['Score']

    #in case of division by 0
    try:
        q_avg_score = q_avg_score/num_questions
    except:
        q_avg_score = 0
    try:
        a_avg_score = a_avg_score/num_answers
    except:
        a_avg_score = 0

    print("Questions Posted: " + str(num_questions))
    print("Question Average Score: " + str(q_avg_score))
    print("Answers Posted: " + str(num_answers))
    print("Answer Average Score: " + str(a_avg_score))
    print("Votes Received: " + str(num_votes) + "\n")    

def write_post(database, uid, type_of_post):
    #done
    print("\nEnter your " + type_of_post + "\n")
    post = cli.write_post()

    tags = [string.strip() for string in post["tags"].split(';')] #converts given string into a list of tags
    post["tags"] = tags
    if type_of_post == "question":
        post["type"] = 1
    else:
        post["type"] = 2
    post["uid"] = uid

    database.create_post(post)    

def search_and_act(database, uid):
    #done
    keywords = cli.get_keyword() #asks for keywords to base search off of
    keywords_list  = [string.strip() for string in keywords]
    questions_found = database.search(keywords_list)
    questions_found = [{"Id": 5, "Title": "question_title", "CreationDate": "now", "Score": 10, "AnswerCount": 5}] #remove this later


    if questions_found is None:
        print('No matches found')
    else:
        while True:
            pid = generate_search_list(questions_found)
            if pid != '+':
                break

        action_menu(database, uid, pid) 

def action_menu(database, uid, pid, is_question=True):
    #done
    display_post(database, pid)

    response = cli.action_menu_select(is_question)
    if response == 'Answer question':
        write_post(database, uid, "answer")

    elif response == 'List answers':
        answers_found = database.find_answers(pid)
        answers_found = [{"Id": 15, "Title": "answer_title", "CreationDate": "now", "Score": 10}] #remove this later

        while True:
            response = generate_search_list(answers_found)
            if response != '+':
                break

        action_menu(database, uid, response, False)

    elif response == 'Upvote':
        database.up_vote(database, uid, pid)

def display_post(database, pid):
    #done
    post = database.get_post(pid)
    post = {"Id": 45, "Title": "question_title", "CreationDate": "now", "Score": 10, "AnswerCount": 5} #remove this later

    print("\nShowing Post:")
    for key in post:
        print(key + ": " + str(post[key]))
        
    print("\n")
    
def generate_search_list(posts):
    #done
    page_size = 10 
    empty = False
    try:
        items = []
        for _ in range(page_size):
            items.append(posts.pop(0))
    except IndexError:
        empty = True
    if not posts:
        empty = True
    return cli.put_search_list(items, not empty)

