#!/usr/bin/env python

##################################################
#
# bdzd - get top answers to your question
# written by wangyijie @tegongdete
# inspired by Benjamin Gleizman (gleitz@mit.edu)
#
##################################################

__version__ = '0.1'

import click
import sys
import os
import random
import re
import requests
import requests_cache
import sys

from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

# Handle imports for python 2/3
if sys.version < '3':
    import codecs
    from urllib import quote as url_quote
    
    def u(x):
        return codecs.unicode_escape_decode(x)[0]

else:
    from urllib.parse import quote as url_quote

    def u(x):
        return x


SEARCH_URL = 'https://www.baidu.com/s?wd=site:{0}%20{1}'
URL = 'zhidao.baidu.com'

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
    'Chrome/19.0.1084.46 Safari/536.5'),
    ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
    'Safari/536.5'), )

ANSWER_HEADER = ('问题链接:    {0} \n\n原问题:    {1}\n\n最佳回答:    {2}')
NOANSWER_HEADER = '<no answer given>'
XDG_CACHE_DIR = os.environ.get('XDG_CACHE_HOME',
                os.path.join(os.path.expanduser('~'), '.cache'))
CACHE_DIR = os.path.join(XDG_CACHE_DIR, 'bdzd')
CACHE_FILE = os.path.join(CACHE_DIR, 'cache{0}'.format(
    sys.version_info[0] if sys.version_info[0] == 3 else ''))


# Get search result 
def _get_result(url):
    try:
        return requests.get(url, headers={'User-Agent':random.choice(USER_AGENTS)}).text
    except requests.exceptions.SSLError as e:
        raise e

# Get links from serach result
def _get_links(query):
    result = _get_result(SEARCH_URL.format(URL, url_quote(query)))
    html = pq(result)
    return [a.attrib['href'] for a in html('.t')('a')]


def get_link_at_pos(links, position):
    if not links:
        return False

    if len(links) >= position:
        link = links[position]
    else:
        link = links[-1]
    return link


def _format_output(answer):
    return answer


def _get_title(link):
    if not link:
        return False
    page = _get_result(link)
    page = page.encode("latin1").decode("gbk")
    html = pq(page)

    return html('title').text()[:-5]


def _get_answer(link):
    if not link:
        return False
    page = _get_result(link)
    page = page.encode("latin1").decode("gbk")
    html = pq(page)

    best_answer = html('.best-text').text()
    if not best_answer:
        answers = html('.answer-text')
        if not answers:
            return ''
        best_answer = html('.answer-text')[0].find('span').text
    return _format_output(best_answer)


def _get_instructions(args):
    links = _get_links(args['query'])

    if not links:
        return False
    answers = []
    for n in range(args['num_of_ans']):
        link = get_link_at_pos(links, n)
        answer = _get_answer(link)
        title = _get_title(link)
        if not answer:
            continue
        answer = format_answer(link, title, answer)
        answers.append(answer)
    return "\n\n\n".join(answers)


def format_answer(link, title, answer):
    return ANSWER_HEADER.format(link, title, answer)


def _enable_cache():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    requests_cache.install_cache(CACHE_FILE)


def bdzd(args):
    args['query'] = args['query'].replace('？', '')
    try:
        res = _get_instructions(args)
        return res
    except ConnectionError as e:
        return e


@click.command()
@click.argument('query', nargs=1, required=False)
@click.option('--number', '-n', default=1, required=False)
@click.option('--version', '-v', is_flag=True)
def command_line_executor(query, number, version):
    args = {'query': query, 'num_of_ans': number}
    
    if version:
        print('bdzd version ' + __version__)
    
    if not args['query']:
        return
    
    _enable_cache()
    if sys.version < '3':
        print(bdzd(args).encode('utf-8', 'ignore'))
    else:
        print(bdzd(args))


if __name__ == '__main__':
    command_line_executor()
