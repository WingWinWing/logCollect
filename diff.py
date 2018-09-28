# coding: utf-8
import pandas as pd
import numpy as np
import os

xls_path = '/Users/robert/Documents/doc/problemData/53_v370_costTime/20180928/3_grep_Pipeline.xls'
#xls_path = '/Users/robert/Documents/doc/problemData/20_pipeline/ios/7_grep_Pipeline.xls'
PATTERN = 'Pipeline.'



class AddIndex(object):
    def __init__(self):
        self.gap_cqd_1 = 'gap_1'
        self.dur_cqd_1_3 = 'dur_1_3'
        self.dur_cqd_1_2 = 'dur_1_2'

        # RenderEngne
        self.gap_cqd_3 = 'gap_3'
        self.dur_cqd_3_31 = 'dur_3_3.1'

        self.dur_cqd_31_34 = 'dur_3.1_3.4'
        self.dur_cqd_32_33 = 'dur_3.2_3.3'
        self.dur_cqd_1_34 = 'dur_1_3.4'
        self.dur_cqd_1_4 = 'dur_1_4'
        self.dur_cqd_3_4 = 'dur_3_4'
        self.gap_cqd_4 = 'gap_4'

        # Encoder
        self.gap_cqd_5 = 'gap_5'
        self.dur_cqd_51_52 = 'dur_5.1_5.2'
        self.gap_cqd_5_3 = 'gap_5.3'
        self.gap_cqd_6 = 'gap_6'

        # Muxer
        self.gap_cqd_7 = 'gap_7'



    def tolist(self):
        return [self.gap_cqd_1,
                self.dur_cqd_1_3,
                self.dur_cqd_1_2,

                # RenderEngne
                self.dur_cqd_3_31,
                self.dur_cqd_31_34,
                self.dur_cqd_32_33,
                self.dur_cqd_1_34,
                self.dur_cqd_1_4,
                self.dur_cqd_3_4,
                self.gap_cqd_3,
                self.gap_cqd_4,

                # Encoder
                self.gap_cqd_5,
                self.dur_cqd_51_52,
                self.gap_cqd_5_3,
                self.gap_cqd_6,

                # Muxer
                self.gap_cqd_7
                ]

    def _check(self, index_list):
        temp_list = []
        for item in index_list:
            if item in temp_list:
                return False
            else:
                if item not in self.__dict__.values():
                    return False
                else:
                    temp_list.append(item)
        return True

    def __len__(self):
        return len(self.tolist())

    def get_values_from_dict(self, input_dict):
        values = []
        for k in self.tolist():
            assert k in input_dict.keys()
            values.append(input_dict[k])
        return values



class CaseDictKeys(object):
    def __init__(self):
        self.cqd_1 = 'cqd_1'
        self.cqd_2 = 'cqd_2'
        self.cqd_2_1 = 'cqd_2_1'
        self.cqd_2_2 = 'cqd_2_2'
        self.cqd_3 = 'cqd_3'
        self.cqd_3_1 = 'cqd_3_1'
        self.cqd_3_2 = 'cqd_3_2'
        self.cqd_3_3 = 'cqd_3_3'
        self.cqd_3_4 = 'cqd_3_4'
        self.cqd_4 = 'cqd_4'
        self.cqd_5 = 'cqd_5'
        self.cqd_5_1_first = 'cqd_5_1_first'
        self.cqd_5_2 = 'cqd_5_2'
        self.cqd_5_3 = 'cqd_5_3'
        self.cqd_6 = 'cqd_6'
        self.cqd_7 = 'cqd_7'



