import sqlite3
from datetime import date
from random import randint
import os
import re

def _instr_nocase(X, Y):
    """Sees if one string is inside the other ignoring case

    Args:
        X (str): String to find in Y
        Y (str): String to check in

    Returns:
        boolean: whether or not X is in Y
    """    

    if X is None or Y is None:
        return 0
    if re.search(Y, X, re.IGNORECASE) is not None:
        return 1
    return 0

def _next_lexical_char(character):
    """Gets the next character in lexical order

    Args:
        character (str): char to find next from

    Returns:
        str: next lexical char
    """    
    if '0' <= character < '9':
        return str(int(character) + 1)
    elif character == '9':
        return 'A'
    elif 'A' <= character < 'Z' or 'a' <= character < 'z':
        return chr(ord(character) + 1)
    elif character == 'Z':
        return 'a'
    elif character == 'z':
        return '0'

def _prev_lexical_char(character):
    """Gets the previous character in lexical order

    Args:
        character (str): char to find previous from

    Returns:
        str: previous lexical char
    """  
    if '0' < character <= '9':
        return str(int(character) - 1)
    elif character == '0':
        return 'z'
    elif 'A' < character <= 'Z' or 'a' < character <= 'z':
        return chr(ord(character) - 1)
    elif character == 'A':
        return '9'
    elif character == 'a':
        return 'A'

def _gen_random_char():
    """Generates a random character in range [A-Za-z0-9]

    Returns:
        str: random character
    """  
    value = randint(0, 9 + 2*(ord('Z') - ord('A')))
    if value <= 9:
        return str(value)
    elif 9 < value <= 9 + ord('Z') - ord('A'):
        return chr(value - 9 + ord('A'))
    elif 9 + ord('Z') - ord('A') < value:
        return chr(value - 9 - ord('Z') + ord('A') + ord('a'))


