from handles import *
from pprint import pprint
import os
import numpy as np

def rank_chains(ref='2021-04-15'):
    tc = {}
    for f in os.listdir(f'data/{ref}'):
        chains = read_json(f'data/{ref}/{f}')
        for s, o in chains.items():
            if s not in tc:
                tc[s] = 0
            tc[s] += len(o)
    top = sorted(list(tc.items()), key=lambda x: x[1], reverse=True)
    return top

def basic_stats(a):
    a = np.array(a)
    stats = {
        'Shape': a.shape,
        'Mean': np.mean(a),
        'Min': np.amin(a),
        'Max': np.amax(a),
        'SDev': np.std(a),
    }
    return stats
    
