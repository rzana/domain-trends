from collections import Counter
import csv
import gzip
import requests
from typing import Generator
import wordninja


DOMAIN_RANKS_URL = (
    'http://commoncrawl.s3.amazonaws.com/projects/hyperlinkgraph/'
    'cc-main-2019-feb-mar-apr/domain/cc-main-2019-feb-mar-apr-domain-ranks.txt.gz'
)


def analyze_trends() -> None:
    filestream = _get_filestream(DOMAIN_RANKS_URL)
    word_counter = Counter()

    for line in csv.DictReader(_read_lines(filestream, 10**5), delimiter='\t'):
        name = line['#host_rev'].split('.')[-1]
        words = [word for word in wordninja.split(name) if len(word) > 2]

        for word in words:
            word_counter[word] += 1

    for word, count in word_counter.most_common(50):
        print(count, word)


def _get_filestream(url: str) -> gzip.GzipFile:
    r = requests.get(url, stream=True)
    r.raise_for_status()

    return gzip.open(r.raw, mode='rt')


def _read_lines(filestream: gzip.GzipFile, count: int) -> Generator[str, None, None]:
    yield next(filestream)

    while count > 0:
        yield next(filestream)

        count -= 1
        if count % 10000 == 0:
            print(count)


if __name__ == '__main__':
    analyze_trends()
