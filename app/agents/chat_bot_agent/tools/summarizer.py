from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk


class Summarizer:
    @staticmethod
    def get_summerize_result(results):
        try:  # PUNKT_TAB NOT FOUND ERROR
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt_tab")

        if not results:
            return "No results to summarize", []

        combined_text = ""
        urls = []

        for item in results:
            snippet = item.get("snippet", "")
            url = item.get("link") or item.get("url", "")
            urls.append(url)
            combined_text += f"{snippet}"

        parser = PlaintextParser.from_string(combined_text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, sentences_count=5)

        summary = " ".join(str(sentence) for sentence in summary_sentences)
        sources = "\n".join(
            f"-{item.get("link") or item.get("url","")}" for item in results
        )
        context = f"{summary}\nSources:\n{sources}"

        return context

    @staticmethod
    def get_summerize_text(text, amount=3):
        try:  # PUNKT_TAB NOT FOUND ERROR
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt_tab")

        if not text:
            return "No text to summarize", []

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, sentences_count=amount)

        return " ".join(str(sentence) for sentence in summary_sentences)
