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


def check_real_data(prob_list):
    print("prob_list length: " + str(len(prob_list)))
    print("distinct values: " + str(len(set(prob_list))))
    pred_list = []

    for prob in prob_list:
        pred = True if prob > 0.5 else False
        pred_list.append(pred)
    true_count = pred_list.count(True)
    print("true_count: " + str(true_count))
    print(pred_list)


# This is the main function, which runs the miner.
if __name__ == "__main__":
    prob_list = [False, True, False, True, True, True, False, True, False, False, False, True, False, True, False, True, True, False, False, False, False, True, True, True, True, False, True, False, False, False, False, True, False, False, False, True, False, False, False, True, True, True, True, True, False, True, False, True, True, True]
    true_count = prob_list.count(True)
    print("true_count:" + str(true_count))
    print("prob_list length: " + str(len(prob_list)))

    real_data = [0.15216108677647214, 0.4579209618685184, 0.06006172757272946, 0.6469827309912941, 0.010377847804850699, 0.0017180291163946177, 0.799042464903298, 0.39486973180258933, 0.8373297876455509, 0.799042464903298, 3.5061068781455808e-06, 0.799042464903298, 0.799042464903298, 0.869513683730835, 0.7034905268039958, 0.6469827309912941, 4.1737236265259637e-10, 0.7034905268039958, 0.6469827309912941, 0.869513683730835, 0.028610347440133795, 3.433365527697585e-07, 0.010377847804850699, 0.869513683730835, 0.799042464903298, 0.39486973180258933, 0.00013016413431989066, 0.12175406301551235, 0.8373297876455509, 0.2802477407046338, 0.017271002420987818, 0.2802477407046338, 0.799042464903298, 0.5223494462447779, 0.5223494462447779, 0.12175406301551235, 1.923777586528014e-10, 0.4579209618685184, 0.09673015485427572, 0.8373297876455509, 0.12175406301551235, 0.06006172757272946, 0.799042464903298, 0.869513683730835, 0.09673015485427572, 0.04703823524565933, 0.33513279952074937, 0.33513279952074937, 0.8373297876455509, 0.5223494462447779]
    check_real_data(real_data)




