from urllib.parse import urlparse

def get_domain(url):
    res = urlparse(url).netloc.replace('.', '_')
    tmp = ""
    for i in range(0, 4):
        tmp += res[i]
    if tmp == "www_":
        new_res = ""
        for i in range(4, len(res)):
            new_res += res[i]
        return new_res
    return res

def get_path(url):
    parsed = urlparse(url)
    return (parsed.netloc.replace('.', '_') + parsed.path).replace('/', '_')

print(get_domain("https://www.abc.com/browse/comedy/familyguy/episode1"))