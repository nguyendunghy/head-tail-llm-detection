import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from nltk.tokenize import sent_tokenize

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
    sentences = sent_tokenize(text)
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
    text = "If you follow me on my other blog, SeeSaw (it's >HERE< ) you've seen me introduce a host of new products over the 10 years I've been blogging and running shops. Some products sold well. Others didn't. Running a business is always a process. Or, as the trendies say now, a \"journey.\"\nNow I'm introducing mugs. I found a wonderful printer in the US that manufactures and drop ships. That's great for me, because the last thing I want is shelves full of inventory and trips to the post office. That was fine when I was younger, but now...no thanks. But with all the advances in print technologies and online servicing, it's now relatively easy to make a great product AND have it delivered to the customer's home in a pretty package, safe and sound.\nI've tested this cup and it passes both the visual test - it's gorgeous - and the drinkability test. I'm really picky about what kind of cup I like to drink from. They have to feel just right, with good balance, an easy to hold handle, and the right feel on the lips. I wouldn't sell a cup I don't like to use, so for what it's worth to you, this cup passes the LIZA COWAN DESIGN (that's me!) TEST."
    el = {"text": text}
    ind_lst = index_data(el)
    print(ind_lst)

    verify_text = "Some products sold Others didn't. Running a business is always a process."
    cut_list = cut_head_tail(verify_text)
    print(cut_list)

    print(ind_lst[0] == cut_list[0])
    print(ind_lst[2] == cut_list[1])

