from collections import Counter
import spacy
nlp = spacy.load('en')


class Line:

    def __init__(self, text):
        self.text = text
        self.nouns = self.get_nouns(text)

    def get_nouns(self, line):
        doc = nlp(line)
        nouns = [word.text for word in doc if word.pos_ in ['NOUN', 'PROPN']]
        return Counter(nouns)
