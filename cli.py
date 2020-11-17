from PyInquirer import prompt, Separator

#template forms that will be repeatedly used
#   type determines the type of input that it expects the user to perform
#   i.e. 'input' expects text while 'confirm' expect y/n
#   name is the key for the value that the user enters
#   message is the prompt that the form gives the user

_LOGIN_FORM = [
    {
        'type': 'input',
        'name': 'id',
        'message': 'User Id (leave blank to use as anonymous):',
        'validate': lambda x : x.isdigit() or x == ''
    }
]

_MASTER_MENU =[
    {
        'type' : 'list',
        'name' : 'action',
        'message' : 'What do you want to do?',
        'choices': [
            'Post a question',
            'Search for questions',
            'Quit'
        ]
    }
]

_POST_FORM = [
    {
        'type' : 'input',
        'name' : 'title',
        'message' : 'title'
    },    
    {
        'type' : 'input',
        'name' : 'body',
        'message' : 'body'
    },
    {
        'type' : 'input',
        'name' : 'tags',
        'message' : 'Enter tags seperated by \';\'\n'
    }
]

_SEARCH_FORM = [
    {
        'type' : 'input',
        'name' : 'keywords',
        'message' : 'Enter Search Keywords seperated by \';\'\n'
    }
]

_SELECT_FORM = [
    {
        'type' : 'list',
        'name' : 'post',
        'message' : 'Select a post',
        'choices' : []
    }
]

_ACTION_MENU = [
    {
        'type' : 'list',
        'name' : 'action',
        'message' : 'What do you want to do?',
        'choices': []
    }
]

def login():
    """Prompts user for a username and password.

    Returns:
        Tuple of strings: Username and password
    """
    return prompt(_LOGIN_FORM)['id']

def master_menu_select():
    """User is prompted to select from the master menu: post, search, logout, or quit.

    Returns:
        String: Returns the string of the action chosen by the user
    """    
    return prompt(_MASTER_MENU)['action']

def write_post():
    """User is prompted to submit a title and a text body for a post.

    Returns:
        Dictionary: Returns a dictionary containing two strings - title and body
    """    
    #user submits a title and a text body
    return prompt(_POST_FORM)

def get_keyword():
    """Prompts user to submit as many key words as they like. User submits in a specified regular expression.

    Returns:
        Dictionary: Returns a dictionary containing a string of the regular expression containing the keyword(s)
    """    
    return prompt(_SEARCH_FORM)['keywords'].split(';') #will require parsing when accessed

def put_search_list(posts, empty):
    """Shows user the first five posts that match their search. User can select a post or
    (if there are more than 5 results) select to move on to the next page.

    Args:
        posts (list): Contains all posts that match search criteria
        empty (boolean): Is true if we have 5 or less posts that match criteria

    Returns:
        Dictionary: Returns a dictionary containing the post that the user selected
    """
    display = [Separator("{:<5}|{:<10}|{:<30}|{:<40.40}|{:<15}|{:<5}|{:<5}".format('Pid', 'Date', 'Title', 'Body', 'Poster', 'Votes', 'Answers'))]
    for post in posts:
        item = {}
        if post[6] is not None:
            item['name'] = "{:<5}|{:<10}|{:<30}|{:<40.40}|{:<15}|{:<5}|{:<5}".format(post[0], post[1], post[2], post[3], post[4], post[5], post[6])
        else:
            item['name'] = "{:<5}|{:<10}|{:<30}|{:<40.40}|{:<15}|{:<5}".format(post[0], post[1], post[2], post[3], post[4], post[5])
        item['value'] = post[0]
        display.append(item)
    _SELECT_FORM[0]['choices'] = display
    if not empty:
        _SELECT_FORM[0]['choices'].append({'name':'Next Page', 'value': '+'})
    return prompt(_SELECT_FORM)['post']

def action_menu_select(show_question_action):
    """A user is looking at a post. This prompts the user to decide what 
    to do with the post.

    Args:
        show_priviledged_actions (boolean): Is true if the user is privileged
        show_answer_actions ([type]): Is true if the post being viewed is an answer

    Returns:
        Dictionary: Returns a dictionary containing a string of what option was selected
    """    
    # Actions for are dependent on the type of post so we build the choices at runtime
    
    _ACTION_MENU[0]['choices'].append("Vote") # Vote

    if show_question_action:
        # Show any answers if its a post
        _ACTION_MENU[0]['choices'].append('Show answers')

    _ACTION_MENU[0]['choices'].append("Return") # User return to main menu
    
    return prompt(_ACTION_MENU)['action']
