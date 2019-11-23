import json, re, pprint, math, sys, logging, textwrap
from Entry import Entry

# Logging Setup
logging.basicConfig(    level=logging.DEBUG, 
                        filename='app.log', 
                        filemode='w', 
                        format='%(asctime)s - (%(levelname)s) - %(message)s', 
                        datefmt='%d-%b-%y %H:%M:%S' )

# TODO Extract this to an argument (sys.argv[1])
# Also, check number of arguments first to prevent errors. 
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
numchunks = 50
current = 0
print('|'+'-'*(numchunks)+'|')
prev_chunk =0
print('|',end='', flush=True)
for text in all_text:
    try:
        entry = Entry(text)
        all_entries.append(entry)
        logging.info(f'New Entry:\n{str(entry)}')
    except Exception as e:
        logging.error("Exception occurred",exc_info=True)
    current+=1
    progress = current/len(all_text)
    current_chunk=math.ceil(progress*50)
    if current_chunk != prev_chunk:
        print('#', end='', flush=True)
    prev_chunk = current_chunk
print('|')

for e in sorted(all_entries):
    print(e)

# TODO Extract progress bar code to a different class
# TODO Add a cool thing where it shows what is being processed at the bottom of the screen under the progress bar
# TODO Implement a container of entries