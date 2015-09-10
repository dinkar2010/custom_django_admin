__author__ = 'dinkar'
from itertools import izip
import datetime
def pairwise(iterable,n):
    a = iter(iterable)
    return izip(*[iter(iterable)]*n)

def change_message(*args):
    message =str(datetime.datetime.now())+'\n'+ 'Changed '+'\n'
    for x, y,z in pairwise(args,3):
        y=str(y)
        z=str(z)
        if y != z:
            message += x + ' from '+ y +' to '+ z
            message += '\n'
    return message