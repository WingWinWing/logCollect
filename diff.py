# coding: utf-8
import pandas as pd
import numpy as np
import os


class Analysis(object):
    def __init__(self, xls_path):
        self.df = pd.read_excel(xls_path)
        """
        self.add_index = ['gap_cqd.3', 'gap_cqd.4', 'dur_cqd.3_4', 'gap_cqd.5.1', 'gap_cqd.5.4', 'dur_cqd.4_5.1']
        gap_cqd.3 :  表示前后相邻两帧, cqd.3 位置处的时间戳的差值, 表示 RenderEngine 接收数据的时间间隔;
        gap_cqd.4 :  表示前后相邻两帧, cqd.4 位置处的时间戳的差值，表示 RenderEngine 发送数据的时间间隔;
        dur_cqd.3_4: 表示同一帧 cqd.4 - cqd.3， 表示 RenderEngine 接收一帧到 发送渲染后帧至Encoder 的时间间隔;
        gap_cqd.5.1：表示 “当前帧 Encoder 成功输出一帧对应送入数据的时间戳” 减去 “上一帧第一次遍历输入帧的时间戳” 的差值;
        gar_cqd.5.4: 表示 Encoder 编码器吐出前后两帧数据的时间间隔;
        dur_cqd.4_5.1: “当前帧第一次接收到 RenderEngine 发送过来的数据的时间戳” 减去 “RenderEngine 发送时间的时间戳”, 表示 RenderEninge 发送的待编码帧在消息队列中耗费的时间;
        
        
        """
        self.add_index = ['gap_cqd.3', 'gap_cqd.4', 'dur_cqd.3_4', 'gap_cqd.5.1', 'gap_cqd.5.4', 'dur_cqd.4_5']#['gap_cqd.3', 'dur_cqd.3_4', 'gap_cqd.5.1', 'gap_cqd.5.4']

        self.case_dict_keys = ['cqd_3', 'cqd_4', 'cqd_5_1_first', 'cqd_5_1_last', 'cqd_5_4']
        self.first_index = 'pts'
        self.add_df = pd.DataFrame([[np.nan] * len(self.add_index)] * len(self.df), columns=self.add_index)

    @staticmethod
    def add_parameters(params, **kwargs):
        params.update(kwargs)

    @property
    def df_index(self):
        return self.df[self.first_index].drop_duplicates()

    def _case_generator(self):
        for ind in self.df_index:
            yield self.df[self.df[self.first_index] == ind]

    @staticmethod
    def _get_cqd_first(case_df, index):
        return case_df.loc[case_df.index[0], index]

    @staticmethod
    def _get_cqd_last(case_df, index):
        return case_df.loc[case_df.index[-1], index]

    @staticmethod
    def _get_last_index(case_df):
        return case_df.index[-1]

    def _get_case_dict(self, case_df):
        case_dict = dict()
        case_dict[self.case_dict_keys[0]] = self._get_cqd_first(case_df, 'CQD.3')
        case_dict[self.case_dict_keys[1]] = self._get_cqd_first(case_df, 'CQD.4')
        case_dict[self.case_dict_keys[2]] = self._get_cqd_first(case_df, 'CQD.5.1')
        case_dict[self.case_dict_keys[3]] = self._get_cqd_last(case_df, 'CQD.5.1')
        case_dict[self.case_dict_keys[4]] = self._get_cqd_last(case_df, 'CQD.5.4')
        return case_dict

    @staticmethod
    def _diff(case_dict_pre, case_dict_current, index_pre, index_current, dtype_func):
        if np.isnan(case_dict_pre[index_pre]) or np.isnan(case_dict_current[index_current]):
            return np.nan
        else:
            return dtype_func(case_dict_current[index_current]) - dtype_func(case_dict_pre[index_pre])

    def _diff_items(self, case_dict_pre, case_dict_current):
        diff_cqd_3 = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys[0], self.case_dict_keys[0], int)
        diff_cqd_4 = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys[1], self.case_dict_keys[1], int)
        diff_cqd_5_1 = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys[2], self.case_dict_keys[3], int)
        diff_cqd_5_4 = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys[4], self.case_dict_keys[4], int)
        dur_4_3 = self._diff(case_dict_current, case_dict_current, self.case_dict_keys[0], self.case_dict_keys[1], int)
        dur_51_4 = self._diff(case_dict_current, case_dict_current, self.case_dict_keys[1], self.case_dict_keys[2], int)
        diff_list = [diff_cqd_3, diff_cqd_4, dur_4_3, diff_cqd_5_1, diff_cqd_5_4, dur_51_4]
        assert len(diff_list) == len(self.add_index)
        return diff_list

    def _get_adding_colums(self):
        for index, case_df in enumerate(self._case_generator()):
            if index == 0:
                continue
            if index == 1:
                case_dict_pre = self._get_case_dict(case_df)
                continue
            case_dict_current = self._get_case_dict(case_df)
            diff_list = self._diff_items(case_dict_pre, case_dict_current)
            self.add_df.loc[self._get_last_index(case_df)] = diff_list
            case_dict_pre = case_dict_current

    def add_columns(self):
        self._get_adding_colums()
        df = pd.concat([self.df, self.add_df], axis=1)
        return df


def test():
    xls_path = '/Users/robert/Documents/doc/problemData/12_android_output/18_grep_cqd.xls'
    out_path = os.path.join(os.path.dirname(xls_path), os.path.basename(xls_path).split('.')[0] + '_add_dff.xls')
    analysis = Analysis(xls_path)
    analysis.add_columns()
    out_df = analysis.add_columns()
    out_df.to_excel(out_path, header=True, index=False)


if __name__ == '__main__':
    test()