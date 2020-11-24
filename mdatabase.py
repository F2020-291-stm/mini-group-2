from pymongo import MongoClient
from datetime import datetime
import time
import re

client = MongoClient()
db = client['291db']

class Database:
    def __init__(self, db):
        self.db = db
        self.posts = db["Posts"]
        self.votes = db["Votes"]
        self.tags = db["Tags"]

    def create_post(self, post):
        #done
        #post given has 5 attributes: uid, title, body, tags, and type
        dic_post = {}
        dic_post["Id"] = self.id_generator(self.posts)
        dic_post["PostTypeId"] = post["type"]
        if post["type"] == "2":
            dic_post["ParentId"] = post['qid']
        dic_post["CreationDate"] = datetime.now()
        for attribute in ["Score", "ViewCount", "AnswerCount", "CommentCount", "FavoriteCount"]:
            dic_post[attribute] = 0
        dic_post["ContentLicense"] = "CC BY-SA 2.5"
        if post["uid"] != "":
            dic_post["OwnerUserId"] = post["uid"]

        dic_post["Body"] = "<p>" + post["body"] + "</p>\n"
        dic_post["Title"] = post["title"]
        dic_post["Tags"] = "<" + "><".join(post["tags"]) + ">"

        self.posts.insert_one(dic_post)

    def search(self, keywords_list):
        #TODO Retrieve all questions that match keywords in body, title, or tags
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
        #Retrieve the post that has pid
        return self.posts.find_one({'Id':pid})

    def get_user_posts(self, uid):
        #Retrieve all posts made by user uid
        return self.posts.find({'Id':uid})

    def tag_updater(self, tags):
        #given a list of tags, check if that tag is in the database
        #if it is, then increase the count by 1,  
        #otherwise add it to the database with a unique, "Id",
        #"TagName" as the tag, and "Count" set to 0

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
        post = self.get_post(pid)
        views = post['ViewCount']
        self.posts.update_one({'Id': pid}, {'$set': {'ViewCount':(views+1)}})

    def get_user_received_votes(self, uid):
        #Find all posts made by uid, 
        #Find all votes made on each of those posts
        #Count all those votes
        count = 0

        posts = self.get_user_posts(uid)
        for post in posts:
            count += self.votes.find({'PostId':post['Id']}).count()

        return count

    def id_generator(self, collection):
        if collection is self.posts:
            objs = self.posts.find({},{'Id':1})
        elif collection is self.tags:
            objs = self.tags.find({},{'Id':1})
        elif collection is self.votes:
            objs = self.votes.find({},{'Id':1})

        max_id = 0
        for obj in objs:
            Id = obj['Id']
            if Id is not None:
                Id = int(Id)
                if Id > max_id:
                    max_id = Id

        return str(max_id+1)
