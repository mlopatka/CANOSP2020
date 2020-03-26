import re
import os
import itertools
import multiprocessing
import spacy
import warnings
import numpy as np
import pandas as pd

from typing import List, Callable
from requests_html import HTML
from pandas import DataFrame
from nltk import FreqDist
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from tqdm import tqdm
from num2words import num2words

from .language_dector import LanguageDetector

# Filter out annoying bs4 warning about URL in the text
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

TITLE_CONTENT = "title_content"


def parallelize_dataframe(df, func, n_cores=multiprocessing.cpu_count()):
    df_split = np.array_split(df, n_cores)
    pool = multiprocessing.Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def apply_clean_text(df):
    df.loc[:, "content"] = df["content"].apply(clean_text)
    df.loc[:, "title"] = df["title"].apply(clean_text)
    return df


def clean_text(text):
    if not text:
        return text
    try:
        text = HTML(html=text).text
    except Exception as e:
        print(e)
        print(text)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"…", "...", text)
    text = re.sub(r"[`‘’‛⸂⸃⸌⸍⸜⸝]", "'", text)
    text = re.sub(r"[„“]|(\'\')|(,,)", '"', text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lower()

    return text


def parallelize_spacy_docs(docs, df, func, n_cores=multiprocessing.cpu_count()):
    docs_split = np.array_split(docs, n_cores)
    df_split = np.array_split(df, n_cores)
    pool = multiprocessing.Pool(n_cores)
    output_df = pd.concat(pool.map(func, zip(docs_split, df_split)))
    pool.close()
    pool.join()
    return output_df


def apply_spacy_docs(inputs):
    docs, df = inputs
    output_content = []
    output_lang = []
    for index, doc in enumerate(docs):
        lang = doc._.language
        if lang == "en":
            output_content.append(" ".join([token.lemma_ for token in doc if not (token.is_punct or token.is_stop)]))
        else:
            output_content.append(doc.text)
        output_lang.append(lang)
    df["content"] = output_content
    df["lang"] = output_lang

    return df


def apply_num2words(inputs):

    inputs = inputs.split()
    tokens = []
    for token in inputs:
        if token.isnumeric():
            tokens.append(num2words(token))
        else:
            tokens.append(token)
    return " ".join(tokens)


class Preprocess:
    """
    Preprocess text documents with spacy.

    :param csv_file: Path to input csv file
    :param stopwords: A list of custom stopwords

    >>> preprocessor = Preprocess("data/tickets.csv")
    >>> preprocessor.preprocess_tickets()
    """

    def __init__(self, csv_file: str, stopwords: List[str] = None, num_2_word=False):
        self._df = pd.read_csv(csv_file)
        self._nlp = spacy.load("en_core_web_sm")
        self._num_2_word = num_2_word

        self._df["title"] = self._df["title"].astype(str)
        self._df["content"] = self._df["content"].astype(str)

        if stopwords:
            self._nlp.Defaults.stop_words |= set(stopwords)

    def preprocess_tickets(self):
        """
        Preprocess ticket title and content

        Apply the following
            - Strip HTML tags
            - Strip whitespaces
            - Remove dots
            - Remove http[s] url suffix
            - Remove punctuation
            - Remove stop words
            - Lemmatize

        Overwrite preprocessed text back to original column
        in the dataframe.

        Add new `title_content` column column
        which consists content from both title and content

        Add new `lang` column.
        """
        import time

        language_detector = LanguageDetector()
        self._nlp.add_pipe(language_detector, name="language_detector")

        # Add new lang column with default value of `en`
        start_time = time.time()
        self._df = parallelize_dataframe(self._df, apply_clean_text)
        print(f"Pre-preprocess (content): {time.time() - start_time} sec")

        # Run spacy pipeline on `content` column
        start_time = time.time()
        content_docs = list(
            self._nlp.pipe(
                self._df["content"], disable=["tagger", "ner", "textcat"], n_process=multiprocessing.cpu_count()
            )
        )
        print(f"Spacy pipe (content): {time.time() - start_time} sec")

        # Remove punct, stopwords, lemmatizer on `content`
        start_time = time.time()
        self._df = parallelize_spacy_docs(content_docs, self._df, apply_spacy_docs)
        print(f"Final cleanup (content): {time.time() - start_time} sec")

        # Run spacy pipeline on `title` column
        self._nlp.remove_pipe("language_detector")
        title_docs = list(
            self._nlp.pipe(
                self._df["title"], disable=["parser", "ner", "textcat"], n_process=multiprocessing.cpu_count()
            )
        )

        # Remove punct, stopwords, lemmatizer on `title`
        start_time = time.time()
        self._df.loc[:, "title"] = [
            " ".join([token.lemma_ for token in doc if not (token.is_punct or token.is_stop)]) for doc in title_docs
        ]
        print(f"Final cleanup (title): {time.time() - start_time} sec")

        # convert number to word on `content` and `title`
        if self._num_2_word:
            start_time = time.time()
            self._df["title"] = self._df["title"].apply(apply_num2words)
            self._df["content"] = self._df["content"].apply(apply_num2words)
            print(f"Final cleanup (title and content): {time.time() - start_time} sec")

        # Merge `title` and `content` column into a new column
        self._df["title_content"] = self._df["title"] + " " + self._df["content"]

    @staticmethod
    def preprocess_tags(tags):
        nlp = spacy.load("en_core_web_sm")
        docs = nlp.pipe(tags, disable=["parser", "ner", "textcat"], n_process=multiprocessing.cpu_count())
        tags = ["".join([token.lemma_ for token in doc if not (token.is_stop)]) for doc in docs]
        return list(filter(None, tags))

    @staticmethod
    def get_stop_words(input_file="data/tickets_word2vec.model", threshold=0.02) -> List[str]:
        """
        Get a list of step words base on relative frequency.
        The input could either be the raw CSV file or word2vec model build with genism.
        The input format will be determined by the input_file extension <filename>.[csv|model].
        The `eval` method is a function which takes a float variable,
        word frequency, as a single argument and return a boolean value
        which represent whether a word is a stop word or not.
        By default, we consider the words within the top 2 percentile as stop words.
            >>> from canosp2020.preprocessing import Preprocess
            >>> stopwords = Preprocess.get_stop_words(input_file="data/tickets_word2vec.model", eval=lambda x: x <= 0.2)
        :param input_file: Path to tickets data csv file or genism word2vec model.
        :param eval: A function to evaluate whether a word is stop word of not
        :rtype: A list of words.
        """
        _, extension = os.path.splitext(os.path.basename(input_file))

        if extension == ".csv":
            nlp = spacy.load("en_core_web_sm")

            # Load csv file and merge title and content column
            df = pd.read_csv(input_file)
            df[TITLE_CONTENT] = df["title"] + " " + df["content"]
            df[TITLE_CONTENT].replace("", np.nan, inplace=True)
            df.dropna(subset=[TITLE_CONTENT], inplace=True)
            docs = list(nlp.pipe(df["title_content"], disable=["tagger", "parser", "ner"]))
            sents = [[token.text for token in doc] for doc in docs]
            big_words = itertools.chain(*sents)

            # Build frequency distribution
            fdist = FreqDist(big_words)

        elif extension == ".model":
            model = Word2Vec.load(input_file)
            counter = {word: vocab.count for word, vocab in model.wv.vocab.items()}
            counter = dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))
            fdist = FreqDist(counter)

        # stopwords = [word for word in fdist if eval(fdist.freq(word))]
        stopwords = [each[0] for each in fdist.most_common(int(threshold * fdist.B()))]

        return stopwords
