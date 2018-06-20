import pandas as pd
import numpy as np

class Stastic(object):
    def __init__(self, xls_path):
        self.df = pd.read_excel(xls_path)

    # def cal_column_mean(self, index):
    #     column = self.df[index]
    #     mean = np.mean(np.array(column))
    #     return mean
    #
    # def add_row(self, index):
    #     add_df = pd.DataFrame

    def add_mean_line(self):
        add_df = self.df.apply(np.mean)
        out_df = self.df.append(add_df, ignore_index=True)
        return out_df


def test():
    xls_path = '/Users/robert/Documents/doc/problemData/19_export_picture_to_video/24_test.xls'
    out_df = Stastic(xls_path).add_mean_line()
    out_df.to_excel('/Users/robert/Documents/doc/problemData/19_export_picture_to_video/a.xls')
    pass


if __name__ == '__main__':
    test()