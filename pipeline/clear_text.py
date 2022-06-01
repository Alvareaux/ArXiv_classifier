#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import string

# Internal

# External
import emoji
import regex as re


class TextCleaner:
    contraction_mapping = {
        "ain't": "is not", "aren't": "are not", "can't": "cannot", "'cause": "because",
        "could've": "could have", "couldn't": "could not",
        "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not",
        "hasn't": "has not", "haven't": "have not",
        "he'd": "he would", "he'll": "he will", "he's": "he is", "how'd": "how did",
        "how'd'y": "how do you", "how'll": "how will",
        "how's": "how is", "I'd": "I would", "I'd've": "I would have", "I'll": "I will",
        "I'll've": "I will have", "I'm": "I am",
        "I've": "I have", "i'd": "i would", "i'd've": "i would have", "i'll": "i will",
        "i'll've": "i will have", "i'm": "i am",
        "i've": "i have", "isn't": "is not", "it'd": "it would", "it'd've": "it would have",
        "it'll": "it will", "it'll've": "it will have",
        "it's": "it is", "let's": "let us", "ma'am": "madam", "mayn't": "may not",
        "might've": "might have", "mightn't": "might not",
        "mightn't've": "might not have", "must've": "must have", "mustn't": "must not",
        "mustn't've": "must not have", "needn't": "need not",
        "needn't've": "need not have", "o'clock": "of the clock", "oughtn't": "ought not",
        "oughtn't've": "ought not have", "shan't": "shall not",
        "sha'n't": "shall not", "shan't've": "shall not have", "she'd": "she would",
        "she'd've": "she would have", "she'll": "she will",
        "she'll've": "she will have", "she's": "she is", "should've": "should have",
        "shouldn't": "should not", "shouldn't've": "should not have",
        "so've": "so have", "so's": "so as", "this's": "this is", "that'd": "that would",
        "that'd've": "that would have", "that's": "that is",
        "there'd": "there would", "there'd've": "there would have", "there's": "there is",
        "here's": "here is", "they'd": "they would",
        "they'd've": "they would have", "they'll": "they will", "they'll've": "they will have",
        "they're": "they are", "they've": "they have",
        "to've": "to have", "wasn't": "was not", "we'd": "we would", "we'd've": "we would have",
        "we'll": "we will", "we'll've": "we will have",
        "we're": "we are", "we've": "we have", "weren't": "were not", "what'll": "what will",
        "what'll've": "what will have",
        "what're": "what are", "what's": "what is", "what've": "what have", "when's": "when is",
        "when've": "when have", "where'd": "where did",
        "where's": "where is", "where've": "where have", "who'll": "who will",
        "who'll've": "who will have", "who's": "who is",
        "who've": "who have", "why's": "why is", "why've": "why have", "will've": "will have",
        "won't": "will not", "won't've": "will not have",
        "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have",
        "y'all": "you all", "y'all'd": "you all would",
        "y'all'd've": "you all would have", "y'all're": "you all are", "y'all've": "you all have",
        "you'd": "you would", "you'd've": "you would have",
        "you'll": "you will", "you'll've": "you will have", "you're": "you are",
        "you've": "you have", 'u.s': 'america', 'e.g': 'for example'
    }

    punct = [
        ',', '.', '"', ':', ')', '(', '-', '!', '?', '|', ';', "'", '$', '&', '/', '[', ']', '>', '%', '=', '#',
        '*', '+', '\\', '•', '~', '@', '£',
        '·', '_', '{', '}', '©', '^', '®', '`', '<', '→', '°', '€', '™', '›', '♥', '←', '×', '§', '″', '′', 'Â',
        '█', '½', 'à', '…',
        '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―',
        '¥', '▓', '—', '‹', '─',
        '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸',
        '¾', 'Ã', '⋅', '‘', '∞',
        '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø',
        '¹', '≤', '‡', '√',
    ]

    punct_mapping = {
        "‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2",
        "—": "-", "–": "-", "’": "'", "_": "-",
        "`": "'", '“': '"', '”': '"', '“': '"', "£": "e", '∞': 'infinity', 'θ': 'theta', '÷': '/',
        'α': 'alpha', '•': '.', 'à': 'a', '−': '-',
        'β': 'beta', '∅': '', '³': '3', 'π': 'pi', '!': ' '
    }

    mispell_dict = {
        'colour': 'color', 'centre': 'center', 'favourite': 'favorite', 'travelling': 'traveling',
        'counselling': 'counseling', 'theatre': 'theater',
        'cancelled': 'canceled', 'labour': 'labor', 'organisation': 'organization', 'wwii': 'world war 2',
        'citicise': 'criticize', 'youtu ': 'youtube ',
        'Qoura': 'Quora', 'sallary': 'salary', 'Whta': 'What', 'narcisist': 'narcissist', 'howdo': 'how do',
        'whatare': 'what are', 'howcan': 'how can',
        'howmuch': 'how much', 'howmany': 'how many', 'whydo': 'why do', 'doI': 'do I',
        'theBest': 'the best', 'howdoes': 'how does',
        'mastrubation': 'masturbation', 'mastrubate': 'masturbate', "mastrubating": 'masturbating',
        'pennis': 'penis', 'Etherium': 'Ethereum',
        'narcissit': 'narcissist', 'bigdata': 'big data', '2k17': '2017', '2k18': '2018', 'qouta': 'quota',
        'exboyfriend': 'ex boyfriend',
        'airhostess': 'air hostess', "whst": 'what', 'watsapp': 'whatsapp',
        'demonitisation': 'demonetization', 'demonitization': 'demonetization',
        'demonetisation': 'demonetization'
    }

    @staticmethod
    def __remove_formula(text):
        """
        Clean formulas that start and end with $
        """

        text = re.sub(r'\$(.*)\$', '', text)

        return text

    @staticmethod
    def __clean_text(text, lowercase):
        """
        Clean emoji, Make text lowercase, remove text in square brackets,remove links,remove punctuation
        and remove words containing numbers.
        """

        text = emoji.demojize(text)
        text = re.sub(r'\:(.*?)\:', '', text)

        if lowercase:
            text = str(text).lower()

        text = re.sub('\[.*?\]', '', text)

        # Replacing everything with space except (a-z, A-Z, ".", "?", "!", ",", "'")
        text = re.sub(r"[^a-zA-Z?.!,¿']+", " ", text)
        return text

    @staticmethod
    def __clean_contractions(text, mapping):
        """
        Clean contraction using contraction mapping
        """

        specials = ["’", "‘", "´", "`"]

        for s in specials:
            text = text.replace(s, "'")

        for word in mapping.keys():
            if "" + word + "" in text:
                text = text.replace("" + word + "", "" + mapping[word] + "")

        # Remove Punctuations
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)

        # Creating a space between a word and the punctuation following it
        # "he is a boy." => "he is a boy ."

        text = re.sub(r"([?.!,¿])", r" \1 ", text)
        text = re.sub(r'[" "]+', " ", text)

        return text

    @staticmethod
    def __clean_special_chars(text, punct, mapping):
        """
        Cleans special characters present(if any)
        """

        for p in mapping:
            text = text.replace(p, mapping[p])

        for p in punct:
            text = text.replace(p, f' {p} ')

        specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''}

        for s in specials:
            text = text.replace(s, specials[s])

        return text

    @staticmethod
    def __correct_spelling(x, dic):
        """
        Corrects common spelling errors
        """

        for word in dic.keys():
            x = x.replace(word, dic[word])
        return x

    @staticmethod
    def __remove_space(text):
        """
        Removes awkward spaces
        """

        # Removes awkward spaces
        text = text.strip()
        text = text.split()
        return " ".join(text)

    def text_clearing_pipeline(self, text, lowercase=True):
        """
        Cleaning and parsing the text.
        """

        text = self.__remove_formula(text)
        text = self.__clean_text(text, lowercase)
        text = self.__clean_contractions(text, self.contraction_mapping)
        text = self.__clean_special_chars(text, self.punct, self.punct_mapping)
        text = self.__correct_spelling(text, self.mispell_dict)
        text = self.__remove_space(text)

        return text


if __name__ == '__main__':
    prc = TextCleaner()

    text = '''Let $[n]=\{1,2,\ldots,n\}$ be a finite chain and let $\mathcal{CT}_{n}$ be
the semigroup of full contractions on $[n]$. Denote $\mathcal{ORCT}_{n}$ and
$\mathcal{OCT}_{n}$ to be the subsemigroup of order preserving or reversing and
the subsemigroup of order preserving full contractions, respectively. It was
shown in [17] that the collection of all regular elements (denoted by,
Reg$(\mathcal{ORCT}_{n})$ and Reg$(\mathcal{OCT}_{n}$), respectively) and the
collection of all idempotent elements (denoted by E$(\mathcal{ORCT}_{n})$ and
E$(\mathcal{OCT}_{n}$), respectively) of the subsemigroups $\mathcal{ORCT}_{n}$
and $\mathcal{OCT}_{n}$, respectively are subsemigroups. In this paper, we
study some combinatorial and rank properties of these subsemigroups.'''

    print(prc.text_clearing_pipeline(text, lowercase=True))
