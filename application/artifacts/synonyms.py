"""Generate Synonyms"""
from textblob import Word


class SynonymGenerator:  # pylint:disable=too-few-public-methods
    """Generate synonyms/related words based on a search"""

    def __init__(self, params):
        self.params = params
        self.synonyms = []
        self.synsets = []
        self.synset_relations = []
        self.synset_synonyms = []
        self.synonyms_list = ""

    def get_synonyms(self):
        """Get synonyms for this configured generator"""
        self._create_synsets()
        self._combine_synsets()
        self.synonyms_list = self._parse_synsets_to_string(self.synonyms)
        return self.synonyms_list if self._word_found() else self.params

    def _word_found(self):
        return True if self.synonyms_list else False

    def _create_synsets(self):
        self.synsets = self._get_word_synsets(self.params)
        self.synset_relations = self._get_synset_relations(self.synsets)
        self.synset_synonyms = self._get_synset_synonyms(self.synsets)

    def _get_synset_synonyms(self, superset):
        synonyms_list = self._parse_synsets_to_string(superset)
        synset_synonyms = self._get_word_synsets(synonyms_list)
        return synset_synonyms

    def _get_synset_relations(self, synsets):
        synset_relations = []
        for synset in synsets:
            synset_relations.extend(
                synset.hypernyms() + synset.hyponyms() + synset.member_holonyms() + synset.part_meronyms()
            )
        return synset_relations

    def _get_word_synsets(self, words):
        args = words.split(" ")
        word_synsets = []
        for arg in args:
            word = Word(arg)
            word_synsets.extend(word.synsets)
        return word_synsets

    def _get_lemma_names(self, synsets):
        lemmas = []
        for synset in synsets:
            lemma = synset.lemma_names()
            lemmas.extend(lemma)
        return lemmas

    def _parse_synsets_to_string(self, synsets):
        lemmas = self._get_lemma_names(synsets)
        return " ".join(set(lemmas))

    def _combine_synsets(self):
        self.synonyms.extend(self.synsets + self.synset_relations + self.synset_synonyms)
