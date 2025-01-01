import re

def match_criteria(title, query):
    title = title.replace(" ", "")
    query = query.replace(" ", "")

    if query.lower() in title.lower():
        if ("promax" in query.lower()) and ("promax" in title.lower()):
            return True
        if ("promax" not in query.lower()) and ("promax" in title.lower()):
            return False
        if ("pro" in query.lower()) and ("pro" in title.lower()):
            return True
        if ("max" in query.lower()) and ("max" in title.lower()):
            return True
        if ("max" not in query.lower()) and ("max" not in title.lower()):
            return True
        if ("pro" not in query.lower()) and ("pro" not in title.lower()):
            return True
        return False
    return False

print(match_criteria("iPhone 14 Pro Max brand new", "iphone 14 pro"))        
        
    
