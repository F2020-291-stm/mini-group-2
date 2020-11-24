from pymongo import MongoClient
from datetime import datetime
import time
import re

client = MongoClient()
db = client['291db']

class Database:

    def __init__(self, port):
        """
        represents a database and related functionality 
        """
        self.db = MongoClient('localhost', port)['291db']
        self.posts = db["Posts"]
        self.votes = db["Votes"]
        self.tags = db["Tags"]

    def use_uid(self, uid):
        self.uid = uid

    def build_post(self, post):
        dic_post = {}
        dic_post["Id"] = self.id_generator(self.posts)
        dic_post["CreationDate"] = datetime.now()
        dic_post["ContentLicense"] = "CC BY-SA 2.5"
        if self.uid is not None:
            dic_post["OwnerUserId"] = uid

        dic_post["Body"] = "<p>" + post["body"] + "</p>\n"
        dic_post["Title"] = post["title"]
        if len(post['tags']) > 0:
            dic_post["Tags"] = "<" + "><".join(post["tags"]) + ">"
        
        return dic_post

    # Depricated (pls remove)
    def create_post(self, post):
        """creates a post and inserts into the given dictionary

        Args:
            post (post): A dictionary containing all the posts
        """
        dic_post = {}
        dic_post["Id"] = self.id_generator(self.posts)
        dic_post["PostTypeId"] = post["type"]
        if post["type"] == "2":
            dic_post["ParentId"] = post['qid']
        dic_post["CreationDate"] = datetime.now()
        dic_post["ContentLicense"] = "CC BY-SA 2.5"
        if self.uid is not None:
            dic_post["OwnerUserId"] = uid

        dic_post["Body"] = "<p>" + post["body"] + "</p>\n"
        dic_post["Title"] = post["title"]
        if len(post['tags']) > 0:
            dic_post["Tags"] = "<" + "><".join(post["tags"]) + ">"

        self.posts.insert_one(dic_post)
    
    def post_question(self, post):
        # TODO
        dic_post["PostTypeId"] = '2'

    def post_answer(self, post):
        # TODO
        dic_post["PostTypeId"] = '1'


    def search(self, keywords_list):
        """searches the collection using given keywords

        Args:
            keywords_list (list): contains the keywords to search with

        Returns:
            list: list of cursors containing the results of the search
        """
        matching_questions = []
        for keyword in keywords_list:
            if len(keyword) >= 3:
                questions = self.posts.find({'$text': {'$search': keyword}, 'PostTypeId': '1'})
            else:
                regular_exp = re.compile('\\b' + keyword + '\\b', re.IGNORECASE)
                questions = self.posts.find({
                    '$or': [
                        {'Title' : regular_exp},
                        {'Body' : regular_exp},
                        {'Tags' : regular_exp}
                    ],
                    'PostTypeId': '1'
                })
            for question in questions:
                matching_questions.append(question)
        print(len(matching_questions))
        res = []
        [res.append(x) for x in matching_questions if x not in res]
        return res

    def find_answers(self, pid):
        #Retrieve all answers that answer pid
        #How?
        #Find all posts whose 'ParentId' is pid
        return self.posts.find({'ParentId': pid})

    def get_post(self, pid):
        """Retrieve a post that has given pid

        Args:
            pid (str): contains the post id

        Returns:
            Cursor object: returns tyhe post as a cursor object
        """
        return self.posts.find_one({'Id':pid})

    def get_user_posts(self, uid):
        """Retrieve all posts made by user uid

        Args:
            uid (str): contains the post id

        Returns:
            [list]: a list of Cursor objects 
        """
        
        return self.posts.find({'Id':uid})

    def tag_updater(self, tags):
        """given a list of tags, check if that tag is in the database 
        if it is, then increase the count by 1,  
        otherwise add it to the database with a unique, "Id",
        "TagName" as the tag, and "Count" set to 0

        Args:
            tags (list): holds the tags to
        """
        for tag in tags:
            #check if the tag exists
            exists = False
            tag = self.tags.find_one({'TagName': tag})
            if tag is not None:
                exists = True
                count = tag['Count']

            if exists:
                #update count by 1
                self.tags.update_one({'TagName': tag}, {'$set': {'Count':(count+1)}}) 
            else:
                #insert new tag
                Id = self.id_generator(self.tags)
                dic_tag = {"Id":Id, "TagName":tag, "Count":0}
                self.tags.insert_one(dic_tag)

    def up_vote(self, database, uid, pid):
        """
        upvotes a post given uid and pid
        Args:
            database ([type]): [description]
            uid (str): holds the user id
            pid (str): holds the post id

        Returns:
            [int]: return 0 to flag if already voted
        """
        votes = self.votes.find({'UserId': uid})
        for vote in votes:
            if vote['PostId'] == pid:
                print("Already voted on this post!\n")
                return 0

        post = self.get_post(pid)
        score = post['Score']
        self.posts.update_one({'Id': pid}, {'$set': {'Score': (score+1)}})
        dic_vote = {}
        dic_vote['Id'] = self.id_generator(self.votes)
        dic_vote['PostId'] = pid
        dic_vote['VoteTypeId'] = "2"
        dic_vote['CreationDate'] = datetime.now()
        if uid != "":
            dic_vote["UserId"] = uid
        self.votes.insert_one(dic_vote)

    def up_view(self, pid):
        """increases the viewcount

        Args:
            pid (str): the id of post that is viewed
        """
        post = self.get_post(pid)
        views = post['ViewCount']
        self.posts.update_one({'Id': pid}, {'$set': {'ViewCount':(views+1)}})

    def get_user_received_votes(self, uid):
        """
        Find all posts made by uid, 
        Find all votes made on each of those posts
        Count all those votes

        Args:
            uid (str): contains the user id to check

        Returns:
            int: contains the number of votes received
        """
        count = 0
        posts = self.get_user_posts(uid)
        for post in posts:
            count += self.votes.find({'PostId':post['Id']}).count()
        return count

    def id_generator(self, collection):
        """generates an unique id for each collection

        Args:
            collection (str): contains the name of the collection

        Returns:
            str: contains the generated id
        """
        max_id = collection.aggregate(
            [
                {
                    '$group':
                        {
                            "max_id": {
                                '$max': '$Id'
                            }
                        }
                }
            ]
        )['max_id']

        return str(int(max_id)+1)