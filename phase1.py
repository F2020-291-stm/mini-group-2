from simplejson import load as j_load
from pymongo import MongoClient
from sys import argv
import re

term_seperators = re.compile(r"\\n|<.*?>|(?:(?<!\w)\w{,2}(?:'\w*)?(?!\w))+|[\(\),.; \"\']+")

def build_collection(db, cname: str, extract_terms = None):
    db.drop_collection(cname)
    collection = db[cname]
    with open(cname + ".json") as file:
        documents = j_load(file)[cname.lower()]['row']
    
    # Extracts terms
    if extract_terms is not None and len(extract_terms) > 0:
        terms = set()
        for document in documents:
            for key in extract_terms:
                if key in document.keys():
                    for item in term_seperators.split(document[key]):
                        terms.update(item.lower())
        terms.discard('')
        document['terms'] = list(terms)

    # TODO build index on 'terms'



    collection.insert_many(documents)

    
        

if __name__ == "__main__":
    if (len(argv) < 2 or not argv[1].isdigit()):
        print("No database port given, exiting...")
        exit()
    client = MongoClient('localhost', int(argv[1]))
    db = client['291db']

    print("Adding posts")
    build_collection(db, 'Posts', ['Title', 'Body'])

    print("Adding tags")
    build_collection(db, 'Tags')

    print("Adding Votes")
    build_collection(db, 'Votes')


    


