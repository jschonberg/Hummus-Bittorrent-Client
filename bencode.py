# Code extended from https://wiki.theory.org/Decoding_bencoded_data_with_python
# -*- coding: utf-8 -*-

import re
from utilities import HummusError

RE_DECIMAL = re.compile('\d')


class BencodeError(HummusError):
    pass


def bencode(data):
    """Encode a list of tuples in bencode format"""
    if isinstance(data, list):
        if isinstance(data[0], tuple):
            tmp = 'd'
            for element in data:
                key = element[0]
                value = element[1]
                tmp = "".join([tmp, bencode(key), bencode(value)])
            tmp += 'e'
            return tmp
        else:
            tmp = 'l'
            for element in data:
                tmp = "".join([tmp, bencode(element)])
            tmp += 'e'
            return tmp
    elif isinstance(data, int):
        return "".join(['i', str(data), 'e'])
    elif isinstance(data, basestring):
        return "".join([str(len(data)), ':', data])
    else:
        raise BencodeError('Unexpected data type for bencoding.')


def bdecode(data, rtn_type={}):
    """Decode data from bencode format to python objects.

    Args:
      data (string): bencode format data
      rtn_type (object): python dict or tuple indicating desired return type

    """
    if not isinstance(rtn_type, dict) and not isinstance(rtn_type, tuple):
        raise BencodeError("Bdecode return type must be dict or tuple")

    chunks = list(data)
    chunks.reverse()
    root = _dechunk(chunks, rtn_type)
    return root


def _dechunk(chunks, rtn_type={}):
    """Helper for bdecode. Should not be called directly"""
    item = chunks.pop()
    if item == 'd':
        if isinstance(rtn_type, dict):
            item = chunks.pop()
            hash = {}
            while item != 'e':
                chunks.append(item)
                key = _dechunk(chunks, rtn_type)
                hash[key] = _dechunk(chunks, rtn_type)
                item = chunks.pop()
            return hash
        elif isinstance(rtn_type, tuple):
            item = chunks.pop()
            temp_array = []
            while item != 'e':
                chunks.append(item)
                key = _dechunk(chunks, rtn_type)
                temp_array.append((key, _dechunk(chunks, rtn_type)))
                item = chunks.pop()
            return temp_array
        else:
            raise BencodeError("Uncreachable in _dechunk()")
    elif item == 'l':
        item = chunks.pop()
        temp_list = []
        while item != 'e':
            chunks.append(item)
            temp_list.append(_dechunk(chunks, rtn_type))
            item = chunks.pop()
        return temp_list
    elif item == 'i':
        item = chunks.pop()
        num = ''
        while item != 'e':
            num += item
            item = chunks.pop()
        return int(num)
    elif RE_DECIMAL.search(item):
        num = ''
        while RE_DECIMAL.search(item):
            num += item
            item = chunks.pop()
        line = ''
        for i in range(int(num)):
            line += chunks.pop()
        return line
    else:
        raise BencodeError("Unreachable in _dechunk() #2")
