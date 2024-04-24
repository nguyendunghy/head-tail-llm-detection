import hashlib

from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.utils import hash_code

TOKEN_LENGTH = 125
MIN_TEXT_LENGTH = 251
TOO_SHORT_TEXT = "TOO_SHORT_TEXT"


def process_word_longer_or_equal_token_length(text):
    indexing_list = []
    tmp_head_list = take_head_longer_or_equal_token_length(text)
    indexing_list.append(tmp_head_list)

    tmp_tail_list = take_tail_longer_or_equal_token_length(text)
    indexing_list.append(tmp_tail_list)
    return indexing_list


def take_tail_longer_or_equal_token_length(text):
    return text[len(text) - TOKEN_LENGTH:]


def take_head_longer_or_equal_token_length(text):
    return text[:TOKEN_LENGTH]


def process_head(sentence, sentences, current_index):
    sub_sentences = sentences[current_index:]
    all_sub_word = ' '.join(sub_sentences)
    if len(all_sub_word) >= MIN_TEXT_LENGTH:
        if len(sentence) < TOKEN_LENGTH:
            while len(sentence) < TOKEN_LENGTH:
                next_sentence = sentences[current_index + 1]
                sentence = sentence + ' ' + next_sentence
                current_index = current_index + 1

        head = take_head_longer_or_equal_token_length(sentence)
        return head
    else:
        # Do nothing because min text request is MIN_TEXT_LENGTH
        return ''


def process_tail(sentence, sentences, current_index):
    sub_sentences = sentences[:current_index + 1]
    all_sub_word = ' '.join(sub_sentences)
    if len(all_sub_word) >= MIN_TEXT_LENGTH:
        if len(sentence) < TOKEN_LENGTH:
            while len(sentence) < TOKEN_LENGTH:
                previous_sentence = sentences[current_index - 1]
                sentence = previous_sentence + ' ' + sentence
                current_index = current_index - 1

        tail = take_tail_longer_or_equal_token_length(sentence)
        return tail
    else:
        # Do nothing because min text request is MIN_TEXT_LENGTH
        return ''


def cut_head_tail(text):
    if len(text) < MIN_TEXT_LENGTH:
        return [TOO_SHORT_TEXT]
    else:
        head = text[:TOKEN_LENGTH]
        tail = text[len(text) - TOKEN_LENGTH:]
        return [head, tail]


def index_data(el):
    text = el['text']
    indexing_list = []
    data_aug = DataAugmentator()
    sentences = data_aug.get_all_sentences(text)
    if len(sentences) < 4:  # min sentence in request is 3, if less than 3, return all text
        line = ' '.join(sentences)
        if len(line) < MIN_TEXT_LENGTH:
            ...
        else:
            tmp_list = process_word_longer_or_equal_token_length(line)
            indexing_list.extend(tmp_list)

    else:
        line = ' '.join(sentences)
        if len(line) < MIN_TEXT_LENGTH:
            ...
        else:
            for i in range(len(sentences)):
                sentence = sentences[i]
                if i >= 2:
                    tmp_tail = process_tail(sentence, sentences, i)
                    if len(tmp_tail) > 0:
                        indexing_list.append(tmp_tail)

                if i <= len(sentences) - 3:
                    tmp_head = process_head(sentence, sentences, i)
                    if len(tmp_head) > 0:
                        indexing_list.append(tmp_head)
    return indexing_list


def get_hash_and_db(token):
    m = hashlib.sha256(token.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    hash_value = hash_code(sha256_hex)
    db = hash_value % 10_000
    return sha256_hex[:8], db


if __name__ == "__main__":
    TOKEN_LENGTH = 125
    MIN_TEXT_LENGTH = 251
    data_aug = DataAugmentator()
    text = '''Brushing your teeth on a regular basis is one of the best things you can do for yourself. Healthy teeth make a beautiful smile. Brushing can also help with gum health and even keep your breath smelling sweet.\nFor some of us, though, brushing can be an annoying chore that gets in the way of a good time. Hopefully you don’t think of brushing in such dire terms, but it happens.\nThe best way to build brushing into your routine is to make it a habit. A habit is a repeated practice that becomes hard to give up. Some habits can be bad, of course. Brushing can be a good habit.\nDon’t complicate the instructions for your kids. Keep it as simple as possible at the start. A small amount of toothpaste on your toothbrush, brush for two minutes, rinse with clear water. Simple.\nOnce you have created a healthy habit around brushing your teeth, you’ll have plenty of reason to smile.\nAt Providence Dental in North Las Vegas, the dental health of our patients is our top priority. We offer a full range of services, from family dentistry to urgent dental care. Schedule your next cleaning and checkup with us today.'''
    sentences = data_aug.get_all_sentences(text)
    print("len sentences: " + str(len(sentences)))
    print(sentences)
    el = {'text': text}
    result = index_data(el)
    print("len result: " + str(len(result)))
    print(result)
