import nltk
from textblob import Word

class SynonymGenerator:

    @classmethod
    def get_synonyms(cls,params):
        synonyms = []

        synsets = cls.get_word_synsets(params)
        synset_relations = cls.get_synset_relations(synsets)
        synset_synonyms = cls.get_synset_synonyms(synsets)

        synonyms.extend(synsets + synset_relations + synset_synonyms)

        synonyms_list = cls.get_synonym_list(synonyms)

        return synonyms_list

    @classmethod
    def get_synset_synonyms(cls,superset):
        synonyms_list = cls.get_synonym_list(superset)
        synset_synonyms = cls.get_word_synsets(synonyms_list)
        return synset_synonyms

    @classmethod
    def get_synset_relations(cls,synsets):
        synset_relations = []
        for synset in synsets:
            synset_relations.extend(synset.hypernyms())
            synset_relations.extend(synset.hyponyms())
            synset_relations.extend(synset.member_holonyms())
            synset_relations.extend(synset.part_meronyms())
        return synset_relations

    @classmethod
    def get_word_synsets(cls,params):
        args = params.split(' ')
        word_synsets = []
        for arg in args:
            word = Word(arg)
            word_synsets.extend(word.synsets)
        return word_synsets

    @classmethod
    def get_lemma_names(cls,synsets):
        lemmas = []
        for synset in synsets:
            lemma = synset.lemma_names()
            lemmas.extend(lemma)
        return lemmas

    @classmethod
    def get_synonym_list(cls,synsets):
        lemmas = cls.get_lemma_names(synsets)
        return ' '.join(set(lemmas))
