import pandas as pd
import numpy as np
from scipy.optimize import minimize
import csv

def synthetic_control(data, etf_codes, outcome, treated_etf, pre_period):
    #干预前控制组（其他etf）的特征数据矩阵
    X_pre = data.loc[data['Date'].isin(pre_period), etf_codes].values
    y_treated_pre = data.loc[(data['Code'] == treated_etf) & (data['Date'].isin(pre_period)), outcome].values
    #目标函数，通过最小化实验组（目标etf）和合成控制组（线性组合的控制组eft）之间的误差来确定权重
    def objective_function(weights):
        y_synthetic = np.dot(X_pre.T, weights)
        return np.sum((y_treated_pre - y_synthetic) ** 2)
    #设置约束条件和边界
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0, 1) for _ in range(X_pre.shape[1])]
    #使用scipy优化求解权重
    result = minimize(objective_function, x0=np.ones(X_pre.shape[1]) / X_pre.shape[1],
                      constraints=constraints, bounds=bounds)
    weights = result.x
    #计算干预后目标值
    # y_synthetic_post = np.dot(data.loc[data['Date'].isin(post_period), etf_codes].values.T, weights)
    # y_treated_post = data.loc[(data['Code'] == treated_etf) & (data['Date'].isin(post_period)), outcome].values
    return weights