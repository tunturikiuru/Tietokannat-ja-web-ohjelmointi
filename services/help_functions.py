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


    