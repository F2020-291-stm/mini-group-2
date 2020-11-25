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
        self.uid = None

    def use_uid(self, uid):
        self.uid = uid

    def build_post(self, data):
        post = {}
        post["Id"] = self.id_generator(self.posts)
        post["CreationDate"] = datetime.now()
        post["ContentLicense"] = "CC BY-SA 2.5"
        if self.uid is not None:
            post["OwnerUserId"] = self.uid

        post["Body"] = "<p>" + data["body"] + "</p>\n"
        post["Score"] = 0

        return post
    
    def post_question(self, data):
        post = self.build_post(data)
        post["Title"] = data["title"]
        if len(data['tags']) > 0:
            post["Tags"] = "<" + "><".join(data["tags"]) + ">"
        post["PostTypeId"] = '1'
        self.posts.insert_one(post)

    def post_answer(self, data):
        post = self.build_post(data)
        post["PostTypeId"] = '2'
        post["ParentId"] = data['qid']
        self.posts.insert_one(post)

    def find_questions(self, keywords_list):
        """searches the collection using given keywords

        Args:
            keywords_list (list): contains the keywords to search with

        Returns:
            list: list of cursors containing the results of the search
        """
        criteria = []
        for keyword in keywords_list:
            if (len(keyword) > 2):
                criteria.append({'Terms': keyword.lower()})
            else:
                criteria.extend([
                    {'Tags': {"$regex": '<{}>'.format(keyword),
                              "$options" :'i'}},
                    {'Title': {"$regex": '\b{}\b'.format(keyword),
                              "$options" :'i'}},
                    {'Body': {"$regex": '\b{}\b'.format(keyword),
                              "$options" :'i'}},
                ])
        questions = self.posts.find({
            '$or': criteria,
            'PostTypeId': '1'
        })
        return list(questions)

    def find_answers(self, pid):
        return self.posts.find({'ParentId': pid})

    def get_post(self, pid):
        """Retrieve a post that has given pid

        Args:
            pid (str): contains the post id

        Returns:
            Cursor object: returns tyhe post as a cursor object
        """
        return self.posts.find_one_and_update({'Id':pid}, {'$inc': {'ViewCount':1}})

    def get_user_report(self, uid):
        """Retrieve all posts made by user uid

        Args:
            uid (str): contains the post id

        Returns:
            [list]: a list of Cursor objects 
        """
        report = {'qcount': 0, 'qavg': 0, 'acount': 0, 'aavg': 0, 'vcount': 0}
        for question_report in self.posts.aggregate(
            [
                {'$match': {'OwnerUserId':uid, 'PostTypeId':'1'}},
                {
                    '$group': {
                        '_id': None,
                        'count': {'$sum': 1},
                        'avg': {'$avg': '$Score'}
                    }
                }
            ]
        ):
            report['qcount'] = question_report['count']
            report['qavg'] = question_report['avg']
            break
        
        for answer_report in self.posts.aggregate(
            [
                {'$match': {'OwnerUserId':uid, 'PostTypeId':'2'}},
                {
                    '$group': {
                        '_id': None,
                        'count': {'$sum': 1},
                        'avg': {'$avg': '$Score'}
                    }
                }
            ]
        ):
            report['acount'] = answer_report['count']
            report['aavg'] = answer_report['avg']
            break

        for vote_report in self.votes.aggregate(
            [
                {'$match':{'UserId':uid}},
                {'$count': 'count'}
            ]
        ):
            report['vcount'] = vote_report['count']
            break

        return report

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
                self.tags.update_one({'TagName': tag}, {'$set': {'Count': tag['Count']+1}}) 
            else:
                #insert new tag
                Id = self.id_generator(self.tags)
                self.tags.insert_one({"Id":Id, "TagName":tag, "Count":0})

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
                {'$replaceWith': {'$toInt': '$Id'}},
                {
                    '$group': {
                        "_id": None,
                        "max_id": {'$max':  '$Id'}
                    }
                }
            ]
        )

        for id in max_id:
            return str(max_id+1)