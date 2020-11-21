from simplejson import load as j_load
from pymongo import MongoClient, TEXT
from sys import argv
import re

term_rule = re.compile(r"(?<!\w)\w{3,}(?=\W)")

# Old split regex: [^\w<]*(?:<[^>]*>|(?<!\w)\w{,2}[^\w .,;:\"<]+\w*)|\W+

def build_collection(db, cname, extract_keys = None):
    """Builds a database collection based on a json file in the directory

    Args:
        db (pymongo.Database): Mongo database build collection in
        cname (str): Name of file (used as name of database)
        extract_terms (list(str), optional): Keys to extract terms from. Defaults to None.
    """
    print("Building collection: {}".format(cname))
    # Drop any existing collection by the same name
    db.drop_collection(cname)

    # Extract documents from file
    with open(cname + ".json") as file:
        documents = j_load(file)[cname.lower()]['row']
    
    # Extract terms from any provided keys and create an index
    if extract_keys is not None and len(extract_keys) > 0:
        db[cname].create_index([('terms', TEXT)])
        for document in documents:
            document['terms'] = extract_terms(document, extract_keys)

    # Insert the documents
    db[cname].insert_many(documents)
    print("Inserted {} documents into {}\n".format(db[cname].count_documents({}), cname))

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
        words.add(item[0].lower())
    return words

if __name__ == "__main__":
    # Get port number
    if (len(argv) < 2 or not argv[1].isdigit()):
        print("No valid database port given, exiting...")
        exit()

    # Connect to database
    client = MongoClient('localhost', int(argv[1]))
    db = client['291db']
    
    # Build all collections
    build_collection(db, 'Posts', ['Title', 'Body'])
    build_collection(db, 'Tags')
    build_collection(db, 'Votes')


    


