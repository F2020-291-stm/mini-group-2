import cli

def user_report(database, uid):
    #done
    print("\nUser Report")
    print("User: " + str(uid))
    posts = database.get_user_posts(uid) #fetches the posts posted by this user
    num_votes = 0
    num_questions = 0
    num_answers = 0
    q_avg_score = 0
    a_avg_score = 0

    #calculates above four values by going through each user's posts and counting
    for post in posts:
        if post['PostTypeId'] == "1": #is a question
            num_questions += 1
            q_avg_score += post['Score']
        else:
            num_answers += 1
            a_avg_score += post['Score']

    #in case of division by 0
    if num_questions > 0:
        q_avg_score = q_avg_score/num_questions
    else:
        q_avg_score = 0
    if num_answers > 0:
        a_avg_score = a_avg_score/num_answers
    else:
        a_avg_score = 0

    print("Questions Posted: " + str(num_questions))
    print("Question Average Score: " + str(q_avg_score))
    print("Answers Posted: " + str(num_answers))
    print("Answer Average Score: " + str(a_avg_score))
    print("Votes Received: " + str(num_votes) + "\n")    

def write_post(database, uid, type_of_post, qid = None):
    #done
    print("\nEnter your " + type_of_post)
    post = cli.write_post()
    print("")

    tags = [string.strip() for string in post["tags"].split(';')] #converts given string into a list of tags
    post["tags"] = tags
    if type_of_post == "question":
        post["type"] = "1"
    else:
        post["type"] = "2"
        post['qid'] = str(qid)
    post["uid"] = str(uid)

    database.create_post(post)    

def search_and_act(database, uid):
    #done
    keywords = cli.get_keyword() #asks for keywords to base search off of
    keywords_list  = [string.strip() for string in keywords]

    questions_found = database.search(keywords_list)
    questions_found = ['remove this later']

    if questions_found is None:
        print('No matches found')
    else:
        q_found_list = []
        for question in questions_found:
            q_found_list.append(question)
        q_found_list = [{"Id": "5", "Title": "question_title", "CreationDate": "now", "Score": 10, "AnswerCount": 5, "PostTypeId": "1"}] #remove this later

        while True:
            qid = generate_search_list(q_found_list)
            if qid != '+':
                break

        action_menu(database, uid, qid) 

def action_menu(database, uid, pid, is_question=True):
    #done
    display_post(database, pid)

    response = cli.action_menu_select(is_question)
    if response == 'Answer question':
        write_post(database, uid, "answer", pid)

    elif response == 'List answers':
        answers_found = database.find_answers(pid)

        if answers_found is None:
            print('This question has no answers')
        else:
            a_found_list = []
            for answer in answers_found:
                a_found_list.append(answer)

            while True:
                aid = generate_search_list(a_found_list)
                if aid != '+':
                    break

            action_menu(database, uid, aid, False)

    elif response == 'Upvote':
        database.up_vote(database, uid, pid)
        print("You upvoted this post!\n")

def display_post(database, pid):
    #done
    post = database.get_post(pid)

    print("\nShowing Post:")
    for key in post:
        print(key + ": " + str(post[key]))

    print('')
    
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

    if items[0]['PostTypeId'] == '1':
        return cli.put_q_search_list(items, not empty)
    else:
        return cli.put_a_search_list(items, not empty)

