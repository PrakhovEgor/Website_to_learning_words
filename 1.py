r = {'work': 'hard', 'job': 'easy'}

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

print(get_key(r, '1'))
print(get_key(r, 'hard'))
print(get_key(r, 'easy'))