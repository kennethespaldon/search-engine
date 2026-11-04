import sys # Used to read the file name from the command line

#Runtime: O(n), where n is the number of characters in the file.
#The function goes through each character once.
def tokenize(file_path):
    """
    Reads the text file and creates a list of tokens from it.

    A token is a sequence of letters or numbers. Each character is checked
    one at a time, and characters that are not alphanumeric separate the
    tokens. Tokens are changed to lowercase so words with different
    capitalization are treated as the same word.

    If the file cannot be found, an empty list is returned.
    """
    tokens = []
    current_token = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            for line in file:
                for char in line:
                    if char.isascii() and char.isalnum():
                        current_token.append(char.lower())
                    else:
                        if current_token:
                            tokens.append("".join(current_token))
                            current_token = []
    except FileNotFoundError:
        return []
    
    if current_token:
        tokens.append("".join(current_token))

    return tokens

#Runtime: O(n), where n is the number of tokens.
#Each token is processed once.
def compute_word_frequencies(tokens):
    """
    Takes the list  of tokens and counts how many times each token appears.

    A dictionary is used to  store the tokens and their frequencies.
    If a token is already in the dictionary, its count is increased by one.
    Otherwise, it is added to the dictionary with a count of one.

    The dictionary containing each token and its frequency is returned.
    """
    frequencies = {}

    for token in tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1

    return frequencies

#Runtime: O(n log n), where n is the number of unique tokens.
#Sorting the token-frequency pairs takes O(n log n) time.
def print_frequencies(frequencies):
    """
    Prints each token and its frequency in the order required by the assignment.

    Tokens with a higher frequency are printed first. If two tokens have the
    same frequency, they are ordered alphabetically. The helper function
    sort_order() creates the sorting rule used by sorted().
    """
    #Runtime: O(1), since it only looks at one token-frequency pair.
    def sort_order(item):
        token, frequency = item
        return (-frequency, token)

    sorted_frequencies = sorted(
        frequencies.items(),
        key=sort_order
    )

    for token, frequency in sorted_frequencies:
        print(token, frequency)