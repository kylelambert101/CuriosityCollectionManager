import logging
from pygbif import species
from AttributeValueCounter import AttributeValueCounter

class PyGBIFParser:

    @staticmethod
    def parse(name, target_level, taxo_dict):
        # Assumption is that self.taxo_dict has relevant keys and Nones as values
        taxa = list(taxo_dict.keys())

        # Rank messes with species-level lookups, so only use for higher-level searches
        if target_level == 'Species':
            logging.info(f'Calling pygbif.species.namelookup with name "{name}"')
            data = species.name_lookup(q=name, limit=1000) 
        else:
            logging.info(f'Calling pygbif.species.namelookup with name "{name}" and rank "{target_level}"')
            data = species.name_lookup(q=name, rank=target_level, limit=1000) 

        results = data['results']
        logging.debug(f'PyGBIF returned {len(results)} results')

        missing_identifier = "N/A"
        if len(results) > 0: # If data was returned by pygbif
            avc = AttributeValueCounter(results,missing=missing_identifier)

            # slice to exclude levels more specific than the target
            #relevant_levels = Entry.taxon_levels[:Entry.taxon_levels.index(target_level)+1]
            relevant_levels = taxa[:taxa.index(target_level)+1]

            for level in relevant_levels:
                logging.debug(f"Attribute Value Counts for {level}: "+"\n"+avc.visual_summary(level.lower()))
                rankings = avc[level.lower()]

                rankings.pop(missing_identifier) # Remove any N/A's from the rankings
                
                top_result = max(rankings, key=rankings.get)
                logging.debug(f'Top result for "{level}" is "{top_result}"\n')
                taxo_dict[level] = max(rankings, key=rankings.get)
                # TODO Add some aliases so that 'Metazoa' remaps to 'Animalia' and so on

        return taxo_dict