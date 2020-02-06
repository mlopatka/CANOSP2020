import spacy

from textpipe import doc, pipeline


class Preprocess:
    """
    Preprocess text documents with textpipe and sPacy.

    >>> preprocessor = Preprocess()
    >>> preprocessor.preprocess(<p>hello world! Liking</p>)
    hello world like
    """

    def __init__(self, lemmatization=True, remove_punct=True, remove_stopword=True):
        self._pipeline = pipeline.Pipeline(["CleanText"])
        self._pipeline.register_operation("CustomOp", self._custom_op)
        self._pipeline.steps.append(
            (
                "CustomOp",
                {"Lemmatization": lemmatization, "RemovePunct": remove_punct, "RemoveStopword": remove_stopword},
            )
        )

    @staticmethod
    def _custom_op(doc: doc.Doc, context=None, settings=None, **kwargs):
        # TODO
        # add multi lang/lm support
        # return None for now
        if doc.detect_language()[1] != "en":
            print("Cannot determine input language.")
            return None

        spacy_doc = doc._spacy_doc
        spacy_nlp = doc._spacy_nlps["en"][None]

        # TODO
        # speed things up
        # fine tune configurable pre-processing later on
        spacy_doc = spacy_nlp(" ".join([token.lemma_ for token in spacy_doc if not (token.is_punct or token.is_stop)]))

        # if settings["Lemmatization"]:
        #     spacy_doc = spacy_nlp(" ".join([token.lemma_ for token in spacy_doc]))

        # if settings["RemovePunct"]:
        #     spacy_doc = spacy_nlp(" ".join([token.text for token in spacy_doc if not token.is_punct]))

        # if settings["RemoveStopword"]:
        #     spacy_doc = spacy_nlp(" ".join([token.text for token in spacy_doc if not token.is_stop]))

        return spacy_doc

    def preprocess(self, text) -> spacy.tokens.doc.Doc:
        try:
            text = self._pipeline(text)["CustomOp"]
            return text
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    sample_text = "<p>hello world! Liking</p>"
    preprocessor = Preprocess()
    processed_text = preprocessor.preprocess(sample_text)
