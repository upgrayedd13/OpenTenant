import random
import string

# Generates a random string of numChars characters from the specified character subset.
# If charSubset is not specified, upper- and lower-case letters, numbers, and characters in the set !@#$%^&*()-_+=,.<>?:;'"[]{`} are used.
# The deafult charSubset should be safe for use in file names.
def genRandomString(numChars: int, charSubset: str|None=None) -> str:
    if charSubset is None:
        charSubset = string.ascii_letters + string.digits + "!@#$%^&*()-_+=,.<>?:;'\"[]{`}"
    return ''.join(random.choices(charSubset, k=numChars))