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

_Q_POST_FORM = [
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

_A_POST_FORM = [ 
    {
        'type' : 'input',
        'name' : 'body',
        'message' : 'body'
    },
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

def write_post(type_of_post):
    """User is prompted to submit a title, a text body, and tags for a post.

    Returns:
        Dictionary: Returns a dictionary containing three strings - title, body, and tags
    """    
    #user submits a title, text body, and tag for a question
    #and just a text body for an answer
    if type_of_post == 'question':
        return prompt(_Q_POST_FORM)
    else:
        return prompt(_A_POST_FORM)

def get_keyword():
    """Prompts user to submit as many key words as they like. User submits in a specified regular expression.

    Returns:
        Dictionary: Returns a dictionary containing a string of the regular expression containing the keyword(s)
    """    
    return prompt(_SEARCH_FORM)['keywords'].split(';') #will require parsing when accessed

def put_q_search_list(posts, more):
    display = [Separator("{:<80}|{:<30}|{:<8}|{:<8}".format('Title', 'Date', 'Score', 'Answers'))]
    for post in posts:
        item = {}

        title = post['Title']
        if len(title) > 80:
            title = title[:79]

        item['name'] = "{:<80}|{:<30}|{:<8}|{:<8}".format(title, str(post['CreationDate']), post['Score'], post['AnswerCount'])
        item['value'] = post['Id']
        display.append(item)
    _SELECT_FORM[0]['choices'] = display
    if more:
        _SELECT_FORM[0]['choices'].append({'name':'Next Page', 'value': '+'})
    return prompt(_SELECT_FORM)['post']

def put_a_search_list(posts, more):
    display = [Separator("{:<2}|{:<30}|{:<8}|{:<80}".format('  ', 'Date', 'Score', 'Body'))]
    for post in posts:
        item = {}

        if 'is_acc_ans' in post.keys():
            buffer = '* '
        else:
            buffer = '  '

        body = post['Body']
        if len(body) > 80:
            body = body[:79]

        item['name'] = "{:<2}|{:<30}|{:<8}|{:<80}".format(buffer, str(post['CreationDate']), post['Score'], body)
        item['value'] = post['Id']
        display.append(item)
    _SELECT_FORM[0]['choices'] = display
    if more:
        _SELECT_FORM[0]['choices'].append({'name':'Next Page', 'value': '+'})
    return prompt(_SELECT_FORM)['post']

def action_menu_select(is_question):
    _ACTION_MENU[0]['choices'] = []

    if is_question:
        _ACTION_MENU[0]['choices'].extend(
            [
                'Answer question',
                'List answers'
            ]
        )
    _ACTION_MENU[0]['choices'].extend(
            [
                'Upvote',
                'Return'
            ]
        )

    return prompt(_ACTION_MENU)['action']