class Analysis(object):
    def __init__(self, xls_path):
        self.df = pd.read_excel(xls_path)
        """
        self.add_index = ['gap_cqd.3', 'gap_cqd.4', 'dur_cqd.3_4', 'gap_cqd.5.1', 'gap_cqd.5.4', 'dur_cqd.4_5.1','dur_cqd_3_1']
        gap_cqd.3 :  表示前后相邻两帧, cqd.3 位置处的时间戳的差值, 表示 RenderEngine 接收数据的时间间隔;
        gap_cqd.4 :  表示前后相邻两帧, cqd.4 位置处的时间戳的差值，表示 RenderEngine 发送数据的时间间隔;
        dur_cqd.3_4: 表示同一帧 cqd.4 - cqd.3， 表示 RenderEngine 接收一帧到 发送渲染后帧至Encoder 的时间间隔;
        gap_cqd.5.1：表示 “当前帧 Encoder 成功输出一帧对应送入数据的时间戳” 减去 “上一帧第一次遍历输入帧的时间戳” 的差值;
        gar_cqd.5.4: 表示 Encoder 编码器吐出前后两帧数据的时间间隔;
        dur_cqd.4_5.1: “当前帧第一次接收到 RenderEngine 发送过来的数据的时间戳” 减去 “RenderEngine 发送时间的时间戳”, 表示 RenderEninge 发送的待编码帧在消息队列中耗费的时间;
        
        
        """

        self.pattern = PATTERN
        self.add_index = AddIndex()
        self.case_dict_keys = CaseDictKeys()

        self.first_index = 'pts'

        # list 乘标量表示将list 扩展;
        self.add_df = pd.DataFrame([[np.nan] * len(self.add_index)] * len(self.df),
                                   columns=self.add_index_list)  # 根据源 excel 文件的行数，及要添加的列数，分配空间;

    @property
    def add_index_list(self):
        return self.add_index.tolist()

    # @property
    # def case_dict_keys_list(self):
    #     return self.case_dict_keys.tolist()

    @staticmethod
    def add_parameters(params, **kwargs):
        params.update(kwargs)

    @property
    def df_index(self):
        """
        取出所有的列索引为 pts 的列的所有内容 ,并去除重复值;
        :return:    pts 列表;
        """
        return self.df[self.first_index].drop_duplicates()

    def _case_generator(self):
        """
        生成器: 取出源 excel 文件中 pts 等于 某pts 对应的所有的行;
        :return:
        """
        for ind in self.df_index:
            yield self.df[self.df[self.first_index] == ind]

    @staticmethod
    def _get_cqd_first(case_df, index):
        """
        取出 case_df 表格中"第0行,index 列"的值;
        :param case_df: 某相同pts 的各行组成的表格;
        :param index:   列号
        :return:        返回 case_df 表格中"第0行,index 列"的值;
        """
        return case_df.loc[case_df.index[0], index]  # 取出 case_df 第0行, 列号为 index 的单元的值;

    @staticmethod
    def _get_cqd_last(case_df, index):
        return case_df.loc[case_df.index[-1], index]

    @staticmethod
    def _get_last_index(case_df):
        return case_df.index[-1]

    def _gen_case_dict_key_single(self, func, index):
        base_key = index.replace('.', '_')
        key = '{}_{}'.format(self._dtype(func), base_key)
        return key

    def _dtype(self, func):
        if func == self._get_cqd_first:
            return 0
        elif func == self._get_cqd_last:
            return 1
        else:
            raise ValueError("Input must be self._get_cqd_first or self._get_cqd_last.")

    def _get_func_from_dtype(self, dtype):
        if dtype == 0:
            return self._get_cqd_first
        elif dtype == 1:
            return self._get_cqd_last
        else:
            raise ValueError("Input must be 0 or 1.")

    def _get_case_dict(self, case_df):
        case_dict = dict()

        case_dict[self.case_dict_keys.cqd_1] = self._get_cqd_first(case_df,  self.pattern + '1')
        case_dict[self.case_dict_keys.cqd_2] = self._get_cqd_first(case_df,  self.pattern + '2')
        case_dict[self.case_dict_keys.cqd_2_1] = self._get_cqd_first(case_df,self.pattern + '2.1')
        case_dict[self.case_dict_keys.cqd_2_2] = self._get_cqd_first(case_df,self.pattern + '2.2')

        case_dict[self.case_dict_keys.cqd_3] = self._get_cqd_first(case_df, self.pattern + '3')

        case_dict[self.case_dict_keys.cqd_3_1] = self._get_cqd_last(case_df, self.pattern + '3.1')
        case_dict[self.case_dict_keys.cqd_3_2] = self._get_cqd_last(case_df, self.pattern + '3.2')
        case_dict[self.case_dict_keys.cqd_3_3] = self._get_cqd_last(case_df, self.pattern + '3.3')
        case_dict[self.case_dict_keys.cqd_3_4] = self._get_cqd_last(case_df, self.pattern + '3.4')

        case_dict[self.case_dict_keys.cqd_4] = self._get_cqd_last(case_df, self.pattern + '4')
        case_dict[self.case_dict_keys.cqd_5] = self._get_cqd_last(case_df, self.pattern + '5')

        case_dict[self.case_dict_keys.cqd_5_1_first] = self._get_cqd_first(case_df, self.pattern + '5.1')
        case_dict[self.case_dict_keys.cqd_5_2] = self._get_cqd_first(case_df, self.pattern + '5.2')
        case_dict[self.case_dict_keys.cqd_5_3] = self._get_cqd_first(case_df, self.pattern + '5.3')

        case_dict[self.case_dict_keys.cqd_6] = self._get_cqd_last(case_df, self.pattern + '6')
        case_dict[self.case_dict_keys.cqd_7] = self._get_cqd_last(case_df, self.pattern + '7')

        return case_dict

    # @staticmethod
    def _diff(self, case_dict_pre, case_dict_current, index_pre, index_current, dtype_func):
        if np.isnan(float(case_dict_pre[index_pre])) or np.isnan(float(case_dict_current[index_current])):
            return np.nan
        else:
            return dtype_func(case_dict_current[index_current]) - dtype_func(case_dict_pre[index_pre])

    def _diff_items(self, case_dict_pre, case_dict_current):
        diff_dict = dict()
        diff_dict[self.add_index.gap_cqd_1] = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys.cqd_1,
                                                         self.case_dict_keys.cqd_1, int)

        diff_dict[self.add_index.dur_cqd_1_3] = self._diff(case_dict_current, case_dict_current,self.case_dict_keys.cqd_1, self.case_dict_keys.cqd_3, int)

        key_cqd_2 = self.case_dict_keys.cqd_2
        if np.isnan(case_dict_current[self.case_dict_keys.cqd_2]): # case_dict_current[self.case_dict_keys.cqd_2] 值存在时
            key_cqd_2 = self.case_dict_keys.cqd_2_2

        diff_dict[self.add_index.dur_cqd_1_2] = self._diff(case_dict_current, case_dict_current,
                                                           self.case_dict_keys.cqd_1, key_cqd_2, int)

        diff_dict[self.add_index.dur_cqd_3_31] = self._diff(case_dict_current, case_dict_current,
                                                             self.case_dict_keys.cqd_3, self.case_dict_keys.cqd_3_1, int)

        diff_dict[self.add_index.dur_cqd_31_34] = self._diff(case_dict_current, case_dict_current,
                                                             self.case_dict_keys.cqd_3_1, self.case_dict_keys.cqd_3_4,
                                                             int)

        diff_dict[self.add_index.dur_cqd_32_33] = self._diff(case_dict_current, case_dict_current,
                                                             self.case_dict_keys.cqd_3_2, self.case_dict_keys.cqd_3_3,
                                                             int)

        diff_dict[self.add_index.dur_cqd_1_34] = self._diff(case_dict_current, case_dict_current,
                                                           self.case_dict_keys.cqd_1, self.case_dict_keys.cqd_3_4,
                                                           int)

        diff_dict[self.add_index.dur_cqd_1_4] = self._diff(case_dict_current, case_dict_current,
                                                            self.case_dict_keys.cqd_1, self.case_dict_keys.cqd_4,
                                                            int)



        diff_dict[self.add_index.dur_cqd_3_4] = self._diff(case_dict_current, case_dict_current,
                                                             self.case_dict_keys.cqd_3, self.case_dict_keys.cqd_4,
                                                             int)

        diff_dict[self.add_index.gap_cqd_3] = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys.cqd_3,
                                                         self.case_dict_keys.cqd_3, int)

        diff_dict[self.add_index.gap_cqd_4] = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys.cqd_4, self.case_dict_keys.cqd_4, int)

        diff_dict[self.add_index.gap_cqd_5] = self._diff(case_dict_pre, case_dict_current, self.case_dict_keys.cqd_5,
                                                         self.case_dict_keys.cqd_5, int)

        diff_dict[self.add_index.dur_cqd_51_52] = self._diff(case_dict_current, case_dict_current,
                                                           self.case_dict_keys.cqd_5_1_first,
                                                           self.case_dict_keys.cqd_5_2, int)

        diff_dict[self.add_index.gap_cqd_5_3] = self._diff(case_dict_pre, case_dict_current,
                                                           self.case_dict_keys.cqd_5_3, self.case_dict_keys.cqd_5_3,
                                                           int)

        diff_dict[self.add_index.gap_cqd_6] = self._diff(case_dict_pre, case_dict_current,
                                                           self.case_dict_keys.cqd_6, self.case_dict_keys.cqd_6,
                                                           int)

        diff_dict[self.add_index.gap_cqd_7] = self._diff(case_dict_pre, case_dict_current,
                                                         self.case_dict_keys.cqd_7, self.case_dict_keys.cqd_7,
                                                         int)

        return diff_dict

    def _get_adding_colums(self):  # 将要计算的结果存于 self.add_df 中;
        for index, case_df in enumerate(self._case_generator()):  # 每次取出源表格中某个相同的 pts 的所有行;最终会遍历所有的不同的pts的行;
            if index == 0:
                continue
            if index == 1:
                case_dict_pre = self._get_case_dict(case_df)  # case_df 存储的是 pts 值相同的所有行构成的表格;
                continue
            case_dict_current = self._get_case_dict(case_df)
            diff_dict = self._diff_items(case_dict_pre, case_dict_current)
            self.add_df.loc[self._get_last_index(case_df)] = self.add_index.get_values_from_dict(diff_dict)
            case_dict_pre = case_dict_current

    def add_columns(self):
        self._get_adding_colums()
        df = pd.concat([self.df, self.add_df], axis=1)  # axis=1 列合并(行索引相同的行合成一行;)
        return df


def test():
    out_path = os.path.join(os.path.dirname(xls_path), os.path.basename(xls_path).split('.')[0] + '_add_dff.xls')
    analysis = Analysis(xls_path)
    out_df = analysis.add_columns()
    out_df.to_excel(out_path, header=True, index=False)


if __name__ == '__main__':
    test()
