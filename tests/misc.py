# import stanza
# from stanza.models.common.doc import Document


# nlp = stanza.Pipeline(lang='en', processors='tokenize,lemma', lemma_pretagged=True, tokenize_pretokenized=True)
# pp = Document([[{'id': 1, 'text': 'shattered', 'pos': 'vbd'}]])
# doc = nlp(pp)
# print(doc)


# import spacy
# nlp = spacy.load("en_core_web_sm")
# doc = nlp(u"Apples and oranges are similar. Boots and hippos aren't.")

# for token in doc:
#     print(token, token.lemma, token.lemma_)


# import spacy
# nlp = spacy.load('en_core_web_sm')
import spacy
from spacy.lemmatizer import Lemmatizer, ADJ, NOUN, VERB
nlp = spacy.load('en')

lemmatizer = nlp.vocab.morphology.lemmatizer
print(lemmatizer('hated', 'VERB'))