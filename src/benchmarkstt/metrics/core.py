from benchmarkstt.schema import Schema
import logging
import json
from benchmarkstt.diff import Differ
from benchmarkstt.diff.core import RatcliffObershelp
from benchmarkstt.diff.formatter import format_diff
from benchmarkstt.metrics import Metric
from collections import namedtuple
# from benchmarkstt.modules import LoadObjectProxy
import editdistance

logger = logging.getLogger(__name__)

OpcodeCounts = namedtuple('OpcodeCounts',
                          ('equal', 'replace', 'insert', 'delete'))


def traversible(schema, key=None):
    if key is None:
        key = 'item'
    return [word[key] for word in schema]


def get_opcode_counts(opcodes) -> OpcodeCounts:
    counts = OpcodeCounts(0, 0, 0, 0)._asdict()
    for tag, alo, ahi, blo, bhi in opcodes:
        if tag == 'equal':
            counts[tag] += ahi - alo
        elif tag == 'insert':
            counts[tag] += bhi - blo
        elif tag == 'delete':
            counts[tag] += ahi - alo
        elif tag == 'replace':
            ca = ahi - alo
            cb = bhi - blo
            if ca < cb:
                counts['insert'] += cb - ca
                counts['replace'] += ca
            elif ca > cb:
                counts['delete'] += ca - cb
                counts['replace'] += cb
            else:
                counts[tag] += ahi - alo
    return OpcodeCounts(counts['equal'], counts['replace'], counts['insert'], counts['delete'])


def get_differ(a, b, differ_class: Differ):
    if differ_class is None:
        # differ_class = HuntMcIlroy
        differ_class = RatcliffObershelp
    return differ_class(traversible(a), traversible(b))


class WordDiffs(Metric):
    """
    Present differences on a per-word basis

    :param dialect: Presentation format. Default is 'ansi'.
    :example dialect: 'html'
    :param differ_class: For future use.
    """

    def __init__(self, dialect=None, differ_class: Differ = None):
        self._differ_class = differ_class
        self._dialect = dialect

    def compare(self, ref: Schema, hyp: Schema):
        differ = get_differ(ref, hyp, differ_class=self._differ_class)
        a = traversible(ref)
        b = traversible(hyp)
        return format_diff(a, b, differ.get_opcodes(),
                           dialect=self._dialect,
                           preprocessor=lambda x: ' %s' % (' '.join(x),))


class WER(Metric):
    """
    Word Error Rate, basically defined as::

        insertions + deletions + substitions
        ------------------------------------
             number of reference words

    See: https://en.wikipedia.org/wiki/Word_error_rate

    Calculates the WER using one of two algorithms:

    [Mode: 'strict' or 'hunt'] Insertions, deletions and
    substitutions are identified using the Hunt–McIlroy
    diff algorithm. The 'hunt' mode applies 0.5 weight to
    insertions and deletions. This algorithm is the one
    used internally by Python.
    See https://docs.python.org/3/library/difflib.html

    [Mode: 'levenshtein'] In the context of WER, Levenshtein
    distance is the minimum edit distance computed at the
    word level. This implementation uses the Editdistance
    c++ implementation by Hiroyuki Tanaka:
    https://github.com/aflc/editdistance. See:
    https://en.wikipedia.org/wiki/Levenshtein_distance

    :param mode: 'strict' (default), 'hunt' or 'levenshtein'.
    :param differ_class: For future use.
    """

    # WER modes
    MODE_STRICT = 'strict'
    MODE_HUNT = 'hunt'
    MODE_LEVENSHTEIN = 'levenshtein'

    DEL_PENALTY = 1
    INS_PENALTY = 1
    SUB_PENALTY = 1

    def __init__(self, mode=None, differ_class: Differ = None):
        self._mode = mode
        if mode == self.MODE_LEVENSHTEIN:
            return

        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class
        if mode == self.MODE_HUNT:
            self.DEL_PENALTY = self.INS_PENALTY = .5

    def compare(self, ref: Schema, hyp: Schema) -> float:
        if self._mode == self.MODE_LEVENSHTEIN:
            ref_list = [i['item'] for i in ref]
            total_ref = len(ref_list)
            if total_ref == 0:
                return 1
            return editdistance.eval(ref_list, [i['item'] for i in hyp]) / total_ref

        diffs = get_differ(ref, hyp, differ_class=self._differ_class)

        counts = get_opcode_counts(diffs.get_opcodes())

        changes = counts.replace * self.SUB_PENALTY \
            + counts.delete * self.DEL_PENALTY \
            + counts.insert * self.INS_PENALTY

        total_ref = counts.equal + counts.replace + counts.delete
        if total_ref == 0:
            return 1
        return changes / total_ref


class DiffCounts(Metric):
    """
    Get the amount of differences between reference and hypothesis
    """

    def __init__(self, differ_class: Differ = None):
        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class

    def compare(self, ref: Schema, hyp: Schema) -> OpcodeCounts:
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)
        return get_opcode_counts(diffs.get_opcodes())


