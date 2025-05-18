from langdetect import detect
import re

def is_english(query):
    try:
        words = re.findall(r"\w+", query)  
        non_english = [word for word in words if detect(word) != "en"]
        return len(non_english) == 0  
    except:
        return False
