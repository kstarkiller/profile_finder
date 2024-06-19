import re

# s is input text
def normalize_text(s):
    """
    Normalize a text by removing all special characters and multiple spaces.

    :param s: str
    :return: str
    """
    # remove all special characters
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
    
    return s