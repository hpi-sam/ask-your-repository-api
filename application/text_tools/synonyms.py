from textblob import Word
import nltk

from .helpers import TextProcessingHelpers as Helper
from .word_processing import WordProcessor

class SynonymGenerator:

    def __init__(self, params):
        self.params = Helper.get_list(params)
        self.search_terms = []
        self.synonyms = []
        self.synsets = []
        self.synset_relations = []
        self.synset_synonyms = []
        self.synonyms_list = Helper.get_string(self.params) + " "

        self.detailed_log = False
        self.general_log = True

    def get_synonyms(self):
        self.search_terms = WordProcessor(self.params).process_words()

        if self.general_log:
            print("Search Terms:")
            print(self.search_terms)

        self._create_synsets()
        self._combine_synsets()
        self.synonyms_list += self._parse_synsets_to_string(self.synonyms)

        if self.general_log:
            print("Final Result:")
            print(self.synonyms_list)

        return self.synonyms_list

    def _create_synsets(self):
        self.synsets = self._get_word_synsets(self.search_terms)
        self.synset_relations = self._get_synset_relations(self.synsets)
        self.synset_synonyms = self._get_word_synsets(self.synsets)

    def _combine_synsets(self):
        self.synonyms.extend(self.synsets + self.synset_relations + self.synset_synonyms)

    def _parse_synsets_to_string(self, synsets):
        lemmas = self._get_lemma_names(synsets)
        return Helper.get_string(set(lemmas))

    def _get_word_synsets(self, list):
        word_synsets = []
        print("here")
        print(list)
        for item in list:
            print(item)
            word = Helper.get_word(item)
            print(word)
            word_synsets.extend(word.synsets)
        word_synsets = self._remove_unfit_synonyms(0.5, word_synsets)
        print(word_synsets)
        print("until here")
        return word_synsets

    def _remove_unfit_synonyms(self, bound, synsets):
        approved_synonyms = []
        for item in self.params:
            word = Helper.get_word(item)
            for synonym in synsets:
                sim = self._check_path_similarity(word, synonym)
                if self.detailed_log:
                    print(sim)
                    print("\n")
                if sim >= bound:
                    approved_synonyms.insert(0, synonym)
        if self.detailed_log:
            print("were approved:")
            print(approved_synonyms)
        return approved_synonyms

    def _get_synset_relations(self, synsets):
        synset_relations = []
        for synset in synsets:
            synset_relations.extend(
                synset.hypernyms() + synset.hyponyms() + synset.member_holonyms() + synset.part_meronyms())
        return synset_relations

    def _get_second_level_synonyms(self, superset):
        synonyms_list = self._parse_synsets_to_string(superset)
        all_synsets = self._get_synonym_synsets(synonyms_list)
        return all_synsets

    def _check_path_similarity(self, word, synset):
        word_synset = word.synsets[0]
        if self.detailed_log:
            print(word_synset)
            print(synset)
        similarity = word_synset.path_similarity(synset)
        return similarity if similarity else 0.0

    def _get_lemma_names(self, synsets):
        lemmas = []
        for synset in synsets:
            lemma = synset.lemma_names()
            lemmas.extend(lemma)
        return lemmas
