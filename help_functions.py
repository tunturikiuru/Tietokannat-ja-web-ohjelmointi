#import users
import database_functions as dbf


#SEARCH

def search_handler(request):
    word = request.args.get("word", "")
    word = check_asterisk(word)
    sender = request.args.get("sender", "")
    sender = check_asterisk(sender)
    subforums = request.args.getlist("subforum")
    subforums = [int(x) for x in subforums]
    time = request.args.get("time", "")
    order = request.args.get("order", "DESC")
    messages = dbf.search(word, sender, subforums, time, order)
    return messages


# CHECK

def check_input(content: str, min: int, max:int):
    if min <= len(content) <= max:
        return True
    return False

def check_asterisk(keyword):
    if keyword:
        if keyword[-1] == "*":
            keyword = keyword[0:-1]
        else:
            keyword =(r"([\.\,!\?\"\'\(\)=\-:;\+/\s]|^)" + keyword + r"([\.\,!\?\"\'\(\)=\-:;\+/\s]|$)")
    return keyword


    