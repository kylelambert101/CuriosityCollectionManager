import json
import re
import pprint
import math
import sys
import logging
import textwrap
from Entry import Entry
from ProgressBar import ProgressBar
import pickle
from os import path
from PyGBIFParser import PyGBIFParser
from Utilities import coalesce_taxo_results

# General Settings
LOG_FILE_NAME = 'app.log'
GBIF_CACHE_FILE_NAME = 'gbif_results.dat'
JSON_OUTPUT_FILE_NAME = 'all_entries.json'

# Logging Setup
logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    filemode='w',
    format='%(asctime)s - (%(levelname)s) - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

# TODO Expand with argparse.ArgumentParser to be fancier
if len(sys.argv) < 2:
    print('Error: Please specify a file.')
    logging.critical('No file specified - exiting ParseDayOne')
    sys.exit(1)

# Arguments were acceptable - check for cache file
if path.exists(GBIF_CACHE_FILE_NAME):
    logging.info(f'Found cached gbif result file: {GBIF_CACHE_FILE_NAME}')
    cached_gbif_results = pickle.load(open(GBIF_CACHE_FILE_NAME, 'rb'))
    logging.debug(f'There are {len(cached_gbif_results)} cached results')
else:
    logging.info(
        f'No cached gbif result file found. A new one will be created at "{GBIF_CACHE_FILE_NAME}"')
    cached_gbif_results = dict()

file_name = sys.argv[1]
logging.info(f'Parsing {file_name} for entries')
with open(file_name, 'r') as f:
    data = json.loads(f.read())['entries']

logging.info(f'Found {len(data)} entries')

all_text = [d['text'] for d in data]
all_entries = []
print(f'Processing {len(all_text)} entries')
bar = ProgressBar(50)
bar.start()
current = 0
for text in all_text:
    try:
        # Create the entry
        entry = Entry(text)

        # Assign entry taxonomy

        # Create a dictionary to store taxo results for each label
        taxonomy_results = dict()
        # Populate taxonomy_results
        for (level, text) in entry.taxonomy_labels:
            logging.debug(
                f'Checking the cached gbif results for level/text "{level}/{text}"...')

            if (level, text) in cached_gbif_results.keys():
                # A cached result was found - use that
                result = cached_gbif_results[(level, text)]
                logging.debug(
                    f'Found a result: {json.dumps(result, indent=4)}')
                taxonomy_results[level] = result
            else:
                # no results in cache - use pygbif parser
                logging.debug(f'Did not find a cached result. Calling API...')
                result = PyGBIFParser.parse(
                    name=text, target_level=level, taxo_dict=dict(zip(Entry.taxon_levels, [None]*len(Entry.taxon_levels))))
                logging.debug(
                    f'Assembled result from API: {json.dumps(result,indent=4)}')
                taxonomy_results[level] = result

                # update the cache and autosave
                logging.debug('Updating cache...')
                cached_gbif_results[(level, text)] = result
                logging.debug(
                    f'Saving updated cache file with {len(cached_gbif_results)} results...')
                pickle.dump(cached_gbif_results, open(
                    GBIF_CACHE_FILE_NAME, 'wb'),)

        # assign the coalesced taxo results to the entry
        coalesced = coalesce_taxo_results(taxonomy_results)
        logging.debug(
            f'Assigning coalesced taxonomy: {json.dumps(coalesced, indent=4)}')
        entry.taxonomy = coalesced

        # Add entry to list
        all_entries.append(entry)
        logging.info(f'New Entry:\n{str(entry)}')
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
    current += 1
    bar.update_progress(current, len(all_text))

# Save json file of all entries
with open(JSON_OUTPUT_FILE_NAME, 'w') as f:
    # TODO Fix this - Entry is not JSON Serializable.
    #f.write(json.dumps(all_entries, indent=4))
    message = 'I wish I could save a json file... Bad programmer!'
    logging.debug(message)
    print(message)

# for e in sorted(all_entries):
#     print(e)
# TODO Add a cool thing where it shows what is being processed at the bottom of the screen under the progress bar
