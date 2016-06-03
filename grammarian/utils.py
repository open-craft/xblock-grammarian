# -*- coding: utf-8 -*-
"""
Auxiliary utility methods used for the Grammarian XBlock
"""

from __future__ import unicode_literals
import re


def split_sentence_into_parts(text):
    """
    Split the 'text' (the sentence that contains an error) into discrete parts. The learner
    must identify which one of these parts is incorrect.

    If a part or sequence of parts is surrounded by square brackets, the square brackets will be
    removed from the result and the index of that part will be part of the return value.

    >>> split_sentence_into_parts("To boldy go")
    (['To', ' ', 'boldy', ' ', 'go'], None)

    >>> split_sentence_into_parts("[To] boldy go")
    (['To', ' ', 'boldy', ' ', 'go'], 0)

    >>> split_sentence_into_parts("To[ ]boldy go")
    (['To', ' ', 'boldy', ' ', 'go'], 1)

    >>> split_sentence_into_parts("To [boldy] go")
    (['To', ' ', 'boldy', ' ', 'go'], 2)

    >>> split_sentence_into_parts("To [boldy go]")
    (['To', ' ', 'boldy go'], 2)

    >>> split_sentence_into_parts("[It's] surface was cracked.")
    (["It's", ' ', 'surface', ' ', 'was', ' ', 'cracked', '.'], 0)

    >>> split_sentence_into_parts("What [affect] has it had on your life, that you've noticed?")
    (['What', ' ', 'affect', ' ', 'has', ' ', 'it', ' ', 'had', ' ', 'on', ' ', 'your', ' ',
    'life', ', ', 'that', ' ', "you've", ' ', 'noticed', '?'], 2)

    """
    parts = [part for part in re.split("([^\w'\-\[\]]+|\[|\])", text) if part != '']
    try:
        left_bracket_index = parts.index('[')
        right_backet_index = parts.index(']', left_bracket_index)
    except ValueError:
        selected_part_index = None
    else:
        selected_part_index = left_bracket_index
        selected_text = ''.join(parts[left_bracket_index+1:right_backet_index])
        parts = parts[:left_bracket_index] + [selected_text] + parts[right_backet_index+1:]
    return parts, selected_part_index
