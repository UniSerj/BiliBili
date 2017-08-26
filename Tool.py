import urllib
from six.moves import urllib

def http_get(url):
    response = urllib.request.urlopen(url).read()
    response = response.decode('UTF-8')
    return response

def get_real_roomid(roomid):
    html = http_get("http://live.bilibili.com/" + roomid)
    start = html.find("ROOMID = ") + len("ROOMID = ")
    end = html.find(";", start)
    if 0 < start < end:
        real_roomid = html[start:end].replace(' ', '')
        return real_roomid
    else:
        return roomid

def get_danmu_rnd(roomid):
    html = http_get("http://live.bilibili.com/" + roomid)
    start = html.find("DANMU_RND = ") + len("DANMU_RND = ")
    end = html.find(";", start)
    if 0 < start < end:
        danmu_rnd = html[start:end].replace(' ', '')
        return danmu_rnd
    else:
        return 0

def get_str_between(sub, prev, after):
    btw = None
    prev_loc = sub.find(prev)
    if prev_loc >= 0:
        prev_loc += len(prev)
        after_loc = sub.find(after, prev_loc)
        if after_loc > prev_loc:
            btw = sub[prev_loc: after_loc]
    return btw
