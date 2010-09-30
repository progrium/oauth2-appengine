import time
import hashlib
import random

def now():
    return int(time.mktime(time.gmtime()))

def random_str():
    return hashlib.sha1(str(random.random())).hexdigest()

def extract(keys, d):
    """ Extracts subset of a dict into new dict """
    return dict((k, d[k]) for k in keys if k in d)