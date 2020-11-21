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
        #TODO Retrieve all answers that answer pid
        pass

    def get_post(self, pid):
        #TODO Retrieve the post that has pid
        pass

    def get_user_posts(self, uid):
        #TODO Retrieve all posts from this uid
        #Split into two lists: questions and answers
        pass

    def tag_updater(self, tags):
        #given a list of tags, check if that tag is in the database
        #if it is, then increase the count by 1,  
        #otherwise add it to the database with a unique, "Id",
        #"TagName" as the tag, and "Count" set to 0

        for tag in tags:
            #TODO check if the tag exists
            exists = False

            if exists:
                #TODO update count by 1
                pass 
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
        dic_vote['VoteTypeId'] = 2
        dic_vote['CreationDate'] = datetime.now()

        self.votes.insert_one(dic_vote)

    def get_user_received_votes(self, uid):
        #TODO given a uid, return the number of votes they have received
        pass


#maybe can combine these three functions
    def pid_generator(self):
        #returns a unique post Id
        #idea: find max post Id and + 1
        pass

    def tid_generator(self):
        #returns a unique tag ID
        #idea: find max tid Id and + 1
        pass

    def vid_generator(self):
        #returns a unique vote Id
        #idea: find max vid Id and + 1
        pass
