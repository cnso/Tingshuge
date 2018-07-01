from .version import script_name, __version__
import argparse
import sys
import requests
import re
from pyquery import PyQuery as pq
import json
import codecs
from urllib import parse


def search(keyword):
    res = requests.post("http://m.tingshuge.com/search.asp", keyword)
    res.encoding = "gbk"
    root = pq(res.text)
    list = root(".new_tab_img")("li")
    books = []
    for book in list.items():
        books.append({"id": re.search("\\d+", book("a").attr("href")).group(0), "text": book.text()})
    for i in range(len(books)):
        print(i, books[i]['text'])
    next_page = root('.ui-vpages')(':eq(%d)' % (root('.ui-vpages').children().size() - 2)).attr('href')
    if next_page:
        next_page = parse.parse_qs(parse.urlparse(parse.unquote(next_page, encoding='gbk')).query)
        for key in next_page.keys():
            next_page[key] = next_page[key][0]
        next_page['searchword'] = next_page['searchword'].encode('gbk')
        print('下一页(n)')
    else:
        print()
    print(root('.ui-vpages')(':eq(1)').text(), end=' 下一页(n)' if next_page else '')
    index = input('选择下载的版本:')
    if next_page and index == 'n':
        search(next_page)
    elif index.isdigit() and int(index) in range(len(books)):
        create_uri(books[int(index)]['id'])
    else:
        print('退出')

def create_uri(book_id):
    dic = {'tudou': 'f4v', 'music': 'm4a'}
    urls = {'tudou': lambda s: "http://vr.tudou.com/v2proxy/v2?it=%s" % s, 'music': lambda s: s}
    res = requests.get('http://m.tingshuge.com/playbook/', params={"%d-0-0.html" % int(book_id): ''})
    res.encoding = 'gbk'
    title = re.search("xTitle='(.+?)'", res.text).group(1)
    file = codecs.open("%s.txt" % title, 'w', encoding='utf-8')
    sounds = json.loads(re.search('VideoListJson=\\[\\[\'.*?\',(\\[.*\\])\\]\\]', res.text).group(1).replace("'", "\""))
    for s in sounds:
        data = s.split("$")
        name = "%s.%s" % (data[0], dic[data[2]])
        file.write(urls[data[2]](data[1]))
        file.write("\n\tdir=%s\n" % title)
        file.write("\tout=%s\n" % name)
        file.write("\tmax-connection-per-server=5\n")
        file.write('\tcontinue=true\n')
    print('%s的uri文件已生成，请使用aria2下载' % title)



def main(**kwargs):
    parse = argparse.ArgumentParser(
        prog=script_name,
        usage='{} KEY_WORD'.format(script_name),
        description='A tiny downloader that scrapes the web',
        add_help=True,
    )
    parse.add_argument('-v', '--version', action='store_true',
        help='Print version and exit', required=False)
    parse.add_argument('KEY_WORD', nargs='*', type=str, help='search keyword')

    args = parse.parse_args()
    if args.version:
        print("%s: version %s" % (script_name, __version__))
        sys.exit()
    if args.KEY_WORD:
        search({"searchword": args.KEY_WORD[0].encode('gbk'), "searchtype": "-1"})
    else:
        parse.print_help()


if __name__ == '__main__':
    main()
