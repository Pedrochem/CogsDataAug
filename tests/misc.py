import stanza

nlp = stanza.Pipeline(lang='en', processors='lemma')

doc = nlp('He hoped that she saw what Luis hated')
for sentence in doc.sentences:
    for word in sentence.words:
        print(word.text, word.lemma)

# print(*[f'word: {word.text+" "}\tlemma: {word.lemma}' for sent in doc.sentences for word in sent.words], sep='\n')






# pip install textblob
# from textblob import TextBlob, Word
# from nltk.corpus import wordnet as wn
# print(wn._morphy('hated', 'v')[0])
