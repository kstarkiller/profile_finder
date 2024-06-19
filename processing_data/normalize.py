import unicodedata
import re

# s is input text
def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # replace all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.replace("\t", "")
    s = s.replace("\r", "")
    s = s.replace("\r\n", "")
    s = s.replace("\n\r", "")
    s = s.replace("  ", " ")
    s = s.strip()
    # replace underscores with spaces
    s = s.replace('_', ' ')
    
    # # replace all accents with their base letter
    # s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
    # # lowercase the text
    # s = s.lower()
    
    return s