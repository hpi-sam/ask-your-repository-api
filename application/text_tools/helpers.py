from textblob import Word
import nltk

class TextProcessingHelpers:

    def get_word(string):
        return Word(string)

    def get_string(list):
        return ' '.join(list)

    def get_list(string):
        return string.split()
