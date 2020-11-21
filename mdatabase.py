from pymongo import MongoClient
from datetime import datetime

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
        dic_post["Id"] = self.pid_generator()
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
        pass

    def find_answers(self, pid):
        #Retrieve all answers that answer pid
        #How?
        #Find all posts whose 'ParentId' is pid
        return self.posts.find({'ParentId':pid})

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
            tags = self.tags.find({'TagName': tag})
            for tag in tags:
                exists = True
                count = tag['Count']

            if exists:
                #update count by 1
                self.tags.update_one({'TagName': tag}, {'$set': {'Count':(count+1)}}) 
            else:
                #insert new tag
                Id = self.tid_generator()
                dic_tag = {"Id":Id, "TagName":tag, "Count":0}
                self.tags.insert_one(dic_tag)

    def up_vote(self, database, uid, pid):
        post = self.get_post(pid)
        dic_vote = {}
        dic_vote['Id'] = self.vid_generator()
        dic_vote['PostId'] = pid
        dic_vote['VoteTypeId'] = "2"
        dic_vote['CreationDate'] = datetime.now()

        self.votes.insert_one(dic_vote)

    def get_user_received_votes(self, uid):
        #Find all posts made by uid, 
        #Find all votes made on each of those posts
        #Count all those votes
        count = 0

        posts = self.get_user_posts(uid)
        for post in posts:
            count += self.votes.find({'PostId':post['Id']}).count()

        return count

    def pid_generator(self):
        obj = self.posts.find().sort('Id',-1).limit(1)
        for post in obj:
            return str(int(post['Id'])+1)

    def tid_generator(self):
        obj = self.tags.find().sort('Id',-1).limit(1)
        for tag in obj:
            return str(int(tag['Id'])+1)

    def vid_generator(self):
        obj = self.votes.find().sort('Id',-1).limit(1)
        for vote in obj:
            return str(int(vote['Id'])+1)
