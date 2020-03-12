from spacy.tokens import Doc
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException


def get_language(text, cld_results=None):
    if cld_results is None:
        cld_results = detect_language(text)
    return cld_results["language"]


def get_score(text, cld_results=None):
    if cld_results is None:
        cld_results = detect_language(text)
    return cld_results["score"]


def detect_language(text):
    try:
        detected_language = detect_langs(text.text)[0]
        return {"language": str(detected_language.lang), "score": float(detected_language.prob)}
    except LangDetectException:
        return {"language": "UNKNOWN", "score": 0.0}


class LanguageDetector(object):

    name = "cld"

    def __init__(self, attrs=("language", "language_score")):
        self._language, self._score = attrs
        Doc.set_extension(self._language, getter=get_language)
        Doc.set_extension(self._score, getter=get_score)

    def __call__(self, doc):
        """Apply the language detector as a pipeline component."""
        # Make a single call to the language detector and cache the result.
        cld_results = detect_language(doc)
        doc._.set(self._language, get_language(doc, cld_results))
        doc._.set(self._score, get_score(doc, cld_results))
        return doc
