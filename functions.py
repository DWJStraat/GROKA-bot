import json

def arg_handler(arg):
    arg = str(arg)
    print(arg)
    print(type(arg))
    arg = arg.split[1:]
    print(arg)

def register(text):
    config = json.load(open("config.json"))
    correctpassword = config["password"]
    return text is correctpassword
