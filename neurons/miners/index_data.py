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
    text = "Is Your Subaru Ready For Spring?\nSpring will be in full swing in just a few weeks. Are you and your car prepared for the drastic weather change? We’re taking a guess that you have been enjoying the warmer weather lately, and because of this, we want to make sure that your car is prepared for the warmer weather, just like you! In our previous post, we gave you a few things to check under the hood. Today, your Subaru repair experts will be giving you some things to check on the exterior of your car.\nWhen was the last time you check your Subaru’s wiper blades? It’s important (and suggested) to change out your car’s wiper blades before summer hits, which is why we recommend changing them during the spring time months. After a harsh winter involving lots of mag chloride, we’re sure your windshield will appreciate the love.\nInspect your Subaru for any signs of rust. If you notice that your car has chipped paint evolving into rust, make sure you make an appointment with the Subaru repair experts in Denver immediately. If rust spreads to the rest of the body of your car, you could be in for a rude awakening.\nDouble check your car’s tire pressure. Air expands when it’s warm, which means your tires could be over inflated when warmer temperatures arise. Take a look at what your car’s manual says, and either let air out, or put some air in the tires to keep them at a safe level.\nLastly, be sure that you wash all of the road grime from winter off of your car! A clean car is a happy car.\nTo schedule a repair appointment with Denver’s most trusted Subaru experts, contact us online!"
    el = {"text": text}
    ind_lst = index_data(el)
    print(ind_lst)

    verify_text = "It’s important (and suggested) to change out your car’s wikper blades before summer hits, which is why we recommend changing them during the spring time months. After a harsh winter involving lots of mag chloride, we’re sure your windshield will appreciate the love. Inspect your Subaru for any signs of rust. If you notice that your car has chipped paint evolving into rust, make sure you make an appointment with the Subaru repair experts in Denver immediately. If rust spreads to the rest of the body of your car, you could be in for a rude awakening. Double check your car’s tire pressure. Air expands when it’s warm, which means your tires could be over inflated when warmer temperatures arise."
    cut_list = cut_head_tail(verify_text)
    print(cut_list)

    print(ind_lst[0] == cut_list[0])
    print(ind_lst[2] == cut_list[1])

