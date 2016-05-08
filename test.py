from sem_client import extract_entities

pos_server = "http://127.0.0.1:8080/parse"
txt_server = "http://127.0.0.1:8081/parse"

mode = "content"
text = None
link = "http://en.wikipedia.org/"

token_generator = extract_entities(pos_server, txt_server, mode, text, link)
for tokens in token_generator:
    for token in tokens:
        print(token)
    print("\n")
