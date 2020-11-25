from json import load as j_load
from pymongo import MongoClient, TEXT
from sys import argv
from multiprocessing import Process
import re

term_rule = re.compile(r"(?<!\w)\w{3,20}(?!\w)")
tag_rule = re.compile(r"(?<=<)\w+(?=>)")

def build_collection(cname, port):
    """Builds a database collection based on a json file in the directory

    Args:
        db (pymongo.Database): Mongo database build collection in
        cname (str): Name of file (used as name of database)0
        extract_terms (list(str), optional): Keys to extract terms from. Defaults to None.
    """
    print("Building collection: {}".format(cname))
    db = MongoClient('localhost', port)['291db']
    # Drop any existing collection by the same name
    db.drop_collection(cname)

    # Extract documents from file
    with open(cname + ".json") as file:
        documents = j_load(file)[cname.lower()]['row']
    
    print("Loaded documents from {}\n".format(cname + '.json'))

    # Insert the documents normally
    db[cname].insert_many(documents)
    print("Inserted {} of {} documents into {}\n".format(db[cname].count_documents({}), len(documents), cname))


def build_termed_collection(cname, port):
    print("Building collection: {}".format(cname))

    # Extract documents from file
    with open(cname + ".json") as file:
        documents = j_load(file)[cname.lower()]['row']
    
    print("Loaded documents from {}\n".format(cname + '.json'))
    
    db = MongoClient('localhost', port)['291db']

    # Drop any existing collection by the same name
    db.drop_collection(cname)

    for document in documents:
        extract_terms(document)

    print("Creating indexes for {}".format(cname))
    db[cname].create_index([('Terms', 1)])

    print("Inserting documents for {}".format(cname))
    db[cname].insert_many(documents)

    print("Inserted {} of {} documents into {}\n".format(db[cname].count_documents({}), len(documents), cname))

def extract_terms(document):
    """Extracts terms from a document using given keys

    Args:
        document (dict): document to extract terms from

    Returns:
        document (dict): provided document with terms field
    """
    
    terms = set()
    if 'Title' in document.keys():
        terms.update(extract_3plus_letter_words(document['Title']))
    if 'Body' in document.keys():
        terms.update(extract_3plus_letter_words(document['Body']))
    if 'Tags' in document.keys():
        terms.update(extract_tags(document['Tags']))
    document['Terms'] = list(terms)

def extract_tags(text):
    words = set()
    for item in term_rule.finditer(text):
        words.add(item.group(0).lower())
    return words

def extract_3plus_letter_words(text):
    """Extracts all alphanumberic strings of 3 characters or more

    Args:
        text (str): text to extract words from

    Returns:
        set(str): words extracted (lowercase)
    """
    words = set()
    for item in term_rule.finditer(text):
        words.add(item.group(0).lower())
    return words

def build_database(port):
    # Build all collections using threads to reduce time
    processes = []
    processes.append(Process(target=build_termed_collection, args=('Posts', port)))
    processes.append(Process(target=build_collection, args=('Tags', port)))
    processes.append(Process(target=build_collection, args=('Votes', port)))

    # Run all threads then wait for them to complete
    for process in processes:
        process.start()

    for process in processes:
        process.join()
    
    print("Database is built")

if __name__ == "__main__":
    if len(argv) < 2 or not argv[1].isdigit():
        print("No valid database port given, exiting...")
        exit()
    
    build_database(int(argv[1]))


    


