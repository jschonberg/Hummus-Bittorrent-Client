import re
import numbers
import logging

decimal_match = re.compile('\d')

class BencodeError(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
    def __repr__(self):
        return str(self.reason)
    def __str__(self):
        return str(self.reason)

def bencode(data):
    '''
    Main function to bencode data
    Accepts list of tuples of key/value pairs
    Returns bencoded data?
    '''
    if type(data) is list:
        #Making an assumption below that if we're in one of our lists of tuples, ALL first-level elements are going to be tuples. Is that an okay assumption? Otherwise, how to check that ALL elements of the list are tuples (with two elements each, if extra detail is needed)?
        if type(data[0]) is tuple:
            tmp = 'd'
            for element in data:
                key = element[0]
                value = element[1]
                tmp += bencode(key) + bencode(value)
            tmp += 'e'
            return tmp
        else:
            tmp = 'l'
            for element in data:
                tmp += bencode(element)
            tmp += 'e'
            return tmp

    elif isinstance(data, numbers.Real):
        #This checks if data is an int, long, or float.
        tmp = 'i' + str(int(data)) + 'e'
        return tmp

    elif isinstance(data, basestring):
        tmp = str(len(data)) + ':' + data
        return tmp

    else:
        logging.error('Unexpected data type for bencoding.')

def bdecode(data, rtn_type={}):
    '''
    Main function to decode bencoded data
    Returns list of tuples of key/value pairs
    Will turn bencoded dictionaries into tuples or dicts based on type of rtn_type
    '''
    if type(rtn_type) != dict and type(rtn_type) != tuple:
        raise BencodeError("Bdecode return type must be dict or tuple")

    chunks = list(data)
    chunks.reverse()

    if type(rtn_type) == dict:
        root = _dechunk(chunks)
    elif type(rtn_type) == tuple:
        root = _dechunk(chunks,())
    return root

def _dechunk(chunks, rtn_type={}):
    item = chunks.pop()
    if item == 'd': 
        if type(rtn_type) == dict:
            item = chunks.pop()
            hash = {}
            while item != 'e':
                chunks.append(item)
                key = _dechunk(chunks,rtn_type)
                hash[key] = _dechunk(chunks,rtn_type)
                item = chunks.pop()
            return hash
        elif type(rtn_type) == tuple:
            item = chunks.pop()
            temp_array = []
            while item != 'e':
                chunks.append(item)
                key = _dechunk(chunks,rtn_type)
                temp_array.append((key, _dechunk(chunks,rtn_type)))
                item = chunks.pop()
            return temp_array
        else:
            assert(False)
    elif item == 'l':
        item = chunks.pop()
        temp_list = []
        while item != 'e':
            chunks.append(item)
            temp_list.append(_dechunk(chunks,rtn_type))
            item = chunks.pop()
        return temp_list
    elif item == 'i':
        item = chunks.pop()
        num = ''
        while item != 'e':
            num  += item
            item = chunks.pop()
        return int(num)
    elif decimal_match.search(item):
        num = ''
        while decimal_match.search(item):
            num += item
            item = chunks.pop()
        line = ''
        for i in range(int(num)):
            line += chunks.pop()
        return line
    logging.error("Invalid input!")