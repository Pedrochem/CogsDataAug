import stanza
from stanza.models.common.doc import Document


nlp = stanza.Pipeline(lang='en', processors='tokenize,lemma', lemma_pretagged=True, tokenize_pretokenized=True)
pp = Document([[{'id': 1, 'text': 'snoozed', 'upos': 'VERB'}]])
doc = nlp(pp)
print(doc)




# pip install textblob
# from textblob import TextBlob, Word
# from nltk.corpus import wordnet as wn
# print(wn._morphy('hated', 'v')[0])
