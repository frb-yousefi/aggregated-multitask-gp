#!/usr/bin/env python
# coding: utf-8

import numpy as np

# Standardised Mean Squared Error
def smse(mu_star_list, Y_test_list):
    error_k = []
    for k in range(len(Y_test_list)):
        res = mu_star_list[k] - Y_test_list[k]
        error = (res**2).mean()
        error = error / Y_test_list[k].var()  
        error_k.append(error)
    return np.array(error_k)

# snlp
def snlp(var_star_list, Y_train_list, Y_test_list, mu_star_list):
    error_k = []
    for k in range(len(var_star_list)):
        res = mu_star_list[k] - Y_test_list[k]
        nlp = 0.5 * (np.log(2 * np.pi * var_star_list[k]) + res**2 / var_star_list[k]).mean()
        muY = Y_train_list[k].mean()
        varY = Y_train_list[k].var()
        error = nlp - 0.5 * (np.log(2 * np.pi * varY) + ((Y_test_list - muY) ** 2) / varY).mean()
        error_k.append(error)
    return np.array(error_k)

