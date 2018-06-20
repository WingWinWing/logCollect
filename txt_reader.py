#coding: utf-8
import warnings
import re
import pandas as pd
import sys
import numpy as np

#input_file_path = '/Users/robert/Documents/doc/problemData/12_android_output/18_grep_cqd.txt'
input_file_path = '/Users/robert/Documents/doc/problemData/19_export_picture_to_video/24_grep_cqd.txt'




class TxtReader(object):
    def __init__(self, txt_path):
        self.f = open(txt_path, 'rb')

    def __del__(self):
        self.f.close()

    def _get_pts(self, line):
        split_comma_list = line.split(',')
        for item in split_comma_list:
            if 'pts =' in item:
                item = item.replace('.', '')
              #  print(item)
                return int(item.split('pts =')[-1])
            else:
                continue
        return None

    def _get_cqd(self, line):
        split_comma_list = re.split(r"\,|\ ", line) #将字符串以"," 或 “空格” 分割;
        for item in split_comma_list:
            if 'CQD' in item:
                return item
            else:
                continue
        return None

    def _get_time(self, line):
        if ' ' not in line or len(line.split(' ')) < 2:
            return None
        complete_time = line.split(' ')[1]
        ms_time = self._time_transform(complete_time)
        return ms_time

    def _time_transform(self, time):
        """
        将 hh:min:sec.mirsec 转换成 min * 60 * 1000 + sec * 1000 + mirsec;
        :param time:
        :return:
        """
        assert isinstance(time, str)
        time_split = re.split(r"\:|\.", time)
        time_multiple = [60 * 1000, 1000, 1]
        ms_time = 0
        for i, item in enumerate(time_split):
            if i == 0:
                continue
            ms_time += int(item) * time_multiple[i - 1]
        return ms_time

    def _gen_result(self):
        """

        :return:
        """
        pts_result = {}
        for i, line in enumerate(self.f.readlines()):
            pts = self._get_pts(line)   # 获取 pts = 后面的值;
            cqd = self._get_cqd(line)   # 获取 以 "," 或 “空格”分割后的字符串的，包含有 “CQD” 的字符串;
            time = self._get_time(line) # 获取当前行中时间戳，转换成 ms 为单位;

            if cqd is None:
                warnings.warn("line {} {} cqd is None.".format(i, line))
                continue
            elif pts is None:
                warnings.warn("line {} {} pts is None.".format(i, line))
                continue
            elif time is None:
                warnings.warn("line {} {} time is None.".format(i, line))
                continue
            if not pts_result.has_key(pts):
                pts_result[pts] = [cqd, time]
            else:
                pts_result[pts].append(cqd)
                pts_result[pts].append(time)
        return pts_result

    @staticmethod
    def _get_all_cqd_from_results(result):
        cqd_list = []
        for k, v in result.items():
            for item in v:
                if isinstance(item, str) and 'CQD' in item:
                    if item not in cqd_list:
                        cqd_list.append(item)
        #cqd_list = sorted(cqd_list)
        return cqd_list
    
    def _init_cqd_count(self, cqd_list):
        count_dict = {}
        for item in cqd_list:
            count_dict[item] = 0
        return count_dict

    def gen_csv(self, output_path):
        assert output_path.endswith('.xls')
        upper_limit = 20000
        pts_result = self._gen_result()
        cqd_list = ['CQD.1', 'CQD.2', 'CQD.3','CQD.4.0', 'CQD.4.1', 'CQD.5.1', 'CQD.5.2.x', 'CQD.5.2', 'CQD.5.3', 'CQD.5.4.x', 'CQD.5.4', 'CQD.6', 'CQD.7']
        items = pts_result.items()
        items.sort()
        head = ['pts'] + cqd_list
        df = pd.DataFrame(columns=head)
        for k, v in items:
            cqd_item_count_dict = self._init_cqd_count(cqd_list)
            pts_df = pd.DataFrame([[np.nan] * len(head)] * upper_limit, columns=head)
            line_index = 0
            for ind in range(len(v) / 2):   # cqd.question.1 v 中的内容，偶数表示 key, 奇数表示 value;
                item = v[ind * 2]
                max_count = max(cqd_item_count_dict.values())

                cqd_item_count_dict[item] += 1  # items 中出现了 CQD.6, 但是 cqd_item_count_dict 中未出现该 key， 故崩溃;
                if cqd_item_count_dict[item] > max_count > 0:
                    line_index += 1
                pts_df.iloc[line_index, 0] = k
                pts_df.loc[line_index, item] = v[ind * 2 + 1]
            df = df.append(pts_df.dropna(axis=0, how='all'), ignore_index=True)
        df.to_excel(output_path, header=True, index=False)


def test():
    txt_path = input_file_path  #sys.argv[1]
    out_path = txt_path.replace('txt', 'xls').replace('log', 'xls')
    TxtReader(txt_path).gen_csv(out_path)


if __name__ == '__main__':
    test()
