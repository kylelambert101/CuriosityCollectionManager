import json, re, pprint, math, sys
from Entry import Entry

# TODO Extract this to an argument (sys.argv[1])
# Also, check number of arguments first to prevent errors. 
# TODO Expand with argparse.ArgumentParser to be fancier
if len(sys.argv) < 2:
    print('Error: Please specify a file.')
    sys.exit(1)

file_name = sys.argv[1]
with open(file_name,'r') as f:
    data = json.loads(f.read())['entries']

outfile = open('output.txt','w')

all_text = [d['text'] for d in data]
all_entries = []

print(f'Processing {len(all_text)} entries')
numchunks = 50
current = 0
print('|'+'-'*(numchunks)+'|')
prev_chunk =0
print('|',end='', flush=True)
for text in all_text:
    entry = Entry(text)
    all_entries.append(entry)
    outfile.write(str(entry))
    outfile.write('\n')
    current+=1
    progress = current/len(all_text)
    current_chunk=math.ceil(progress*50)
    if current_chunk != prev_chunk:
        print('#', end='', flush=True)
    prev_chunk = current_chunk
print('|')

# TODO Extract progress bar code to a different class
# TODO Add a cool thing where it shows what is being processed at the bottom of the screen under the progress bar
# TODO Implement a container of entries
# TODO Write all of the pygbif parsing information to a log file to be inspected manually