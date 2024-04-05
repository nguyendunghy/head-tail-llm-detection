import unittest

from detection.validator.data_augmentation import DataAugmentator


class DataAugmentatorTestCase(unittest.TestCase):

    def test_get_all_sub_sentences_1(self):
        text = '0. 1. 2'
        data_aug = DataAugmentator()
        result = data_aug.get_all_sub_sentences(text)
        self.assertEqual(result, ['0. 1. 2'])

        text = '0. 1'
        result = data_aug.get_all_sub_sentences(text)
        self.assertEqual(result, ['0. 1'])

    def test_get_all_sub_sentences_2(self):
        text = '0. 1. 2. 3'
        data_aug = DataAugmentator()
        result = data_aug.get_all_sub_sentences(text)
        self.assertEqual(result, ['0. 1. 2.', '0. 1. 2. 3', '1. 2. 3'])

    def test_get_all_sub_sentences_3(self):
        text = '0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10'
        data_aug = DataAugmentator()
        result = data_aug.get_all_sub_sentences(text)
        self.assertEqual(len(result), 44)
