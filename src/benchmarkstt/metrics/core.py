from benchmarkstt.schema import Schema
import logging
from benchmarkstt.diff.core import HuntMcIlroy, RatcliffObershelp
from benchmarkstt.diff.formatter import format_diff
from benchmarkstt.metrics import Base

logger = logging.getLogger(__name__)


def traversible(schema, key=None):
    if key is None:
        key = 'item'
    return [word[key] for word in schema]


def get_opcode_counts(opcodes):
    counts = dict(equal=0, replace=0, insert=0, delete=0)

    for tag, alo, ahi, blo, bhi in opcodes:
        if tag in ['equal', 'replace', 'delete']:
            counts[tag] += ahi - alo
        elif tag == 'insert':
            counts[tag] += bhi - blo

    return counts


def get_differ(a, b, differ_class):
    if differ_class is None:
        # differ_class = HuntMcIlroy
        differ_class = RatcliffObershelp
    return differ_class(traversible(a), traversible(b))


class WordDiffs(Base):
    def __init__(self, differ_class=None, dialect=None):
        self._differ_class = differ_class
        self._dialect = dialect

    def compare(self, ref: Schema, hyp: Schema):
        differ = get_differ(ref, hyp, differ_class=self._differ_class)
        a = traversible(ref)
        b = traversible(hyp)
        return format_diff(a, b, differ.get_opcodes(),
                           dialect=self._dialect,
                           preprocessor=lambda x: ' %s' % (' '.join(x),))


class WER(Base):
    """
    Item Error Rate, basically defined as:

    .. code-block :: text

        insertions + deletions + substitions
        ------------------------------------
             number of reference words

    See: https://en.wikipedia.org/wiki/Word_error_rate
    """

    # TODO: proper documenting of different modes
    MODE_STRICT = 0
    MODE_HUNT = 1

    DEL_PENALTY = 1
    INS_PENALTY = 1
    SUB_PENALTY = 1

    def __init__(self, mode=None, differ_class=None):
        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class
        if mode is self.MODE_HUNT:
            self.DEL_PENALTY = self.INS_PENALTY = .5

    def compare(self, ref: Schema, hyp: Schema):
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)
        ref_len = len(diffs.a)
        hyp_len = len(diffs.b)

        counts = get_opcode_counts(diffs.get_opcodes())

        changes = counts['replace'] * self.SUB_PENALTY + \
                  counts['delete'] * self.DEL_PENALTY + \
                  counts['insert'] * self.INS_PENALTY

        logger.getChild(type(self).__name__)\
              .debug('WER comparison, reflen: %d, hyplen: %d' , ref_len, hyp_len)

        return changes / (counts['equal'] + changes)


class DiffCounts(Base):
    def __init__(self, differ_class=None):
        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class

    def compare(self, ref: Schema, hyp: Schema):
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)
        return get_opcode_counts(diffs.get_opcodes())
