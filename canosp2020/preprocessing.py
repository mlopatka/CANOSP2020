import re
import multiprocessing
import spacy
import warnings
import numpy as np
import pandas as pd

from typing import List
from requests_html import HTML
from pandas import DataFrame
from tqdm import tqdm
from num2words import num2words

from .language_dector import LanguageDetector

# Filter out annoying bs4 warning about URL in the text
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")


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

    def __init__(self, csv_file: str, stopwords: List[str] = None, num_2_word = False):
        self._df = pd.read_csv(csv_file)
        self._nlp = spacy.load("en_core_web_sm")
        self._num_2_word = num_2_word

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
            self._df['title'] = self._df['title'].apply(apply_num2words)
            self._df['content'] = self._df['content'].apply(apply_num2words)
            print(f"Final cleanup (title and content): {time.time() - start_time} sec")

        # Merge `title` and `content` column into a new column
        self._df["title_content"] = self._df["title"] + " " + self._df["content"]

    def preprocess_tags(self):
        # TODO
        pass
