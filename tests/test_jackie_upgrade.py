import unittest

from neurons.miners.jackie_upgrade import order_prob


class JackieUpgradeTestCase(unittest.TestCase):

    def test_order_prob_1(self):
        prob_list = [0.1, 0.2, 0.11, 0.02, 0.05, 2]
        list_pred = order_prob(prob_list)
        self.assertEqual(list_pred, [False, True, True, False, False, True])

    def test_order_prob_2(self):
        prob_list = [0.1, 0.2, 0.3, 0.4, 0.5, 6, 0.5, 0.5]
        list_pred = order_prob(prob_list)
        self.assertEqual(list_pred, [False, False, False, False, True, True, True, True])
