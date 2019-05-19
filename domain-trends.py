import csv
import gzip
import requests
import wordninja

from collections import Counter
from matplotlib import pyplot as plt
from typing import Generator, List


DOMAIN_RANKS_URL = (
    'http://commoncrawl.s3.amazonaws.com/projects/hyperlinkgraph/'
    'cc-main-2019-feb-mar-apr/domain/cc-main-2019-feb-mar-apr-domain-ranks.txt.gz'
)


def analyze_trends() -> None:
    filestream = _get_filestream(DOMAIN_RANKS_URL)
    word_counter = Counter()
    name_lengths = []
    number_of_words = []

    for line in csv.DictReader(_read_lines(filestream, 10**5), delimiter='\t'):
        name = line['#host_rev'].split('.')[-1]
        words = [word for word in wordninja.split(name) if len(word) > 2]

        for word in words:
            word_counter[word] += 1

        name_lengths.append(len(name))
        number_of_words.append(len(words))

    _save_word_count(word_counter)
    _save_name_lengths(name_lengths)
    _save_number_of_words(number_of_words)


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


def _save_word_count(word_counter: Counter) -> None:
    with open('most-common-words.txt', 'w') as f:
        for word, count in word_counter.most_common(50):
            f.write(f'{count} {word}\n')


def _save_name_lengths(name_lengths: List[int]) -> None:
    plt.plot(_average_chunks(name_lengths, 2000))
    plt.title('Name Length')
    plt.savefig('name-length.png')
    plt.clf()


def _save_number_of_words(number_of_words: List[int]) -> None:
    plt.plot(_average_chunks(number_of_words, 2000))
    plt.title('Number Of Words')
    plt.savefig('number-of-words.png')
    plt.clf()


def _average_chunks(data: List[int], size: int) -> List[float]:
    result = []

    for i in range(len(data) // size):
        chunk = data[size*i:size*(i+1)]
        result.append(sum(chunk) / len(chunk))

    return result


if __name__ == '__main__':
    analyze_trends()
