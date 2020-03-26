"""
Usage: word2vec.py [OPTIONS]

Options:
  --input_file TEXT       Path to input CSV file.
  --output_file TEXT      Path to save output genism model.
  --output_bin_file TEXT  Path to save output word2vec format model.
  --min_count INTEGER     Ignores all words with total frequency lower than
                          this.
  --size INTEGER          Dimension of the word vectors.
  --window INTEGER        Maximum distance between the current and predicted
                          word within a sentence.
  --workers INTEGER       Number of worker threads to train the model. Default
                          to number of cores
  --help                  Show this message and exit.
"""

import os
import sys
import argparse
import multiprocessing
import click
import spacy
import pandas as pd
import numpy as np

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec

nlp = spacy.load("en_core_web_sm")

TITLE_CONTENT = "title_content"


@click.command()
@click.option("--input_file", default="data/tickets_preprocessed.csv", help="Path to input CSV file.")
@click.option("--output_file", default="data/tickets_word2vec.model", help="Path to save output genism model.")
@click.option(
    "--output_bin_file", default="data/tickets_word2vec.bin", help="Path to save output word2vec format model."
)
@click.option("--min_count", default=1, help="Ignores all words with total frequency lower than this.")
@click.option("--size", default=150, help="Dimension of the word vectors.")
@click.option("--window", default=5, help="Maximum distance between the current and predicted word within a sentence.")
@click.option(
    "--workers",
    default=multiprocessing.cpu_count(),
    help="Number of worker threads to train the model. Default to number of cores",
)
def main(input_file, output_file, output_bin_file, min_count, size, window, workers):
    if not os.path.exists(input_file):
        print("Input file does not exist.", file=sys.stderr)
        sys.exit(1)

    # Load csv file and merge title and content column
    df = pd.read_csv(input_file)
    df[TITLE_CONTENT] = df["title"] + " " + df["content"]
    df[TITLE_CONTENT].replace("", np.nan, inplace=True)
    df.dropna(subset=[TITLE_CONTENT], inplace=True)
    docs = list(
        nlp.pipe(df["title_content"], disable=["tagger", "parser", "ner"], n_process=multiprocessing.cpu_count())
    )
    sents = [[token.text for token in doc] for doc in docs]

    # Train word2vec model
    model = Word2Vec(sents, min_count=min_count, size=size, workers=workers, window=window)

    # Save model
    model.save(output_file)
    model.wv.save_word2vec_format(output_bin_file)


if __name__ == "__main__":
    # main()
    model = Word2Vec.load("data/tickets_word2vec.model")
