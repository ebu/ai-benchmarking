from benchmarkstt.input.core import PlainText, File
from benchmarkstt.schema import Item, Schema
import pytest

candide_file = './resources/test/_data/candide.txt'
with open(candide_file) as f:
    candide = f.read()

candide_schema = [Item({"item": "\"There", "type": "word", "@raw": "\n\"There "}),
                  Item({"item": "is", "type": "word", "@raw": "is "}),
                  Item({"item": "a", "type": "word", "@raw": "a "}),
                  Item({"item": "concatenation", "type": "word", "@raw": "concatenation "}),
                  Item({"item": "of", "type": "word", "@raw": "of "}),
                  Item({"item": "events", "type": "word", "@raw": "events "}),
                  Item({"item": "in", "type": "word", "@raw": "in "}),
                  Item({"item": "this", "type": "word", "@raw": "this "}),
                  Item({"item": "best", "type": "word", "@raw": "best "}),
                  Item({"item": "of", "type": "word", "@raw": "of "}),
                  Item({"item": "all", "type": "word", "@raw": "all "}),
                  Item({"item": "possible", "type": "word", "@raw": "possible "}),
                  Item({"item": "worlds:", "type": "word", "@raw": "worlds:\n"}),
                  Item({"item": "for", "type": "word", "@raw": "for "}),
                  Item({"item": "if", "type": "word", "@raw": "if "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "had", "type": "word", "@raw": "had "}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "been", "type": "word", "@raw": "been "}),
                  Item({"item": "kicked", "type": "word", "@raw": "kicked "}),
                  Item({"item": "out", "type": "word", "@raw": "out "}),
                  Item({"item": "of", "type": "word", "@raw": "of "}),
                  Item({"item": "a", "type": "word", "@raw": "a "}),
                  Item({"item": "magnificent", "type": "word", "@raw": "magnificent "}),
                  Item({"item": "castle", "type": "word", "@raw": "castle "}),
                  Item({"item": "for", "type": "word", "@raw": "for "}),
                  Item({"item": "love", "type": "word", "@raw": "love "}),
                  Item({"item": "of", "type": "word", "@raw": "of\n"}),
                  Item({"item": "Miss", "type": "word", "@raw": "Miss "}),
                  Item({"item": "Cunegonde:", "type": "word", "@raw": "Cunegonde: "}),
                  Item({"item": "if", "type": "word", "@raw": "if "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "had", "type": "word", "@raw": "had "}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "been", "type": "word", "@raw": "been "}),
                  Item({"item": "put", "type": "word", "@raw": "put "}),
                  Item({"item": "into", "type": "word", "@raw": "into "}),
                  Item({"item": "the", "type": "word", "@raw": "the "}),
                  Item({"item": "Inquisition:", "type": "word", "@raw": "Inquisition: "}),
                  Item({"item": "if", "type": "word", "@raw": "if "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "had", "type": "word", "@raw": "had\n"}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "walked", "type": "word", "@raw": "walked "}),
                  Item({"item": "over", "type": "word", "@raw": "over "}),
                  Item({"item": "America:", "type": "word", "@raw": "America: "}),
                  Item({"item": "if", "type": "word", "@raw": "if "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "had", "type": "word", "@raw": "had "}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "stabbed", "type": "word", "@raw": "stabbed "}),
                  Item({"item": "the", "type": "word", "@raw": "the "}),
                  Item({"item": "Baron:", "type": "word", "@raw": "Baron: "}),
                  Item({"item": "if", "type": "word", "@raw": "if "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "had", "type": "word", "@raw": "had\n"}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "lost", "type": "word", "@raw": "lost "}),
                  Item({"item": "all", "type": "word", "@raw": "all "}),
                  Item({"item": "your", "type": "word", "@raw": "your "}),
                  Item({"item": "sheep", "type": "word", "@raw": "sheep "}),
                  Item({"item": "from", "type": "word", "@raw": "from "}),
                  Item({"item": "the", "type": "word", "@raw": "the "}),
                  Item({"item": "fine", "type": "word", "@raw": "fine "}),
                  Item({"item": "country", "type": "word", "@raw": "country "}),
                  Item({"item": "of", "type": "word", "@raw": "of "}),
                  Item({"item": "El", "type": "word", "@raw": "El "}),
                  Item({"item": "Dorado:", "type": "word", "@raw": "Dorado: "}),
                  Item({"item": "you", "type": "word", "@raw": "you "}),
                  Item({"item": "would", "type": "word", "@raw": "would\n"}),
                  Item({"item": "not", "type": "word", "@raw": "not "}),
                  Item({"item": "be", "type": "word", "@raw": "be "}),
                  Item({"item": "here", "type": "word", "@raw": "here "}),
                  Item({"item": "eating", "type": "word", "@raw": "eating "}),
                  Item({"item": "preserved", "type": "word", "@raw": "preserved "}),
                  Item({"item": "citrons", "type": "word", "@raw": "citrons "}),
                  Item({"item": "and", "type": "word", "@raw": "and "}),
                  Item({"item": "pistachio-nuts.\"", "type": "word", "@raw": "pistachio-nuts.\"\n\n"}),
                  Item({"item": "\"All", "type": "word", "@raw": "\"All "}),
                  Item({"item": "that", "type": "word", "@raw": "that "}),
                  Item({"item": "is", "type": "word", "@raw": "is "}),
                  Item({"item": "very", "type": "word", "@raw": "very "}),
                  Item({"item": "well,\"", "type": "word", "@raw": "well,\" "}),
                  Item({"item": "answered", "type": "word", "@raw": "answered "}),
                  Item({"item": "Candide,", "type": "word", "@raw": "Candide, "}),
                  Item({"item": "\"but", "type": "word", "@raw": "\"but "}),
                  Item({"item": "let", "type": "word", "@raw": "let "}),
                  Item({"item": "us", "type": "word", "@raw": "us "}),
                  Item({"item": "cultivate", "type": "word", "@raw": "cultivate "}),
                  Item({"item": "our", "type": "word", "@raw": "our\n"}),
                  Item({"item": "garden.\"", "type": "word", "@raw": "garden.\"\n"})]


@pytest.mark.parametrize('cls,args', [
    [PlainText, [candide]],
    [File, [candide_file]],
    [File, [candide_file, 'infer']],
    [File, [candide_file, 'plaintext']],
])
def test_file(cls, args):
    assert list(cls(*args)) == candide_schema
    assert Schema(cls(*args)) == candide_schema


def test_exceptions():
    with pytest.raises(ValueError) as e:
        File('noextension')
    assert 'without an extension' in str(e)

    with pytest.raises(ValueError) as e:
        File('unknownextension.thisisntknowm')
    assert 'thisisntknowm' in str(e)
