import json, re, pprint, math, sys, logging, textwrap
from Entry import Entry
from ProgressBar import ProgressBar

# Logging Setup
logging.basicConfig(    level=logging.DEBUG, 
                        filename='app.log', 
                        filemode='w', 
                        format='%(asctime)s - (%(levelname)s) - %(message)s', 
                        datefmt='%d-%b-%y %H:%M:%S' )

# TODO Expand with argparse.ArgumentParser to be fancier
if len(sys.argv) < 2:
    print('Error: Please specify a file.')
    logging.critical('No file specified - exiting ParseDayOne')
    sys.exit(1)


file_name = sys.argv[1]
logging.info(f'Parsing {file_name} for entries')
with open(file_name,'r') as f:
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
        entry = Entry(text)
        all_entries.append(entry)
        logging.info(f'New Entry:\n{str(entry)}')
    except Exception as e:
        logging.error("Exception occurred",exc_info=True)
    current+=1
    bar.update_progress(current, len(all_text))

for e in sorted(all_entries):
    print(e)

# TODO Extract progress bar code to a different class
# TODO Add a cool thing where it shows what is being processed at the bottom of the screen under the progress bar