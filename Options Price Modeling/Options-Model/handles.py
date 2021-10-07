import json


def read_json(f):
    with open(f, 'r') as df:
        return json.loads(df.read())

def dump_json(f, d):
    with open(f, 'w') as df:
        json.dump(d, df, indent=4)