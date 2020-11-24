from json import load as j_load
from pymongo import MongoClient, TEXT
from sys import argv
from multiprocessing import Process
import re

term_rule = re.compile(r"\w{3,}|\w{2,}'\w+")
html_tag_rule = re.compile(r"<.*?>")

# Old split regex: \\n|[^\w<]*(?:<[^>]*>|(?<![\w'])\w{1,2}(?:[^\w\s.,;:'\"<]+\w*)*[\s.,;:\"<])|\W+

def build_collection(port, cname, extract_keys = None):
    """Builds a database collection based on a json file in the directory

    Args:
        db (pymongo.Database): Mongo database build collection in
        cname (str): Name of file (used as name of database)
        extract_terms (list(str), optional): Keys to extract terms from. Defaults to None.
    """
    print("Building collection: {}".format(cname))
    db = MongoClient('localhost', port)['291db']
    # Drop any existing collection by the same name
    db.drop_collection(cname)

    # Extract documents from file
    with open(cname + ".json") as file:
        documents = j_load(file)[cname.lower()]['row']
    
    # Extract terms from any provided keys and create an index
    if extract_keys is not None and len(extract_keys) > 0:
        db[cname].create_index([('Terms', TEXT)])

        SIZE_FACTOR = 100000
        i = 1
        processes = []

        # Divide and conquer
        while i*SIZE_FACTOR < len(documents):
            processes.append(Process(target=extract_terms_batch,
                args=(documents, extract_keys, (i-1)*SIZE_FACTOR, i*SIZE_FACTOR)))
            processes[-1].start()
            i = i + 1

        processes.append(Process(target=extract_terms_batch,
            args=(documents, extract_keys, (i-1)*SIZE_FACTOR)))
        processes[-1].start()
        
        for p in processes:
            p.join()

    # Insert the documents normally
    db[cname].insert_many(documents)
    print("Inserted {} documents into {}\n".format(db[cname].count_documents({}), cname))

def extract_terms_batch(documents, keys, start=0, finish=-1):
    if (finish > -1):
        for document in documents[start:finish]:
            document['Terms'] = extract_terms(document, keys)
    else: 
        for document in documents[start:]:
            document['Terms'] = extract_terms(document, keys)

def extract_terms(document, keys):
    """Extracts terms from a document using given keys

    Args:
        document (dict): document to extract terms from
        keys (list(str)): keys for values to extract terms from

    Returns:
        list(str): terms extracted
    """
    terms = set()
    for key in keys:
        if key in document.keys():
            terms.update(extract_3plus_letter_words(document[key]))
    return list(terms)

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
    # Connect to database
    
    # Build all collections using threads to reduce time
    processes = []
    processes.append(Process(target=build_collection, args=(int(argv[1]), 'Posts', ['Title', 'Body'])))
    processes.append(Process(target=build_collection, args=(int(argv[1]), 'Tags')))
    processes.append(Process(target=build_collection, args=(int(argv[1]), 'Votes')))

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


    


