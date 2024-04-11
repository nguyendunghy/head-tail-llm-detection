import hashlib

from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.utils import hash_code

TOKEN_LENGTH = 10
TOO_SHORT_TEXT = "TOO_SHORT_TEXT"


def process_word_longer_or_equal_token_length(words):
    indexing_list = []
    tmp_head_list = take_head_longer_or_equal_token_length(words)
    indexing_list.append(tmp_head_list)

    tmp_tail_list = take_tail_longer_or_equal_token_length(words)
    indexing_list.append(tmp_tail_list)
    return indexing_list


def take_tail_longer_or_equal_token_length(words):
    return ' '.join(words[len(words) - TOKEN_LENGTH:])


def take_head_longer_or_equal_token_length(words):
    return ' '.join(words[:TOKEN_LENGTH])


def process_head(words, sentences, current_index):
    sub_sentences = sentences[current_index:]
    sub_line = ' '.join(sub_sentences)
    all_sub_word = sub_line.split(' ')
    if len(all_sub_word) < TOKEN_LENGTH:
        return sub_line
    else:
        if len(words) < TOKEN_LENGTH:
            while len(words) < TOKEN_LENGTH:
                next_sentence = sentences[current_index + 1]
                next_sentence_words = next_sentence.split(' ')
                words.extend(next_sentence_words)
                current_index = current_index + 1

        head = take_head_longer_or_equal_token_length(words)
        return head


def process_tail(words, sentences, current_index):
    sub_sentences = sentences[:current_index + 1]
    sub_line = ' '.join(sub_sentences)
    all_sub_word = sub_line.split(' ')
    if len(all_sub_word) < TOKEN_LENGTH:
        return sub_line
    else:
        if len(words) < TOKEN_LENGTH:
            while len(words) < TOKEN_LENGTH:
                previous_sentence = sentences[current_index - 1]
                previous_sentence_words = previous_sentence.split(' ')
                previous_sentence_words.extend(words)
                words = previous_sentence_words
                current_index = current_index - 1

        tail = take_tail_longer_or_equal_token_length(words)
        return tail


def cut_head_tail(text):
    words = text.split(' ')
    if len(words) < TOKEN_LENGTH:
        return [TOO_SHORT_TEXT]
    else:
        head = ' '.join(words[:TOKEN_LENGTH])
        tail = ' '.join(words[len(words) - TOKEN_LENGTH:])
        return [head, tail]


def index_data(el):
    text = el['text']
    indexing_list = []
    data_aug = DataAugmentator()
    sentences = data_aug.get_all_sentences(text)
    if len(sentences) < 4:
        line = ' '.join(sentences)
        words = line.split(' ')
        if len(words) <= TOKEN_LENGTH:
            indexing_list.append(line)
        else:
            tmp_list = process_word_longer_or_equal_token_length(words)
            indexing_list.extend(tmp_list)

    else:
        line = ' '.join(sentences)
        all_word = line.split(' ')
        if len(all_word) < TOKEN_LENGTH:
            indexing_list.append(line)
        else:
            for i in range(len(sentences)):
                sentence = sentences[i]
                words = sentence.split(' ')
                if i >= 2:
                    tmp_tail = process_tail(words, sentences, i)
                    indexing_list.append(tmp_tail)

                if i <= len(sentences) - 3:
                    tmp_head = process_head(words, sentences, i)
                    indexing_list.append(tmp_head)
    return indexing_list


def get_hash_and_db(token):
    m = hashlib.sha256(token.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    hash_value = hash_code(sha256_hex)
    db = hash_value % 10_000
    return sha256_hex[:8], db


if __name__ == "__main__":
    text = '''June 17, 2018 June 3, 2018 Navya Veena, Ph.D.\nSeptum piercing – a puncture of the central nasal septum between the nostrils or a puncture between the cartilage and the septum – has recently become incredibly popular . We do not take into account FKA Twigs, Rihanna and Zoe Kravitz, who can hardly be called fans of classical style, but even Jessica Biel, Scarlett Johansson and Bella Hadid appeared with a septum on the carpet paths.\nFor the sake of justice, if we are talking about the stars, most of them are fake septum. That is, earrings in the nose that do not require a puncture. That, however, does not stop thousands of their fans around the world, who go to tattoo studios and cosmetology offices for piercing the real thing. If you, too, are crazy about this puncture option, but still can not decide, first carefully read this material. In it – five things that you need to keep in mind before the “operation”.\nDeadly diseases, such as hepatitis and HIV , can be transmitted through unsterilized needles. If you are doing a septum piercing, it is important to make sure that you are dealing with a professional who uses only sterile disposable needles and adheres to other safety rules.\nAs in the case of fresh tattoos , it is better to give up alcohol for a couple of days after the piercing. Despite the fact that even if you go to the bar right after the puncture, you are unlikely to have any serious problems, Bustle recalls that alcohol (not only inside, but also alcohol in cosmetic products ) can cause inflammation and swelling.\nIf your cosmetician does not recommend using alcohol based on the condition of your skin, it’s really best not to do it. But even if he does not say anything, it will not be superfluous to specify, and what about alcohol.\nIn the event that the septum piercing was done incorrectly, damage to the capillaries can lead to bleeding from the nose or to the release from the puncture of a translucent liquid of a reddish hue. All this is an occasion to visit the master, since you may need to use some time for self-disinfection of the puncture area, which reduces discomfort and speeds up healing .\nAlthough this is an extremely rare story, hematoma of the nasal septum is one of the most serious potential dangers associated with septum piercing. It can cause breathing difficulties and even deformation of the face if the help is not provided on time. So if your nose becomes more clogged after the puncture, but you do not have a cold, and all this is accompanied by severe swelling and uncomfortable pressure on the septum, you should consult a doctor as soon as possible to exclude any possible risks.\nIn conclusion, we recall that beauty is first health, and only then everything else. And clip earrings in the nose at the same look at all no worse than these.'''
    el = {"text": text}
    # ind_lst = index_data(el)
    # print(ind_lst)

    aug = DataAugmentator()
    sentences = aug.get_all_sub_sentences(text)
    # print(sentences)
    print('\n'.join(sentences))


    # print(get_hash_and_db(ind_lst[0]))
    # print(get_hash_and_db(ind_lst[1]))

    verify_text = '''jIf your cosmetician does not recommend using alcohol based on the condition of your skin, it’s really best not to do it. But even if he does not say anything, it will not be superfluous to specify, and what about alcohol. In the event that the septum piercing was done incorrectly, damage to the capillaries can lead to bleeding from the nose or to the release from the puncture of a translucent liquid of a reddish hue. All this is an occasion to visit the master, since you may need to use some time for self-disinfection of the puncture area, which reduces discomfort and speeds up healing . Although this is an extremely rare story, hematoma of the nasal septum is one of the most serious potential dangers associated with septum piercing. It can cause breathing difficulties and even deformation of the face if the help is not provided on time. So if your nose becomes more clogged after the puncture, but you do not have a cold, and all this is accompanied by severe swelling and uncomfortable pressure on the septum, you should consult a doctor as soon as possible to exclude any possible risks. In conclusion, we recall that beauty is first health, and only then everything else.'''
    cut_list = cut_head_tail(verify_text)
    print(cut_list)
    print(get_hash_and_db(cut_list[1]))

