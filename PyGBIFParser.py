from pygbif import species
from AttributeValueCounter import AttributeValueCounter

class PyGBIFParser:

    @staticmethod
    # TODO Something is going wrong with some species (e.g. Apis Mellifera) - fix it. 
    def parse(name, target_level, taxo_dict):
        # Assumption is that self.taxo_dict has relevant keys and Nones as values
        taxa = list(taxo_dict.keys())

        # Rank messes with species-level lookups, so only use for higher-level searches
        # TODO Use the limit parameter for pygbif to get more records instead of default 100
        if target_level == 'Species':
            data = species.name_lookup(q=name) 
        else:
            data = species.name_lookup(q=name, rank=target_level) 

        results = data['results']

        if len(results) > 0: # If data was returned by pygbif
            avc = AttributeValueCounter(results)

            # slice to exclude levels more specific than the target
            #relevant_levels = Entry.taxon_levels[:Entry.taxon_levels.index(target_level)+1]
            relevant_levels = taxa[:taxa.index(target_level)+1]

            for level in relevant_levels:
                rankings = avc[level.lower()]
                taxo_dict[level] = max(rankings, key=rankings.get)
                # TODO Add some aliases so that 'Metazoa' remaps to 'Animalia' and so on

        return taxo_dict