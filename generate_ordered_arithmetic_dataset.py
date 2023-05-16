import numpy as np
import random
import json

templates = {
    "{} + {} * {}": "PM",
    "{} * {} + {}": "MP"
}

triples = [(i, j, k) for i in range(0, 10) for j in range(0, 10) for k in range(0, 10)]
assert len(triples) == 1000

random.shuffle(triples)
N = 300
data = []
for i, template in enumerate(templates):
    td = triples[i*N:(i+1)*N]
    for triple in td:
        q = template.format(triple[0], triple[1], triple[2])
        dp = {
            "Question": q + " =",
            "Answer": eval(q),
            "Type": templates[template]
        }
        data.append(dp)

with open('data/ordered_arithmetic_2hop.jsonl', 'w') as f:
    for d in data:
        f.write(json.dumps(d) + "\n")