class BEER(Metric):
    """
    Bag of Entities Error Rate, BEER, is defined as the error rate per entity with a bag of words approach :

    ne_hyp = number of detection of the entity in the hypothesis file
    ne_ref = number of detection of the entity in the reference file

                      abs(ne_hyp - ne_ref)
    BEER (entity) =  ---------------------
                           ne_ref

    The average BEER for a set of N entities is defined as the average of the BEER for the set of entities :

                                          1
    Av_BEER ([entity_1, ... entity_N) =  ---- (BEER (entity_1) ... BEER (entity_1))
                                          N

    The average Weighted BEER for a set of N entities is defined as the weighted average of the BEER for the set of
    entities :

    Av_WBEER ([entity_1, ... entity_N) =  w_1*BEER (entity_1)*L1/L ... w_N*BEER (entity_1))*LN/L
    with
    L1 =  number of occurences of entity 1 in the reference document
    L = L1 + ... + LN
    and
    w_1 + ... + w_N = 1

    """
    def __init__(self, entities_file=''):
        """
        """
        self._weight = []
        self._entities = []

        if entities_file.endswith('.json'):
            with open(entities_file) as f:
                data = json.load(f)
            self._entities = list(data.keys())
            weight = list(data.values())
            weight = [0 if w < 0 else w for w in weight]

            # normalized the sum of the weights to 1
            # after assignment when the file is not red
            sw = sum(weight)
            if sw > 0:
                self._weight = [w / sw for w in weight]
            return

        return

    def get_weight(self):
        return self._weight

    def set_weight(self, weight):

        weight = [0 if w < 0 else w for w in weight]
        sw = sum(weight)
        if sw > 0:
            self._weight = [w / sw for w in weight]

    def get_entities(self):
        return self._entities

    def set_entities(self, entities):
        self._entities = entities

    # find the position of one entity
    # an entity can contain more than one word
    @staticmethod
    def __find_pattern(search_list, complex_entity):
        entity = ''.join(complex_entity).split(' ')
        le = len(entity)
        # complex_entity = [entity1 entity2 ...]
        # the cursor sweep complex_entity to find consecutive entities entity1 ... entity2
        cursor = 0
        idx_found = []
        for idx, elt in enumerate(search_list):
            if elt == entity[cursor]:
                cursor += 1
                if cursor == le:
                    idx_found.append([idx for idx in range(idx - le + 1, idx - le + 1 + le)])
                    cursor = 0
            else:
                cursor = 0
        return idx_found

    # generate a list containing the detected entities in list_parsed
    @staticmethod
    def __generate_list_entity(self, list_parsed):

        list_entity = []
        index_entities = []
        entities = self._entities
        for entity in entities:
            index_entity = self.__find_pattern(list_parsed, entity)
            index_entities.extend(index_entity)

        # sort on the position of the first part of the entity
        index_entities.sort(key=lambda l: l[0])

        # copy-past the entity found in the list
        for k_list in index_entities:
            list_entity.append(' '.join(list_parsed[k_list[0]:k_list[-1] + 1]))

        return list_entity

    # computes the BEER
    @staticmethod
    def compute_beer(self, list_hypothesis_entity, list_reference_entity):
        beer = {}
        beer_av = 0
        entities = self._entities
        for idx, entity in enumerate(entities):
            count_hypothesis = list_hypothesis_entity.count(entity)
            count_ref = list_reference_entity.count(entity)
            beer_entity = 0
            if count_ref != 0:
                beer_entity = round(abs(count_ref - count_hypothesis) / count_ref, 3)
                # accumulate the distance per entity
                beer_av += abs(count_ref - count_hypothesis) * self._weight[idx]
            beer[entity] = {'beer': beer_entity, 'occurrence_ref': count_ref}

        l_ref = len(list_reference_entity)
        if l_ref > 0:
            beer_av = round(beer_av / l_ref, 3)
        else:
            beer_av = 0
        beer['w_av_beer'] = {'beer': beer_av, 'occurrence_ref': l_ref}
        return beer

    def compare(self, ref: Schema, hyp: Schema):

        ref_list = [i['item'] for i in ref]
        total_ref = len(ref_list)
        if total_ref == 0:
            return 1
        hyp_list = [i['item'] for i in hyp]

        # entities = self._entities

        # extract the entities
        list_hypothesis_entity = self.__generate_list_entity(self, hyp_list)
        list_reference_entity = self.__generate_list_entity(self, ref_list)
        # compute the score
        wer_entity = self.compute_beer(self, list_hypothesis_entity, list_reference_entity)
        return wer_entity

# For a future version
# class ExternalMetric(LoadObjectProxy, Base):
#     """
#     Automatically loads an external metric class.
#
#     :param name: The name of the metric to load (eg. mymodule.metrics.MyOwnMetricClass)
#     """
