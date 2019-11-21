from pygbif import species
from AttributeValueCounter import AttributeValueCounter

class PyGBIFParser:

    @staticmethod
    def parse(name, target_level, taxo_dict, debug=False):
        # Assumption is that self.taxo_dict has relevant keys and Nones as values
        taxa = list(taxo_dict.keys())

        # Rank messes with species-level lookups, so only use for higher-level searches
        # TODO Use the limit parameter for pygbif to get more records instead of default 100
        if target_level == 'Species':
            data = species.name_lookup(q=name) 
        else:
            data = species.name_lookup(q=name, rank=target_level) 

        results = data['results']
        if debug:
            print(results)

        missing_identifier = "N/A"
        if len(results) > 0: # If data was returned by pygbif
            avc = AttributeValueCounter(results,missing=missing_identifier)

            # slice to exclude levels more specific than the target
            #relevant_levels = Entry.taxon_levels[:Entry.taxon_levels.index(target_level)+1]
            relevant_levels = taxa[:taxa.index(target_level)+1]

            for level in relevant_levels:
                if debug:
                    print(avc.visual_summary(level.lower()))
                rankings = avc[level.lower()]

                rankings.pop(missing_identifier) # Remove any N/A's from the results
                
                if debug:
                    print(rankings)
                taxo_dict[level] = max(rankings, key=rankings.get)
                # TODO Add some aliases so that 'Metazoa' remaps to 'Animalia' and so on

        return taxo_dict