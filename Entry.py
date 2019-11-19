import re, json
from pygbif import species
from AttributeValueCount import AttributeValueCounter
from functools import total_ordering

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
        # Try to find taxa in reverse hierarchical order
        for level in reversed(Entry.taxon_levels):
            pattern = f'{level[0]}: ?(.+)' # e.g. Family -> 'F: ?(.+)'
            match = re.search(pattern,text)
            if match is not None:
                value = match.group(1).replace('#','')

                # Strip symbols from the match
                value = re.sub(r'[^\w\s]','',value)

                return Entry.fetch_taxonomy(target_level=level, value=value)
        # If no match was ever found, then return taxonomy dict of Nones
        return dict(zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))

    @staticmethod
    def parse_title(text):
        #pull the first line of text out as the title
        lines = text.split('\n')
        title = lines[0].replace('\\','').replace('# ','')
        return title

    @staticmethod
    # TODO this should probably be moved out to a different class. 
    # TODO Something is going wrong with some species (e.g. Apis Mellifera) - fix it. 
    def fetch_taxonomy(target_level, value):
        best_guesses = dict(zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))

        # Rank messes with species-level lookups, so only use for higher-level searches
        # TODO Use the limit parameter for pygbif to get more records instead of deafault 100
        if target_level == 'Species':
            data = species.name_lookup(q=value) 
        else:
            data = species.name_lookup(q=value, rank=target_level) 
        results = data['results']
        if len(results) > 0: # If data was returned by pygbif
            avc = AttributeValueCounter(results)

            # slice to exclude levels more specific than the target
            relevant_levels = Entry.taxon_levels[:Entry.taxon_levels.index(target_level)+1]

            for level in relevant_levels:
                rankings = avc[level.lower()]
                best_guesses[level] = max(rankings, key=rankings.get)
                # TODO Add some aliases so that 'Metazoa' remaps to 'Animalia' and so on

        return best_guesses
    
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
                                               

# TODO Taxonomy class
'''
Taxonomy.SPECIES
Taxonomy.GENUS
and so on
Taxonomy.Levels = List of all of those constants
Maybe not. 

Taxon class?
Name = 'Kingdom'
Aliases = {'Animalia': 'Animalia', 'Metazoa': 'Animalia',...}

Entry would hold the list of taxonomic levelspreerty[' <-- Monty

Okay, I've got it. 
PyGBIFParser object
p = PyGBIFParser(name, target_level, taxo_dictionary)
-> Populate/return taxo_dictionary with values from pygbif search using name
and target level. name is already regex parsed out of the entry text. 
Use the keys in the taxo_dictionary to know what to pull out of pygbif
Adding the dependency prevents you from having to duplicate the taxon hierarchy
in this class. 
'''