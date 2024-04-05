import json
import random
import sys
import time

from nltk import pos_tag

import random
import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from nltk import pos_tag
from nltk.tokenize import sent_tokenize


class DataAugmentator:
    def __init__(self):
        pass

    def add_misspell(self, text):
        words = text.split(' ')
        ind = random.randint(0, len(words) - 1)
        changed_word = words[ind]

        if len(changed_word) == 0:
            return {'text': text, 'subtype': 'None'}

        res = {}
        k = random.randint(0, len(changed_word) - 1)
        random_char = chr(ord('a') + random.randint(0, 25))

        p = random.random()
        if p < 0.33:
            res['subtype'] = 'replace'
            changed_word = changed_word[:k] + random_char + changed_word[k + 1:]
        elif p < 0.66:
            res['subtype'] = 'delete'
            changed_word = changed_word[:k] + changed_word[k + 1:]
        else:
            res['subtype'] = 'insert'
            changed_word = changed_word[:k] + random_char + changed_word[k:]

        words[ind] = changed_word
        res['text'] = ' '.join(words)
        return res

    def remove_random_adjective(self, text):
        tokens = text.split(' ')
        tagged_tokens = pos_tag(tokens)

        # Identify all adjectives (JJ, JJR, JJS)
        adjectives = [word for word, tag in tagged_tokens if tag in ('JJ', 'JJR', 'JJS')]

        if not adjectives:
            return {'text': ' '.join(tokens), 'subtype': 'None'}

        adjective_to_remove = random.choice(adjectives)
        tokens.remove(adjective_to_remove)
        res = {'text': ' '.join(tokens), 'subtype': 'adjective'}
        return res

    def subsample_sentences(self, text, min_sentence=3, max_sentence=10):
        sentences = sent_tokenize(text)
        if len(sentences) <= min_sentence:
            return {'text': ' '.join(sentences), 'subtype': 'None'}

        cnt = random.randint(min_sentence, min(max_sentence, len(sentences)))
        ind = random.randint(0, len(sentences) - cnt)
        return {'text': ' '.join(sentences[ind:ind + cnt]), 'subtype': '{}_sentences'.format(cnt)}

    def get_all_sub_sentences(self, text, min_sentence=3, max_sentence=10):
        sentences = sent_tokenize(text)
        if len(sentences) <= min_sentence:
            return [' '.join(sentences)]
        all_sub_sentences = []
        for i in range(len(sentences) - 2):
            for j in range(i + 3, min(i + max_sentence, len(sentences)) + 1):
                all_sub_sentences.append(' '.join(sentences[i:j]))
        return all_sub_sentences
    def __call__(self, text):
        text = self.subsample_sentences(text)['text']

        if random.random() < 0.5:
            res = self.add_misspell(text)
            res['type'] = 'misspell'
        else:
            res = self.remove_random_adjective(text)
            res['type'] = 'remove_adj'
        return res


if __name__ == '__main__':
    start_time = time.time_ns()
    # file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
    file_path = "/root/c4_dataset/c4/extracted_file/head-1000-00001.json"
    # file_path = "/root/c4_dataset/c4/extracted_file/head-10000-00001.json"
    data_aug = DataAugmentator()
    with open(file_path, 'r') as file:
        for line in file:
            el = json.loads(line)
            text = el['text']
            # print("origin text: " + str(text))
            list_sub_sentence = data_aug.get_all_sub_sentences(text)


