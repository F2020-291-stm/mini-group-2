from simplejson import load as j_load
from pymongo import MongoClient, TEXT
from sys import argv
import re

term_rule = re.compile(r"\w{3,}|\w{2,}'\w+")
html_tag_rule = re.compile(r"<.*?>")

# Old split regex: \\n|[^\w<]*(?:<[^>]*>|(?<![\w'])\w{1,2}(?:[^\w\s.,;:'\"<]+\w*)*[\s.,;:\"<])|\W+

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
        db[cname].create_index([('Terms', TEXT)])
        for document in documents:
            document['Terms'] = extract_terms(document, extract_keys)

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
    clean_text = html_tag_rule.sub(' ', text)
    for item in term_rule.finditer(clean_text):
        words.add(item[0].lower())
    return words

def build_database(port):
    # Connect to database
    client = MongoClient('localhost', int(argv[1]))
    db = client['291db']
    
    # Build all collections
    build_collection(db, 'Posts', ['Title', 'Body'])
    build_collection(db, 'Tags')
    build_collection(db, 'Votes')

if __name__ == "__main__":
    if len(argv) < 2 or not argv[1].isdigit():
        print("No valid database port given, exiting...")
        exit()

    build_database(int(argv[1]))


    


