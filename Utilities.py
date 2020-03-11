from Entry import Entry
import json
import logging


def coalesce_taxo_results(results):
    logging.debug(f'Coalescing {len(results)} result dictionaries')
    final_taxonomy = dict(
        zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))
    # iterate backwards through Entry.taxon_levels to start with species
    is_first_iteration = True
    for level in reversed(Entry.taxon_levels):
        if level in results.keys():
            for level_key in Entry.taxon_levels[:(Entry.taxon_levels.index(level)+1)]:
                if not is_first_iteration and (not final_taxonomy[level_key] == results[level][level_key]):
                    old_value = final_taxonomy[level_key]
                    new_value = results[level][level_key]
                    logging.debug(
                        f'{level} results overriding level "{level_key}": "{old_value}" => "{new_value}"')
                final_taxonomy[level_key] = results[level][level_key]
            is_first_iteration = False
    return final_taxonomy


def cleanUpTaxoDict(taxo_dict):
    # Perform some standard data cleaning on the taxonomy

    new_dict = dict(taxo_dict)
    is_plant = taxo_dict['Kingdom'] == 'Plantae'

    # Keywords that should be transformed to a different word
    remappings = {
        "Metazoa": "Animalia"
    }

    for level, value in taxo_dict.items():
        # Remappings
        if value in remappings.keys():
            logging.debug(f'Remapping "{value}" to "{remappings[value]}"')
            new_dict[level] = remappings[value]

        # Remove phylum and class from plants
        if is_plant and level in ['Phylum', 'Class'] and value is not None:
            logging.debug(
                f'Stripping {level} value for plant entry: "{new_dict[level]}" => {None}')
            new_dict[level] = None

    return new_dict