class Database:
    def init_db(self, path):
        """
        Initialize the database connection.

        Args:
            path (string): path that the chosen database lies in
        """
        exists = True
        if not os.path.exists(path):
            exists = False
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.create_function('INSTRNOCASE',2,_instr_nocase)
        self.cursor = self.db.cursor()
        if not exists:
            self.create_db()
    
    def create_db(self):
        """Creates the database.
        """        
        with open('queries/prj-tables.sql') as sql_file:
            sql_as_string = sql_file.read()
            self.cursor.executescript(sql_as_string)

    def open_session(self, username, password):
        """Creates a session for this user.

        Args:
            username (String): A string containing the username
            password (String): A string containing the password

        Returns:
            [UserSesion]: A session containing uid and if the user is privileged or not
        """        
        self.cursor.execute( #finds all users with this username/password, either 0 or 1
            '''
            SELECT *
            FROM users
            WHERE uid = ?
            COLLATE NOCASE
            INTERSECT
            SELECT *
            FROM users
            WHERE pwd = ?
            ''',
            (username, password)
        )
        if self.cursor.fetchone() is not None: #if the user exists then check if the user is privileged
            self.cursor.execute(
            '''
            SELECT *
            FROM privileged
            WHERE uid = ?
            COLLATE NOCASE
            ''',
            (username,)
            )
            session = UserSession(username, privileged = self.cursor.fetchone() is not None) #creates a session for that user
            session._activate()
            return session

    def register(self, username, password, name, city):
        """Enters a user into the database. Initiates a session for this user
        If user already exists, then complains and doesn't allow it. 

        Args:
            username (String): A string containing the username
            password (String): A string containing the password
            name (String): A string containing the name
            city (String): A straining containing the city name

        Returns:
            UserSession: A session for the user created
        """        
        try:
            self.cursor.execute(
                '''
                INSERT INTO users(uid, name, pwd, city, crdate)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (username, name, password, city, date.today())
            )
            session = UserSession(username)
            session._activate()
            return session
        except sqlite3.IntegrityError:
            print("Error: Enter UNIQUE User ID")
    
    def post_questions(self, session, title, body):
        """Creates a post.

        Args:
            session (UserSession): A session for the user logged in
            title (String): Title of the post
            body (String): Body of the post
        """        
        pid = self.generate_pid() #generates a unique pid
        self.cursor.execute( 
            '''
            insert into posts(pid, pdate, title, body, poster)
            values (?,?,?,?,?)
            ''',
            (pid, date.today(), title, body, session.get_uid())
        )
        self.cursor.execute(
            '''
            insert into questions(pid)
            values (?)
            ''', 
            (pid,)
        )

    def get_post(self, pid):
        """Retrieves post with given pid.

        Args:
            pid (String): pid of the wanted post

        Returns:
            [Post]: The wanted post
        """        
        self.cursor.execute(
            '''
            SELECT title, body
            FROM posts
            WHERE pid = ?
            COLLATE NOCASE
            ''',
            (pid,)
        )
        return self.cursor.fetchone()

    def update_post(self, pid, title, body):
        """Given a pid, updates its title and body with given parameters.

        Args:
            pid (String): pid of selected post
            title (String): String containing new title
            body (String): String containing new body
        """        
        self.cursor.execute( #finds pid and updates values
            '''
            UPDATE posts
            SET title = ?, body = ?
            WHERE pid = ? 
            ''',
            (title, body, pid)
        )
    
    def search_posts(self, keyword_list):
        """Searches all posts and returns them

        Args:
            keyword_list (String[]): Given keyword for the search

        Returns:
            String[]: List of posts
        """
        query = "SELECT p.pid AS pid\nFROM(\n"
        first = True
        for index in range(len(keyword_list)):
            keyword = keyword_list[index]
            if not first:
                query += "\nUNION ALL\n"
            else:
                first = False
            query +="SELECT p.pid AS pid\nFROM posts p\nLEFT JOIN tags t\nON p.pid = t.pid \nWHERE (INSTRNOCASE(p.title,'"+ keyword +"') > 0\nOR INSTRNOCASE(p.body,'" + keyword + "') > 0\nOR INSTRNOCASE(t.tag,'" + keyword + "') > 0)"
        query +=") p\nGROUP BY pid\nORDER BY COUNT(*) DESC;"
        self.cursor.execute(query)
        return self.get_post_info(self.cursor.fetchall())
    
    def get_post_info(self, posts):
        if posts is None or not posts:
            return None
        query = ""
        for index in range(len(posts)):
            query += "SELECT *," + str(index) + " AS filter FROM posts WHERE pid ='" + posts[index][0] + "'"
            if index != len(posts)-1:
                query += "\nUNION ALL\n"
        query+="\nORDER BY filter"
        with open('queries/search_posts.sql') as sql_file:
            sql_as_string = sql_file.read()
            sql_as_string = sql_as_string.replace('<placeholder>', query, 1)
        self.cursor.execute(sql_as_string)
        return self.cursor.fetchall()

    def post_answer(self, session, title, body, qid):
        """Creates a post and assigns it as an answer to a chosen question.

        Args:
            session (UserSession): Relevantly, uid of answerer
            title (String): Title of answer
            body (String): Body of answer
            qid (String): pid of question being answered
        """        
        #creates a post and adds it to the posts and answers tables
        pid = self.generate_pid() #generates unique pid for new answer
        self.cursor.execute( #creates post
            '''
            INSERT INTO posts(pid, pdate, title, body, poster)
            VALUES (?,?,?,?,?)
            ''',
            (pid, date.today(), title, body, session.get_uid())
        )
        self.cursor.execute( #assigns it as an answer to qid
            '''
            INSERT INTO answers(pid, qid)
            VALUES (?,?)
            ''',
            (pid, qid)
        )
    
    def vote_post(self, session, pid):
        """Upvotes a selected post.

        Args:
            session (UserSession): Relevantly, uid of voter
            pid (String): pid of post being voted on

        Returns:
            Boolean: Returns 0 upon successful vote, 1 if user has already cast a vote on that post
        """        
        self.cursor.execute( #finds all votes on pid made by user of the session
            '''
            SELECT *
            FROM votes
            WHERE pid = ?
            AND uid = ?
            COLLATE NOCASE
            ''',
            (pid, session.get_uid())
        )
        if self.cursor.fetchone() is None:
            #if there are none, that means this user has not voted
            #on this post yet, which means they now can
            self.cursor.execute(
                '''
                SELECT max(vno)
                FROM votes   
                '''
            )
            #set vno of this new vote to the biggest vno+1
            vno = 0
            max_vno = self.cursor.fetchone()[0]
            if max_vno is not None:
                vno = max_vno + 1
            #and now apply this vote to the database          
            self.cursor.execute(
                '''
                INSERT INTO votes(pid, vno, vdate, uid)
                VALUES (?,?,?,?)
                ''',
                (pid, vno, date.today(), session.get_uid())
            )
            return True #upon successful vote
        else:
            return False #upon unsuccessful vote
    
    def mark_accepted_answer(self, aid, force=False):
        """Marks an answer as the accepted answer to a post. User
        can choose if they'd like to override any current accepted answers
        with this one.

        Args:
            aid (String): pid of answer being chosen as the accepted answer
            force (bool, optional): True if user wants to override any current accepted answers.
                Defaults to False.

        Returns:
            Boolean: Returns true if post was assigned as accepted answer, false if it wasn't
        """        
        self.cursor.execute( #finds the question and checks if it is already answered
            '''
            SELECT *
            FROM questions q, answers a
            WHERE a.pid = ?
            AND q.pid = a.qid
            AND q.theaid IS NOT NULL
            ''',
            (aid,)
        )
        if (not force and self.cursor.fetchone() is not None):
            #if the question already has a "the answer", then this answer cannot become
            #the accepted answer, so return false. This step is overriden if force is set to true
            return False
        #otherwise, set this answer to be "the answer"
        self.cursor.execute(
            '''
            UPDATE questions
            SET theaid = ?
            WHERE pid IN (
                SELECT qid
                FROM answers a
                WHERE a.pid = ?
            )
            ''',
            (aid, aid)
        )
        return True #return true to signify that it went through
    
    def get_badge_list(self):
        """Finds the name of all badges.

        Returns:
            List: list of all badge names
        """        
        #returns list of all badge names
        self.cursor.execute(
            '''
            SELECT bname
            FROM badges
            '''
        )
        badges = []
        for entry in self.cursor.fetchall():
            badges.append(entry[0])
        return badges

    def give_badge(self, pid, bname):
        """Gives a chosen badge to the poster of a post.

        Args:
            pid (String): pid of chosen post
            bname (String): name of chosen badge
        """        
        self.cursor.execute( #gets uid of poster
            '''
            Select poster
            From posts
            Where pid = ?
            ''',
            (pid,)
        )
        uid = self.cursor.fetchone()[0]

        #gives badge bname to user uid, right now
        try:
            if (uid is not None):
                self.cursor.execute(
                    '''
                    INSERT INTO ubadges
                    VALUES (?, ?, ?)
                    ''',
                    (uid, date.today(), bname)
                )
        except sqlite3.IntegrityError:
            pass # Ignore because that just means the same badge has already been given today

    def add_tag(self, pid, tag):
        """Adds a tag to a specified post. If post already has that tag, then
        don't add it again.

        Args:
            pid (String): pid of select posted
            tag (String): string containing the chosen tag

        Returns:
            Boolean: Return 0 to signify a successful addition of a tag, 1 otherwise
        """        
        self.cursor.execute( #checks if this tag is already applied to pid
            '''
            SELECT *
            FROM tags
            WHERE tag = ?
            COLLATE NOCASE
            ''',
            (tag,)
        )
        if (self.cursor.fetchone() is None):
            #if it hasn't been tagged with this tag, then tag it
            self.cursor.execute(
                '''
                INSERT INTO tags
                VALUES (?, ?)
                ''',
                (pid, tag)
            )

    
    def generate_pid(self):
        """Gerenerates a unique pid

        Returns:
            String: The generated pid
        """
        # Get maximum and minimum pids
        self.cursor.execute(
            '''
            SELECT MAX(pid)
            FROM posts
            '''
        )
        max_pid = self.cursor.fetchone()[0]
        if max_pid is None:
            max_pid = str(0)

        self.cursor.execute(
            '''
            SELECT MIN(pid)
            FROM posts
            '''
        )
        min_pid = self.cursor.fetchone()[0]
        if min_pid is None:
            min_pid = max_pid
        
        # If we haven't reached the max value increment
        if max_pid != 'zzzz':
            pid = max_pid
            next_char = '0'
            i = 0
            while next_char == '0' and i < 4:
                next_char = _next_lexical_char(pid[i])
                pid = pid[0:i] + next_char + pid[i + 1:]
                i = i + 1
        # If we haven't reached the min value decriment
        elif min_pid != '0':
            pid = min_pid
            next_char = 'z'
            i = len(pid) - 1
            while next_char == 'z' and i >= 0:
                next_char = _prev_lexical_char(pid[i])
                pid = pid[0:i] + next_char + pid[i + 1:]
                i = i - 1
        else:
            # We have no idea what values are free and what ones aren't
            # Probably our best option would be to have a set of all possible PIDs
            # and what ones are used and subtract one from the other to figure
            # out what values are available, but that could take a while so..... randomness it is
            pid = [None] * 4
            unique = False
            while (not unique):
                pid[0] = _gen_random_char()
                pid[1] = _gen_random_char()
                pid[2] = _gen_random_char()
                pid[3] = _gen_random_char()
                pid = "".join(pid)
                self.cursor.execute(
                    '''
                    SELECT *
                    FROM posts
                    WHERE pid = ?
                    ''',
                    (pid,)
                )
                if self.cursor.fetchone() is None:
                    unique = True

        return pid
    
    def is_answer(self, pid):
        """Given a pid, checks if it is an answer (as opposed to a question)

        Args:
            pid (String): pid of potential answer

        Returns:
            Boolean: Return True if it is an answer, False otherwise
        """        
        self.cursor.execute(
            '''
            SELECT *
            FROM answers
            WHERE pid = ?
            ''',
            (pid,)
        )
        if self.cursor.fetchone() is not None:
            return True
        return False

class UserSession:
    """Used to keep track of which user is logged in such that their actions
    Can be attributed to their uid
    """    

    def __init__(self, uid, privileged = False):
        #uid is the user id of the user that this session corresponds to
        #Once a session has began, main.py will repeatedly allow the user
        #   to select options from a menu until they logout. Active determines
        #   whether a user is logged our or not
        #privileged sessions have more options available to them for 
        #   interacting with other user's posts
        self.uid = uid
        self.active = False
        self.privileged = privileged

    def _activate(self):
        self.active = True

    def logout(self):
        self.active = False

    def is_active(self):
        return self.active

    def is_privileged(self):
        return self.privileged

    def get_uid(self):
        return self.uid

