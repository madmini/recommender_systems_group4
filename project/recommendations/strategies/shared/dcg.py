import math
from typing import Iterable, Union, Mapping, Any


def index_reverse_lookup_dict(items: Iterable):
    return dict((item, index) for index, item in enumerate(items))


def dcg_similarity(actual: Iterable, reference: Union[Mapping[Any, int], Iterable]) -> float:
    """ Calculates similarity between two lists based on the Discounted Cumulative Gain metric.

    Also accepts a pre-calculated reverse lookup dict for the reference parameter.
    """
    if not isinstance(reference, Mapping):
        # build reverse lookup dict
        reference = index_reverse_lookup_dict(reference)

    ref_len = len(reference)

    rel: list = list()
    for item in actual:
        pos: int

        if item in reference:
            # calculate the relevance score of an item as its inverted position (len - index) in the reference list
            pos = ref_len - reference[item]
        else:
            # define relevance score for items not in reference as zero
            pos = 0

        rel.append(pos)

    # note that DCG is actually preferable to nDCG (normalized DCG) in this context
    # as the list length does not matter, only the number of relevant items
    return dcg(rel)


def dcg(relevances: list) -> float:
    """Calculates the Discounted Cumulative Gain for given relevance scores.

    Gives a notion of how well the list is "ordered" by relevance.
    Note that when comparing DCGs for truncated lists (e.g. the top N search results)
    with different lengths, the normalized DCG should be used.
    """
    result: float = 0
    for index, item in enumerate(relevances):
        # dcg = sum_{i=1}^p rel_i / log_2(i+1)
        # where p is the rank position (the number of results to take into account)
        # "+ 2" as index starts with 0
        result += item / math.log2(index + 2)

    return result