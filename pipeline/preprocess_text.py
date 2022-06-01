#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal

# External
import nltk
from nltk.corpus import stopwords

import stanza


class TextPreprocessor:
    min_len = 2
    max_word_len = 40

    custom_stoplist = [
    ]

    garbage = [

    ]

    def __init__(self):
        nltk.download('stopwords')
        stanza.download('en')

        self.nlp = stanza.Pipeline(lang='en', processors='tokenize, lemma')
        self.english_stopwords = stopwords.words("english")

    def lemmatize(self, text, return_tokens=False):
        lemmatized_doc = self.nlp(text)
        lemmatized_tokens = []

        for sentences in lemmatized_doc.sentences:
            for word in sentences.words:
                if word.lemma is not None \
                        and word.lemma not in self.english_stopwords \
                        and word.lemma not in self.custom_stoplist \
                        and self.min_len < len(word.lemma) < self.max_word_len:
                    lemmatized_tokens.append(word.lemma)

        if return_tokens:
            return lemmatized_tokens
        else:
            return ' '.join(lemmatized_tokens)
