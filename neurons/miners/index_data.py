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
    text = '''British lawmakers are to question the country's financial regulator about whether it was lobbied by ministers to change its rules and lure the $2tn flotation of Saudi's Aramco to London.\nThe fears come amid claims that UK Prime Minister Theresa May and senior government ministers actively attempted to lobby Riyadh for the UK to host the sell-off of the world's biggest energy company.\nAndrew Bailey, head of the Financial Conduct Authority, will be questioned by MPs Nicky Morgan, who chairs the Treasury Committee, and Rachel Reeves, who chairs the Business, Energy and Industrial Strategy Committee. A date has yet to be set for the hearings.\nOn Friday, Morgan made public a joint letter that the two MPs sent to Bailey. In it they asked seven questions, including whether the FCA was \"aware of any interest shown by Saudi Aramco in obtaining a UK listing, and if known, how far that interest influenced the consultation?\"\nMorgan told City AM that the FCA had to maintain its role as the body that preserves the reputation of Britain's financial institution.\n“The UK has a world-class reputation for upholding strong corporate governance,” she said. “The FCA must protect this reputation, especially as the City looks to remain competitive and thrive post-Brexit.” The pair plan to discuss Bailey's response with their fellow committee members.\nRiyadh is selling a five percent portion of Aramco as part of its Vision 2030 strategy, which aims to cut the kingdom's reliance on oil - which has suffered reduced prices in recent years - and raise $200bn during the next several years.\nThe FCA is a regulatory body which operates independently of the UK government. It did not mention Aramco when it announced the rule change in July, nor asked during the consultation period whether the flotations by a sovereign state should have a separate category.\nBoth New York and London have vied for Aramco to host its flotation at their respective stock exchanges.\nIn April, UK Prime Minister Theresa May, visited Riyadh to meet Aramco's chief executive, Khalid al-Falih, who is also the kingdom's energy minister.\nAccompanied by Nikhil Rathi, the head of the London Stock Exchange, May attempted to lure Falih to allow London to host Aramco's flotation.\nDowning Street sources also told the Guardian that London's plans to host the flotation were specifically mentioned during several meetings between May and Saudi ministers in April.\nThe FCA confirmed that it received the letter and said it would reply in due course. It expects to complete its rule change consultation next month.\nA survey by the Chartered Institute for Securities and Investment (CISI) of more than 200 financial service professionals has found that a majority are opposed to the rule changes.'''
    el = {"text": text}
    # ind_lst = index_data(el)
    # print(ind_lst)

    aug = DataAugmentator()
    sentences = aug.subsample_sentences(text)
    print(sentences['text'])

    # print(get_hash_and_db(ind_lst[0]))
    # print(get_hash_and_db(ind_lst[1]))

    # verify_text = 'MellodyFountaine. xxwantedbabyxx. MelissaColt. CARADEMENINOHappyVikkiXtremCockAnastasiaStele .Stefano86PIERCeCUmFUCKjeanexxx0MizzWendy .AmberKush0MizzWendyOrrianaxLovelyTeachr .0MizzWendyblackVScatleticSweetAylineeMikiAble .claudiaangel4uAmberKushblackVSatleticXElizaX .blackVSatleticjeanexxxAdelineAd3AnastasiaStele .GoddesssOfLoveeTiaCyrusdimemoletayrasensualxxx .JustUniqueNiceJohnXxxxninacpxxxDania1 .PIERCeCUmFUCKLeylaDelice1PrettyyBaby19kinkyrochellexx1 .NinaCrystalTylorLeeSweetAylineeAnastasiaStele .xxAriaxxDania1AnnaDiamondXXAmberKush .'
    # cut_list = cut_head_tail(verify_text)
    # print(cut_list)
