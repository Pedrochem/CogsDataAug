from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet 
# pip install textblob
lemmatizer = WordNetLemmatizer()
from textblob import TextBlob, Word

from nltk.corpus import wordnet as wn
print(wn._morphy('hated', 'v')[0])
  

#print("Saw :", lemmatizer.lemmatize("saw"))
# print("Hoped :", lemmatizer.lemmatize("hoped", wordnet.VERB))
# print("Hated :", lemmatizer.lemmatize("hated", wordnet.VERB))
