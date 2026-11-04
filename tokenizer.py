import sys # Used to read the file name from the command line

#Runtime: O(n), where n is the number of characters in the text.
#The function goes through each character once.
def tokenize(text):
    """
    Creates a list of tokens from a string.

    A token is a sequence of letters or numbers. Each character is checked
    one at a time, and characters that are not alphanumeric separate the
    tokens. Tokens are changed to lowercase so words with different
    capitalization are treated as the same word.
    """
    tokens = []
    current_token = []

    for char in text:
        if char.isascii() and char.isalnum():
            current_token.append(char.lower())
        else:
            if current_token:
                tokens.append("".join(current_token))
                current_token = []

    if current_token:
        tokens.append("".join(current_token))

    return tokens
