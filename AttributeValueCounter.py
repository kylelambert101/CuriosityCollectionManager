from collections import Counter

'''
Helper class to get statistics on a list of dictionaries.
Copied from the following link and modified:
https://codereview.stackexchange.com/questions/174769/gathering-statistics-on-a-list-of-dicts
'''
class AttributeValueCounter:
    def __init__(self, iterable, *, missing="N/A"):
        self._missing = missing
        self.length = 0
        self._counts = {}
        self.update(iterable)

    def update(self, iterable):
        if iterable is None or len(iterable) == 0:
            return
        categories = set(self._counts)
        for length, element in enumerate(iterable, self.length):
            categories.update(element)
            for category in categories:
                try:
                    counter = self._counts[category]
                except KeyError:
                    self._counts[category] = counter = Counter({self._missing: length})
                counter[str(element.get(category, self._missing))] += 1
        self.length = length + 1 

    def add(self, element):
        self.update([element])

    def __getitem__(self, key):
        return self._counts[key]

    def summary(self, key=None):
        if key is None:
            return '\n'.join(self.summary(key) for key in self._counts)
        if key not in self._counts.keys():
            return '-- {} --\n{}'.format(key,'Key does not exist\n')

        return '-- {} --\n{}'.format(key, '\n'.join(
                '\t {}: {}'.format(value, count)
                for value, count in self._counts[key].items()
        ))
        
    ''' Similar to summary but prettier '''
    def visual_summary(self,key):
        if key is None:
            return '\n'.join(self.summary(key) for key in self._counts)
        if key not in self._counts.keys():
            return '-- {} --\n{}'.format(key,'Key does not exist\n')
            
        target_len = max([len('{}:'.format(value)) for value,count in self._counts[key].items()])
        target_count = sum(self._counts[key].values())
        
        return '-- {} --\n{}'.format(key, 
            '\n'.join( 
                # value: bar (percent)
                '\t{}:{}|{} ({}%)'.format(value, ' '*(target_len-(len(value))), '#'*count,int(count/target_count*100))
                # bar value (percent)
                #'\t|{}\t{} ({}%)'.format('#'*count,value,int(count/target_count*100))
                for value,count in sorted(self._counts[key].items(), key=lambda item: -item[1])
                )
            )