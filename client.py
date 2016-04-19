def get_assimilator_data(mode, assimilator, text, link):
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
    import requests

    # Prepare url for pos_server
    url = "%s/parse" % pos_server
    # Prepare request object, with text as url-encoded data for the part of speech tagger
    r = requests.post(url, data=content, stream=True)
 
    i = 0
    for line in r.iter_lines():
        yield line

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

    from sys import argv
    try:
        opts,args = getopt(argv[1:], "p:a:t:l:m:h", ["pos-server=", "text=", "link="])
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

    if not assimilator:
        print_help("--assimilator required")
    if not pos_server:
        print_help("--pos_server required")
    if not text and not link:
        print_help("--text or --link required")
    if mode not in ["meta", "content"]:
        print_help("invalid --mode value")

    content = get_assimilator_data(mode=mode, assimilator=assimilator, text=text, link=link)
    if mode == "meta":
        import json
        print(json.dumps(json.loads(content.decode()), indent=4))
    else:
        pos_generator = process_pos(pos_server, content=content)
