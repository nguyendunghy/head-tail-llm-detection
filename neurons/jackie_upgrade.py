import copy


def order_prob(prob_list):
    temp_prob_list = copy.deepcopy(prob_list)
    temp_prob_list.sort()
    mid_index = len(prob_list) // 2
    mid_prob = temp_prob_list[mid_index]
    pred_list = []
    for prob in prob_list:
        pred = False if prob < mid_prob else True
        pred_list.append(pred)
    # half of element is True, half of element is False
    true_count = pred_list.count(True)
    if true_count > len(prob_list) // 2:
        num_update = true_count - len(prob_list) // 2
        for i in range(0, len(prob_list)):
            if num_update == 0:
                break
            else:
                if prob_list[i] == mid_prob:
                    pred_list[i] = False
                    num_update = num_update - 1
    elif true_count < len(prob_list) // 2:
        num_update = len(prob_list) // 2 - true_count
        for i in range(0, len(prob_list)):
            if num_update == 0:
                break
            else:
                if prob_list[i] == mid_prob:
                    pred_list[i] = True
                    num_update = num_update - 1
    return pred_list


def accuracy_monitor(pred_list, log_prefix):
    tmp_pred_list = copy.deepcopy(pred_list)
    first_half = tmp_pred_list[:len(pred_list) // 2]
    second_half = tmp_pred_list[len(pred_list) // 2:]
    count_false = first_half.count(False)
    count_true = second_half.count(True)
    print(log_prefix + " wrong count_false: " + str(len(pred_list) // 2 - count_false))
    print(log_prefix + " wrong count_true: " + str(len(pred_list) // 2 - count_true))


# This is the main function, which runs the miner.
if __name__ == "__main__":
    pred_list = [True, False, True, False, True, False]
    accuracy_monitor(pred_list, 'test-test-accuracy_monitor')

    input_data = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    curr_model_pred = [True, False, False, True, True, False, True, False]
    curr_model_prob = [0.3, 0.1, 0.15, 0.4, 0.45, 0.2, 0.5, 0.11]

    old_model_pred = [False, False, False, True, True, True, False, True]
    old_model_prob = [0.12, 0.1, 0.15, 0.4, 0.45, 0.22, 0.1, 0.5]

    not_agree_list = []
    not_agree_point = []
    arr_len = len(input_data)
    for i in range(arr_len):
        if curr_model_pred[i] != old_model_pred[i]:
            not_agree_list.append(i)
            not_agree_point.append(curr_model_prob[i] + old_model_prob[i])
    print("not_agree_list: " + str(not_agree_list))
    print("not_agree_point: " + str(not_agree_point))

    agree_pred = order_prob(not_agree_point)
    print("agree_pred: " + str(agree_pred))
    pt = 0
    for i in not_agree_list:
        curr_model_pred[i] = agree_pred[pt]
        pt += 1
    print("curr_model_pred final: " + str(curr_model_pred))
