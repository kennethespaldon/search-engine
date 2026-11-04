"""Extracts text from web pages and labels the important parts."""

from bs4 import BeautifulSoup
from bs4.element import PreformattedString

# Names for the kinds of important text a token can appear in.
TITLE = "title"
HEADING = "heading"
BOLD = "bold"

# Maps each important HTML tag to the kind of important text it marks.
IMPORTANT_TAGS = {
    "title": TITLE,
    "h1": HEADING,
    "h2": HEADING,
    "h3": HEADING,
    "b": BOLD,
    "strong": BOLD,
}


def _important_fields(text_node):
    """Returns the kinds of important text that contain this text node."""
    fields = set()
    for parent in text_node.parents:
        field = IMPORTANT_TAGS.get(parent.name)
        if field is not None:
            fields.add(field)
    return fields


def extract_text_segments(content):
    """
    Returns a list of (text, fields) pairs for the text in a page.

    fields is the set of important kinds of text (TITLE, HEADING, BOLD) that
    contain the text, and is empty for normal text.

    The lxml parser tolerates broken HTML, such as missing closing tags, and
    pages with no HTML at all, whose text is returned as normal text.

    Each text node is visited exactly once and its ancestors are checked,
    rather than searching for each important tag separately. This way, a word
    inside <h1><b>word</b></h1> is one occurrence that is both a heading and
    bold, and it isn't counted twice in the term frequency.
    """
    soup = BeautifulSoup(content, "lxml")

    # Scripts and styles hold code rather than the page's text.
    for tag in soup(["script", "style"]):
        tag.decompose()

    segments = []
    for text_node in soup.find_all(string=True):
        # Comments and doctypes are PreformattedString subclasses. They aren't
        # part of the page's text.
        if not isinstance(text_node, PreformattedString):
            segments.append((str(text_node), _important_fields(text_node)))

    return segments
