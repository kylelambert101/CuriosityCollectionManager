from Entry import Entry
import json

# TODO Add logging


def coalesce_taxo_results(results):
    final_taxonomy = dict(
        zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels)))
    # iterate backwards through Entry.taxon_levels to start with species
    for level in reversed(Entry.taxon_levels):
        if level in results.keys():
            for level_key in Entry.taxon_levels[:(Entry.taxon_levels.index(level)+1)]:
                # TODO Indicate if this overrides a previously-assigned value
                final_taxonomy[level_key] = results[level][level_key]
    return final_taxonomy
