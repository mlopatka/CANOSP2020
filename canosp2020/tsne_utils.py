import csv
import itertools
import re
import matplotlib.pyplot as plt
import chars2vec as c2v
import numpy as np

from collections import Counter
from sklearn.manifold import TSNE


def plot_tsne(embeddings, labels):
    x = []
    y = []
    for value in embeddings:
        x.append(value[0])
        y.append(value[1])

    plt.figure(figsize=(16, 16))
    for i in range(len(x)):
        plt.scatter(x[i], y[i])
        plt.annotate(labels[i], xy=(x[i], y[i]), xytext=(5, 2), textcoords="offset points", ha="right", va="bottom")
    plt.show()


def get_tags(path="./data/tickets_v2.csv"):
    with open(path) as f:
        reader = csv.reader(f)
        lines = list(reader)
        all_tags = [t.split("|") for line in lines for t in line[3:] if t]

    return list(itertools.chain.from_iterable(all_tags))


def get_tags_both_human_and_mturk(path="./data/all_annotated_tickets.csv"):
    with open(path) as f:
        reader = csv.reader(f)
        lines = list(reader)
        regular_human_tags = [t.split("|") for line in lines for t in line[3:13] if t]
        mturk_tags = [t.split("|") for line in lines for t in line[13:] if t]

    return list(itertools.chain.from_iterable(regular_human_tags)), list(itertools.chain.from_iterable(mturk_tags))


def cleanup_tags(tags, threshold=0.2, occ_threshold=100):
    """
    Return a list of filtered unique tags

    :tags: A list of tags
    :threshold: The top 20 percentile of tags (occurences) will be removed (defualt)
    :occ_threshold: Minimal number of occurences to be included
    """
    unique_tags = list(set(tags))
    tags_counter = Counter(tags)

    # Build stop "tags" list
    stop_tags = [each[0] for each in tags_counter.most_common(int(threshold * len(unique_tags)))]

    filtered_tags = [
        each for each in tags_counter.elements() if each not in stop_tags and tags_counter[each] >= occ_threshold
    ]

    unique_filtered_tags = list(set(filtered_tags))
    filtered_tags_counter = Counter(filtered_tags)
    print(f"# of tags: {len(tags)}, # of filter tags: {len(filtered_tags)}")
    print(f"# of unique tags: {len(unique_tags)}, # of unique filtered tags {len(unique_filtered_tags)}")

    most_common = filtered_tags_counter.most_common(30)
    print("Reference dict: 'Label': 'Tag'")
    print({i: most_common[i][0] for i in range(len(most_common))})
    plt.bar([str(i) for i in range(len(most_common))], [e[1] for e in most_common])
    plt.show()

    return unique_filtered_tags


def build_tsne_embeddings(tags, c2v_model=None, tsne_model=None):
    """
    Use sklearn TSNE to build embedding layer.
    :return: an Numpy array

    1. Use `char2vec` to transform tags into a 150D vectors -> (num_tags, 150)
    2. Feed word embeddings into sklearn TSNE model

    """
    if not c2v_model:
        c2v_model = c2v.load_model("train_fr_150/")

    word_embeddings = c2v_model.vectorize(tags)

    print(f"Word embedding shape: {word_embeddings.shape}")

    if not tsne_model:
        # preplexity: we should experiment with value between 5 and 50 to see different results
        # n_components: the input word embeding is a (num_words, 150) 2-D matrix
        # n_iter: number of iterations for optimization, >= 250
        # random_state: seed for random number generator
        tsne_model = TSNE(perplexity=40, n_components=2, init="pca", n_iter=2500, random_state=23)

    tsne_embeddings = tsne_model.fit_transform(word_embeddings)

    print(f"T-SNE embedding shape: {tsne_embeddings.shape}")

    return tsne_embeddings


if __name__ == "__main__":
    print(
        cleanup_tags(
            ["firefox-72", "firefox", "a", "a", "firefox-3333.2"],
            threshold=0,
            exclude_tags=[lambda x: re.match(r"^firefox-(.*)", x)],
        )
    )
