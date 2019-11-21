import re, json
from pygbif import species
from functools import total_ordering
from PyGBIFParser import PyGBIFParser

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
        self.text = text
        self.title = Entry.parse_title(self.text)
        self.taxonomy = Entry.parse_taxonomy(self.text)

    def get_displayable_text(self):
        return re.sub(r'\n+','\n', # de-duplicate consecutive newlines
                    re.sub(r'\s(!\[\]\(.+\))\s','\n', # Remove image ref lines
                        self.text))

    @staticmethod
    def parse_taxonomy(text):
        best_guesses = dict(zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))
        # Try to find taxa in reverse hierarchical order
        for level in reversed(Entry.taxon_levels):
            pattern = f'{level[0]}: ?(.+)' # e.g. Family -> 'F: ?(.+)'
            match = re.search(pattern,text)
            if match is not None:
                value = match.group(1)

                # Strip symbols from the match
                value = re.sub(r'[^\w\s]','',value)
                best_guesses = PyGBIFParser.parse(name=value,target_level=level, taxo_dict=best_guesses)
        return best_guesses

    @staticmethod
    def parse_title(text):
        #pull the first line of text out as the title
        lines = text.split('\n')
        title = lines[0].replace('\\','').replace('# ','')
        return title
    
    def __str__(self):
        return f'Text: {self.get_displayable_text()}\nTaxonomy: {json.dumps(self.taxonomy,indent=4)}'

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

# TODO It would be an interesting test to fetch taxonomy for all matches 
# instead of just the lowest level match, and then compare the resulting
# taxonomy dictionaries to see if they match up. 
# E.g. F: Calopterygidae and S: Ebony Jewelwing
# Do both taxonomy dictionaries have the same Kingdom, Phylum, Class, etc?
# This could be a useful automatic check when parsing.

# TODO Throw in some debug options for printing out more info
# Especially extra info about how the taxonomy was parsed out
# Like the visual summary function in AttributeValueCount

# TODO An optional time saver would be to skip taxonomy assignment in the 
# constructor so that you get get a list of unassigned entries. Then in 
# the calling program or container, you can get the unique matches 
# (regex anchors) from the full collection of entries and just call the 
# api on those. It would eliminate a few duplicate calls at least. 