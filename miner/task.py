from openai import OpenAI

from typing import Dict
import requests
import random
from miner.extract import SyntheticData
import logging
from constants import MODEL_NAME

logger = logging.getLogger(__name__)

def chunk(text, sep, n_chunks=None):
    # choose a random chunk from the article
    chunks = [chunk for chunk in text.split(sep) if chunk.strip()]
    # select a subsequence of paragraphs
    if n_chunks is None:
        n_chunks = random.randint(1, len(chunks))

    start_chunk = random.randint(0, len(chunks) - n_chunks)

    return sep.join(chunks[start_chunk : start_chunk + n_chunks])

class Task:
    def __init__(self, client: OpenAI):
        self.client = client

    def run(self) -> SyntheticData:
        return self._run()
    
    def _run(self) -> SyntheticData:
        raise NotImplementedError()

    def get_task(self):
        raise NotImplementedError()


    
class WikipediaSummarization(Task):
    def __init__(
        self,
        client: OpenAI,
        min_length_words: int = 250,
        min_length_bytes: int = 1000,
        max_tries: int = 10,
        min_backlinks: int = 1,
    ):
        super().__init__(client)
        self.url = "https://en.wikipedia.org/w/api.php"
        self.min_length_words = min_length_words
        self.min_length_bytes = min_length_bytes
        self.max_tries = max_tries
        self.min_backlinks = min_backlinks

    def get_task(self):
        return "wikipedia_summarization"

    def _run(self) -> SyntheticData:
        article = self.get_random_wikipedia_article()
        logger.info(f"Generating wikipedia summarization task for {article['title']}...")
        content = self.get_wikipedia_article_content(article["title"])[None]

        questions = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Your responsibility is to generate a question that could be answered by the content asked by the user."},
                {"role": "user", "content": content},
            ],
        )

        answers = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Your responsibility is to answer the following question based on the content provided."},
                {"role": "user", "content": """
                Question: {question}
                Context: {context}
                 """.format(question=questions.choices[0].message.content, context=content)},
            ],
        )

        return SyntheticData(input=questions.choices[0].message.content, output=answers.choices[0].message.content, context={"content": content, "title": article["title"]}, task=self.get_task())


    def get_random_wikipedia_article(self) -> Dict:
        """sample random wikipedia article

        Args:
            min_length (int, optional): min number of words in article. Defaults to 1000.
            min_backlinks (int, optional): backlink is a hyperlink from one webpage to another webpage. Defaults to 1.
        """

        # Parameters for the API request
        params = {
            "action": "query",
            "format": "json",
            "prop": "info|linkshere|categories|categoryinfo|extracts",
            "generator": "random",
            "grnnamespace": 0,  # Namespace 0 indicates articles
            "grnlimit": 10,  # Number of random articles to fetch
            "inprop": "url|displaytitle|length",  # Requesting URL, title, and length of the page
            "lhprop": "pageid",  # Properties for links here (backlinks)
            "lhlimit": "max",  # Maximum number of backlinks to retrieve
            "exlimit": "max",  # Get extracts for each page
            "cllimit": "max",  # Get all categories for each page
        }

        tries = 0
        while tries < self.max_tries:
            # TODO: to avoid blocking from Wikipedia, we should provide a headers argument, where headers = {'User-Agent': 'Bittensor/0.0 (https://Bittensor.org; someone@opentensor.dev)'}
            response = requests.get(self.url, params=params)
            tries += 1

            data = response.json()
            if not data.get("query"):
                continue

            for page_id, page_info in data["query"]["pages"].items():
                length = page_info.get("length", 0)
                backlinks = len(page_info.get("linkshere", []))
                categories = [
                    cat.get("title", "").strip("Category:")
                    for cat in page_info.get("categories", [{}])
                ]
                # filter out any mention of articles
                categories = [cat for cat in categories if "article" not in cat.lower()]
                extract = page_info.get("extract")

                if (
                    length >= self.min_length_bytes
                    and backlinks >= self.min_backlinks
                    and extract
                ):  # and views >= min_views:
                    return {
                        "title": page_info["title"],
                        "url": page_info["fullurl"],
                        "length": length,
                        "extract": extract,
                        "backlinks": backlinks,
                        "categories": categories,
                    }

        raise Exception(
            f"Could not find an article with length >= {self.min_length_bytes} and backlinks >= {self.min_backlinks} after {self.max_tries} tries."
        )

    def get_wikipedia_article_content(self, title: str) -> str:
        """Return wikipedia article content

        Args:
            title (str): title of the article
            remove_headers (bool, optional): remove the headers in the content body. Defaults to False.

        Returns:
            str: article content
        """
        # Parameters for the API request to get article content
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True,  # Get plain text content
        }

        # Making the API request
        # TODO: to avoid blocking from Wikipedia, we should provide a headers argument, where headers = {'User-Agent': 'Bittensor/0.0 (https://Bittensor.org; someone@opentensor.dev)'}
        response = requests.get(self.url, params=params)
        data = response.json()

        # Extracting the page content
        page = next(iter(data["query"]["pages"].values()))
        content = page.get("extract", "Content not found.")

        text = {None: ""}
        section = None
        for line in content.split("\n"):
            if line.startswith("==") and line.endswith("=="):
                section = line.strip("=").strip()
                text[section] = ""
                continue
            text[section] += line + "\n"

        return text
