from detection.validator.data_augmentation import DataAugmentator
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
    sub_sentences = sentences[:current_index+1]
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


if __name__ == "__main__":
    text = 'Swift codes, or BIC codes as they are sometimes called, allow you to make an international wire transfer. Unlike routing numbers used for domestic wire transfers, Swift codes are only used for making international transfers. If you want to send or receive money internationally to a bank account held with BNP PARIBAS, TAIPEI BRANCH, your bank will ask for the Swift code(s) listed below..\nNotice: These Swift/BIC codes for BNP PARIBAS, TAIPEI BRANCH are only used for international wire transfer payments.'
    el = {"text": text}
    ind_lst = index_data(el)
    print(ind_lst)

    verify_text = 'Swift codes, or BIC codes as they are sometimes allow you to make an international wire transfer. Unlike routing numbers used for domestic wire transfers, Swift codes are only used for making international transfers. If you want to send or receive money internationally to a bank account held with BNP PARIBAS, TAIPEI BRANCH, your bank will ask for the Swift code(s) listed below..'
    cut_list = cut_head_tail(verify_text)
    print(cut_list)



