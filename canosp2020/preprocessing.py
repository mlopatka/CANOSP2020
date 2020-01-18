import spacy

from textpipe import doc, pipeline


class Preprocess:
    """
    Preprocess text documents with textpipe and sPacy.

    >>> preprocessor = Preprocess()
    >>> preprocessor.preprocess(<p>hello world! Liking</p>)
    hello world like
    """

    def __init__(self, lemmatization=True, remove_punct=True):
        self._pipeline = pipeline.Pipeline(["CleanText"])
        self._pipeline.register_operation("CustomOp", self._custom_op)
        self._pipeline.steps.append(("CustomOp", {"Lemmatization": lemmatization, "RemovePunct": remove_punct}))

    @staticmethod
    def _custom_op(doc: doc.Doc, context=None, settings=None, **kwargs):
        spacy_doc = doc._spacy_doc
        # TODO
        # add multi lang/lm support
        spacy_nlp = doc._spacy_nlps["en"][None]

        if settings["Lemmatization"]:
            spacy_doc = spacy_nlp(" ".join([token.lemma_ for token in spacy_doc]))

        if settings["RemovePunct"]:
            spacy_doc = spacy_nlp(" ".join([token.text for token in spacy_doc if not token.is_punct]))

        return spacy_doc

    def preprocess(self, text) -> spacy.tokens.doc.Doc:
        return self._pipeline(text)["CustomOp"]


if __name__ == "__main__":
    sample_text = "<p>hello world! Liking</p>"
    preprocessor = Preprocess()
    processed_text = preprocessor.preprocess(sample_text)
