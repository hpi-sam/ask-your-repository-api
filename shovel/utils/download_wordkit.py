import nltk
from shovel import task


@task
def download_wordkit():
    nltk.download("wordnet")
