import re
import spacy
from textpipe import doc, pipeline
from textpipe.doc import Doc
from typing import Callable

class Preprocess:
    """
    Preprocess text documents with textpipe and sPacy.

    >>> preprocessor = Preprocess()
    >>> preprocessor.preprocess(<p>hello world! Liking</p>)
    hello world like
    """

    def __init__(self, custom_op: Callable = None):
        """
        :custom_op: See below _custom_op as example
        """
        self._pipeline = pipeline.Pipeline([])
        if not custom_op:
            self._pipeline.register_operation("CustomOp", self._custom_op)
            self._pipeline.steps.append(("CustomOp", {}))
        else:
            self._pipeline.register_operation("CustomOp", custom_op)
            self._pipeline.steps.append(("CustomOp", {}))

    @staticmethod
    def _custom_op(doc: doc.Doc, context=None, settings=None, **kwargs):
        """
        Default custom textpipe operation
            - Strip HTML tags
            - Lemmatization
            - Remove stop words
            - Remove punctuations
        If encounter unsupported input lanauage, return None
        """
        # TODO
        # add multi lang/lm support
        # return None for now
        if doc.detect_language()[1] != "en":
            # do some manual regex preprocessing and re-try
            text = text.strip()  # remove whitespaces in the front and the end
            text = re.sub("</?.*?>", " <> ", doc.raw)  # remove tags
            text = re.sub("(\\d|\\W)+", " ", text)  # remove special chars and digits
            text = re.sub(r'[.|,|)|(|\|/|?|!|\'|"|#]', r" ", text)  # remove any punctuation
            doc = Doc(raw=text)
            if doc.detect_language()[1] != "en":
                print("Cannot determine input language.")
                return None

        spacy_doc = doc._spacy_doc
        spacy_nlp = doc._spacy_nlps["en"][None]

        # default clean_text method, strip HTML tags and lower case
        raw_text = doc.clean.lower()

        # apply lemmatization
        # remove punct and stop words
        spacy_doc = spacy_nlp(raw_text)
        spacy_doc = spacy_nlp(" ".join([token.lemma_ for token in spacy_doc if not (token.is_punct or token.is_stop)]))

        return spacy_doc

    def preprocess(self, text) -> spacy.tokens.doc.Doc:
        try:
            text = self._pipeline(text)
            return text["CustomOp"]
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    sample_text = "<p>Hello World! This is a sample text.</p>"
    preprocessor = Preprocess()
    processed_text = preprocessor.preprocess(sample_text)
    print(processed_text)
