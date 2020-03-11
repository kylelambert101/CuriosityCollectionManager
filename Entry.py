import re
import json
import logging
import textwrap
from pygbif import species
from functools import total_ordering
from PyGBIFParser import PyGBIFParser
from json import JSONEncoder


@total_ordering
class Entry:
    taxon_levels = [
        'Kingdom',
        'Phylum',
        'Class',
        'Order',
        'Family',
        'Genus',
        'Species'
    ]

    def __init__(self, text):
        logging.debug('Creating new Entry from text:\n' +
                      textwrap.indent(text, "\t+\t", lambda line: True))
        self.text = text
        self.title = Entry.parse_title(self.text)
        # taxonomy_labels will be a list of tuples: (level, searchable text)
        self.taxonomy_labels = Entry.parse_taxonomy_labels(self.text)
        # Initialize taxonomy as an empty dict
        self.taxonomy = dict(
            zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))

    def get_displayable_text(self):
        return re.sub(r'\n+', '\n',  # de-duplicate consecutive newlines
                      re.sub(r'\s(!\[\]\(.+\))\s', '\n',  # Remove image ref lines
                             self.text))

    @staticmethod
    def parse_title(text):
        # pull the first line of text out as the title
        lines = text.split('\n')
        title = lines[0].replace('\\', '').replace('# ', '')
        logging.info(f'Parsed Entry Title: "{title}"')
        return title

    @staticmethod
    def parse_taxonomy_labels(text):
        labels = []
        logging.info('Parsing Entry for Taxonomy Labels...')
        # Try to find taxa in reverse hierarchical order
        for level in reversed(Entry.taxon_levels):
            pattern = f'{level[0]}: ?(.+)'  # e.g. Family -> 'F: ?(.+)'
            match = re.search(pattern, text)
            if match is not None:
                value = match.group(1)
                logging.debug(
                    f'Found taxonomy pattern match: "{match.group(0)}"')
                # Strip symbols from the match
                value = re.sub(r'[^\w\s]', '', value)
                logging.debug(f'Cleaned taxonomy pattern match: "{value}"')
                labels.append((level, value))
        # labels will have (level,text) tuples in reverse order - lower levels first
        return labels

    def __str__(self):
        return f'Title: {self.title}\nTaxonomy: {json.dumps(self.taxonomy,indent=4)}'

    def _is_valid_operand(self, other):
        return (
            hasattr(other, "taxonomy")
            and
            hasattr(other, "text")
            and
            other.taxonomy.keys() == self.taxonomy.keys()
        )

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.text == other.text

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        for level in Entry.taxon_levels:
            if self.taxonomy[level] != other.taxonomy[level]:
                return str(self.taxonomy[level]) < str(other.taxonomy[level])


class EntryJSONEncoder(JSONEncoder):

    def default(self, object):
        if isinstance(object, Entry):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)


# TODO It would be an interesting test to fetch taxonomy for all matches
# instead of just the lowest level match, and then compare the resulting
# taxonomy dictionaries to see if they match up.
# E.g. F: Calopterygidae and S: Ebony Jewelwing
# Do both taxonomy dictionaries have the same Kingdom, Phylum, Class, etc?
# This could be a useful automatic check when parsing.
