from textblob import Word
import nltk

from .helpers import TextProcessingHelpers as Helper

class WordProcessor:

    def __init__(self, params):
        self.items = params # a list of strings
        self.processed_words = ""
        self.valid_tags = ["FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBR", "RBS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

    def process_words(self):
        processed_words = []
        filtered_words = self._get_filtered_words(self.items)
        for item in filtered_words:
            word = Helper.get_word(item)
            spellchecked_words = self._spellcheck_word(word)
            corrected_words = self._get_filtered_words(spellchecked_words)
            for item in corrected_words:
                processed_words.insert(0, item)
        self.processed_words = processed_words
        result = self.processed_words if self.processed_words else self.items
        return result

    def _spellcheck_word(self, word):
        set = word.spellcheck()
        corrected_words = self._get_probable_corrections(set)
        return corrected_words

    def _get_probable_corrections(self,set):
        corrections = []
        for item in set:
            probability = item[1]
            if probability > 0.01:
                word = item[0]
                corrections.insert(0, word)
        return corrections

    def _get_filtered_words(self, items):
        words = []
        for item in items:
            print("start")
            print(item)
            token = nltk.word_tokenize(item)
            print(token)
            pos_tag = nltk.pos_tag(token)[0]
            print(pos_tag)
            word = pos_tag[0]
            print(word)
            tag = pos_tag[1]
            print(tag)
            print("end")
            if self._is_valid(tag):
                words.insert(0, word)
        return words

    def _is_valid(self, tag):
        if tag in self.valid_tags:
            return True
        else:
            return False
