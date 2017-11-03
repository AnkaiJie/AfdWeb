class Utility:
    #returns dict with the wanted keys only, if keys empty, just flattens dict
    def flattenDict (self, d):
        def expand(key, value):
            if isinstance(value, dict):
                return [ (key + '_' + k, v) for k, v in self.flattenDict(value).items()]
            else:
                return [ (key, value) ]

        items = [ item for k, v in d.items() for item in expand(k, v) ]
        return dict(items)

    # if no keys specified, return original dictionary
    def filter(self, d, keys):
        if len(keys) is 0:
            return d
        dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        return dictfilt(d, keys)

    def removePrefix (self, origDict, sep=':'):
        d = dict(origDict)
        rem = []
        for key, value in d.items():
            if len(key.split(sep)) > 1:
                rem.append(key)
        for k in rem:
            newkey = k.split(sep)[1]
            d[newkey] = d.pop(k)
        return d

    def addPrefixToKeys(self, dOrig, prefix):
        d = dict(dOrig)
        keys = list(d.keys())
        for key in keys:
            d[prefix+key] = d.pop(key) 
        return d

    #stack overflow code
    def merge_dicts(self, *dict_args):
        '''
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        '''
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return dict(result)

    def changeKeyString(self, d, change, toThis):
        keys = list(d.keys())
        for key in keys:
            newKey = key.replace(change, toThis)
            d[newKey] = d.pop(key)

    def changeValueString(self, d, change, toThis):
        for key, val in d.items():
            if change in val:
                d[key] = val.replace(change, toThis)

    def replaceKey(self, d, change, toThis):
        d[toThis] = d.pop(change)

    def removeNone(self, d):
        keys = list(d.keys())
        for key in keys:
            if d[key] is None:
                d.pop(key)
