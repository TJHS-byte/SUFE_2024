import yfinance as yf
import pandas as pd


etf_list = []
# 添加实验组基金代码
etf_list += ['512760.SS']


# 下载ETF和基金数据
def download_etf_data(etf_list, start_date, end_date):
    etf_data = {}
    for etf in etf_list:
        etf_data[etf] = yf.download(etf, start = start_date, end = end_date)
    return etf_data


# 将数据转换为DataFrame
def create_dataframe(etf_data):
    all_data = []
    for etf, data in etf_data.items():
        data['ETF'] = etf
        all_data.append(data)
    return pd.concat(all_data)


# 主函数
def main():
    start_date = '2010-01-01'
    end_date = '2023-12-31'

    etf_data = download_etf_data(etf_list, start_date, end_date)
    etf_dataframe = create_dataframe(etf_data)

    # 保存数据到CSV文件
    etf_dataframe.to_csv('etf_fund_data.csv', index = True)


if __name__ == "__main__":
    main()