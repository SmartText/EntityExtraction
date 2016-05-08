def get_assimilator_data(mode, assimilator, text, link):
    """
    This function is used for get parsed web/local document from a Tika-service
    mode: get metadata or content body
    assimilator: api address of the text assimilator, running apache tika
    text: piece of raw text
    link: web url to a html page or binary file
    """

    import requests
    payload = {'mode': mode}

    # Prepare data, if it is text pass it as it is else a dictionary with link
    if text:
        data = text
    else:
        data = {'link': link}

    # Prepare url for assimilator
    url = "%s/parse/" % assimilator
    request = requests.post(url, params=payload, data=data)

    return request.content

def process_pos(pos_server, content):
    """
    A generator function to extract part of speech tags from pos_server
    pos_server: address of the pos_server, typically, http://<ip>:<port>/parse
    content   : raw content, parsed from text assimilator

    Not: There is a limitation, that POS server crashes on providing large data, hence always adviced
    to use with text assimilator
    """
    import requests

    # Prepare url for pos_server
    url = "%s/parse" % pos_server

    # Temporary fix for part of speech tagger, lexical parser does not recognize square brackets
    content = content.replace(b'[', b'(')
    content = content.replace(b']', b')')

    # Prepare request object, with text as url-encoded data for the part of speech tagger
    for line in content.split(b'\n'):
        r = requests.post(url, data=line, stream=True)
        for resp_line in r.iter_lines():
            yield resp_line

def extract_entities(pos_server, assimilator, mode, text, link):
    """
    Extract tokens in the buckets of nouns and other entities
    pos_server: part of speech tagger address
    assimilarot: assimilator address
    mode: metadata or content
    """
    content = get_assimilator_data(mode=mode, assimilator=assimilator, text=text, link=link)
    if mode == "meta":
        import json
        yield json.dumps(json.loads(content.decode()), indent=4)
    else:
        import json
        from .semantic_parser import read_dep
        from nltk.tree import Tree

        concept_map = {}

        pos_generator = process_pos(pos_server, content=content)
        for line in pos_generator:
            data = json.loads(line.decode())
            tree = Tree.fromstring(data['tree'])

            tokens = read_dep(tree)
            yield tokens

if __name__ == "__main__":
    from getopt import getopt,GetoptError

    assimilator = None
    pos_server  = None
    text = None
    link = None
    mode = "content"

    def print_help(e=None):
        if e:
            print(str(e))
        print("\t -h          : This message")
        print("\t -p          : <address of the parser>")
        print("\t--pos-server : <address of the parser>") 
        print("\t -a          : <address of the assimilator>")
        print("\t--assimilator: <address of the assimilator>")
        print("\t -t          : <text>")
        print("\t--text       : <text>")
        print("\t -l          : <link>")
        print("\t--link       : <link>")
        print("\t -m          : <mode meta,content>")
        print("\t--mode       : <mode meta,content>")
        from sys import exit
        exit(0)

    file = None

    from sys import argv
    try:
        opts,args = getopt(argv[1:], "p:a:t:l:m:hf:", ["pos-server=", "text=", "link="])
    except GetoptError as e:
        print_help(e)
    for opt,arg in opts:
        if opt in ["-a", "--assimilator"]:
            assimilator = arg
        elif opt in ["-p", "--pos-server"]:
            pos_server = arg
        elif opt in ["-t", "--text"]:
            text = arg
        elif opt in ["-l", "--link"]:
            link = arg
        elif opt in ["-m", "--mode"]:
            mode = arg
        elif opt in ['-f']:
            file = arg

    if not assimilator:
        print_help("--assimilator required")
    if not pos_server:
        print_help("--pos_server required")
    if not text and not link and not file:
        print_help("--text or --link required")
    if mode not in ["meta", "content"]:
        print_help("invalid --mode value")

    if file:
        text = open(file, "rb").read()

    content = get_assimilator_data(mode=mode, assimilator=assimilator, text=text, link=link)

    # Options for extract entities
    opts = {'pos_server': pos_server, 'assimilator': assimilator, 'mode': mode, 'text': text, 'link': link}
    doc_generator = extract_entities(**opts)

    if mode == "meta":
        metadata = list(doc_generator)[0]
        print(metadata)
    else:
        for tokens in doc_generator:
            print(tokens)
