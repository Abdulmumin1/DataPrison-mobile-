import json
import re


def write_cache(datas, fmt=False):
    if not datas:
        return
    _file = open('cache_data.json', 'w')

    if not fmt:
        cache = {}
        print(datas)
        for data in datas:
            item = [data[0], data[1], data[2]]
            cache[data[2]] = item
    else:
        cache = datas

    json.dump(cache, _file)
    _file.close()


def search_data(query, datas=False):
    if not datas:
        datas = read_cache(fmt=False)
    keys = [i for i in datas.keys()]
    if not query:
        return read_cache()
    matches = set()
    for key in keys:
        datas_to_search = datas[key][:2]
        for entry in datas_to_search:
            match = re.search(query.upper(), str(entry).upper())
            if match:
                matches.add(key)

    return_items = [datas[i] for i in matches]
    return return_items


def update_cache(datas=None, id=None, data=None):

    if all([data, id]):
        datas = read_cache(fmt=False)
        datas[id] = data
        write_cache(datas, fmt=True)
        return

    old_data = read_cache()
    if datas:
        old_data.append(datas)
    write_cache(old_data)


def read_cache(fmt=True):

    datas = json.load(open('cache_data.json'))
    return_datas = []
    if not fmt:
        return datas

    for data in datas.items():
        return_datas.append(data[1])
    return return_datas[::-1]
