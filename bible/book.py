import re
import pandas as pd
from functools import reduce
from itertools import combinations

from stop_words import get_stop_words

from bible.splitter import *
from bible.line import Line
stop_words = get_stop_words('en')


class Book:

    def __init__(self, text):
        self.text = self.clean_book(text)
        lines = re.split(r'[0-9]+:[0-9]+ ', self.text)
        self.title = lines[0]
        self.lines = lines[1:]
        self.nouns = [Line(line) for line in self.lines]
        self.counts = self.get_counts(self.nouns)
        self.edges = self.get_edge_frame_from_book()

    def clean_book(self, book):
        cleaned_book = clean_text(
            book.replace('\ufeff', '').replace('\n', ' '), spaces=True)
        pattern = re.compile(r'\b(' + r'|'.join(stop_words) + r')\b\s*')
        return pattern.sub('', cleaned_book.lower())

    def get_counts(self, lines, ctt_filter=25):
        noun_list = [line.nouns for line in lines]
        nouns = reduce(lambda x, y: {k: x.get(k, 0) + y.get(k, 0)
                       for k in set(x) | set(y)}, noun_list)

        df = pd.Series(nouns).sort_values(ascending=False).to_frame()
        df.columns = ['count']
        df = df[df['count'] > ctt_filter]
        return df

    def get_filtered_combinations(self, nouns):
        combos = []
        for combo in combinations(nouns, 2):

            common_char = all([node in self.counts.index for node in combo])

            if common_char:
                combos.append(combo)

        return combos

    def get_edge_frame_from_book(self):
        tot_edges = pd.DataFrame()

        for line in self.nouns:
            edges = pd.DataFrame(self.get_filtered_combinations(line.nouns))
            tot_edges = tot_edges.append(edges)

        tot_edges.columns = ['node_1', 'node_2']
        tot_edges = tot_edges.reset_index().drop('index', axis=1)
        return tot_edges
