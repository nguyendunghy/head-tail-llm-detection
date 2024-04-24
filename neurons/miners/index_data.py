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
        return None


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
        return None


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
    text = '''We may collect or obtain User Information about you: directly from you (e.g., where you contact us); in the course of our relationship with you (e.g., if you make a purchase); when you make your Personal Information public (e.g., if you make a public post about us on social media); when you download, install, or use any of our Services; when you visit our Services; when you register to use any part of the Services; or when you interact with any third party content or advertising on the Services. We may also receive User Information about you from third parties (e.g., social network sites). We may also create User Information about you, such as records of your interactions with us. Hubfoodcenter is not responsible for Personal Information you volunteer about yourself in public areas of the Services. This Policy does not cover the practices of third parties who may provide information about you to Hubfoodcenter.\nProvision of the Services to You: providing the Services to you from Hubfoodcenter or its partners including (i) offering of contests, as well as chat areas, forums and communities, (ii) posting of your personal testimonial alongside other endorsements, (iii) display of your personal reviews of products or services, (iv) allowing you to search for other website members using information you may already know about that member such as username, full name or gamer profile and identify users matching that criteria, (v) management of your account, and (vi) customer support and relationship management.\nLead Generation: business-to-business lead generation in the provision of leads to customers to improve customer’s target marketing campaigns and services through different strategies. This includes generating leads through phone calls and email newsletter marketing to drive you to content, such as white papers and webinars, offered by Hubfoodcenter B2B, emedia and Salesify, whereupon your contact information will be shared with our customer.\nMarketing to Customers: We may market to current and prospective customers and their employees who have indicated an interest in doing business with, or have previously conducted business with, Hubfoodcenter in order to further generate and promote our business. Such efforts include sending marketing emails or conducting phone calls to drive the purchase of advertising, Speedtest and Online Data licensing, lead generation and other business services offered by Hubfoodcenter.\nIT Administration: administration of Hubfoodcenter’ information technology systems; network and device administration; network and device security; implementing data security and information systems policies; compliance audits in relation to internal policies; identification and mitigation of fraudulent activity; and compliance with legal requirements.\nHubfoodcenter and/or certain third parties may collect information about you for online behavioral advertising purposes in order for you to receive relevant interest-based advertising on the Services and on other websites, platforms and media channels. We use Online Data as well as other User Information to send you online behavioral ads. Online Data is aggregated with the Other Information and data we collect and/or similar data collected by partners to create groups of users and certain general-interest categories or segments that we have inferred. We use this information to get a more accurate picture of audience interests in order to serve ads we believe are more relevant to your interests.\nTracking technologies on the Services may be deployed by Hubfoodcenter and/or by our service providers or partners. Certain tracking technologies enable us to assign a unique identifier to you, and relate information about your use of the Services to other information about you, including your User Information. We may match information collected from you through different means or at different times and use such information along with offline and online information obtained from other sources (including from third parties), including, but not limited to, demographic information and updated contact information, for the purposes of learning more about you so we can provide you with relevant content and advertising.\nHubfoodcenter and/or certain third parties may collect information about you for online behavioral advertising (“OBA”) purposes in order for you to receive relevant interest-based advertising on the Services and on other websites, platforms and media channels. OBA is also referred to as interest-based advertising.\nWith respect to surveys, in the event that responses are publicly disclosed, users will be notified at the time they take the survey. Otherwise we will disclose only aggregate information regarding its users’ responses in surveys to other participants in the survey. Where surveys allow users to submit written comments, and where Hubfoodcenter advises users of the possibility of such disclosure at the time they take the survey, Hubfoodcenter reserves the right to disclose any information provided by users, provided that no User Information identifying a specific user is disclosed.\nHubfoodcenter and some of our advertisers may use third party advertising service companies to serve advertisements, for OBA or otherwise, and perform related services when you interact with the Services. Often, these third party advertising companies employ cookies and other technologies to measure the effectiveness of website, app and email advertisements and to create a record of interaction with our content that they use in conjunction with their advertising which appears on other sites or applications, or for reporting website traffic, app use, statistics, advertisement data and/or other activities on the Services. We also engage third party providers to assist with the segmentation of this data.\nWe may also engage third parties for the purpose of recognizing our users and delivering interest-based content and advertisements to them. We may share your User Information with our partners such as your name, postal address, email, or other identifier. Our partners may also: (i) collect information directly from your device, such as your IP address, device ID, advertising ID, and information about your browser or operating system; (ii) combine User Information about you received from Hubfoodcenter with information about you from other sites or services; and (iii) place or recognize a unique cookie on your browser.\nWe may transfer your Personal Information to recipients in other countries. Hubfoodcenter participates in the E.U.-U.S. Privacy Shield, the Swiss-U.S. Privacy Shield and the APEC Cross Border Privacy Rules System. Where we transfer User Information from the European Economic Area (“EEA”) to a recipient outside the EEA that is not in an adequate jurisdiction, we do so on the basis of standard contractual clauses.\nBecause of the international nature of our business, we may need to transfer your User Information within the Hubfoodcenter group of companies, and to third parties as noted in Section 9 above, in connection with the purposes set out in this Policy. For this reason, we may transfer your User Information to other countries that may have different laws and data protection compliance requirements to those that apply in the country in which you are located.\nWe take every reasonable step to ensure that your User Information is only retained for as long as they are needed. Online Data related to OBA is kept by Hubfoodcenter for not more than 180 days after which it will expire, subject to certain conditions.\nOBA. Hubfoodcenter is a member of the Digital Advertising Alliance (“DAA”) in the U.S., E.U. and Canada and uses third party assurance platforms to comply with the DAA principles. Hubfoodcenter strives to adhere to the self-regulatory organization principles for the DAA (US), the DAAC (Canada) and the EDAA (EU). Online ads on the Services using Online Data are delivered with the DAA Ad Marker Icon , which helps users understand how their data is being used and provides choices for users who want more control. This icon is also on each of our web pages and applications where Online Data is collected that will be used for OBA purposes.\nLocation Based Services. You may opt-out of having your Precise Location Data collected by Hubfoodcenter at any time by editing the appropriate setting on your mobile device (which is usually located in the Settings area of your device).'''
    sentences = data_aug.get_all_sentences(text)
    print("len sentences: " + str(len(sentences)))
    print(sentences)
    el = {'text': text}
    result = index_data(el)
    print("len result: " + str(len(result)))
    print(result)
