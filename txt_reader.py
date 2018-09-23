# coding: utf-8
import warnings
import re
import pandas as pd
import sys
import numpy as np
import collections


# input_file_path = '/Users/robert/Documents/doc/problemData/26_图片导出卡死/ZHS_16_grep_pipeline.txt'    # 后面测试下，看下为什么那几个没有进入对应的表格中;
# input_file_path = '/Users/robert/Documents/doc/problemData/34_tencent/1_grep_pipeline.txt'
input_file_path = '/Users/robert/Documents/doc/problemData/53_v370_costTime/2_grep_pipeline.txt'


temp_list = [
             '1', '1.1',
             '2', '2.1', '2.2',
             '3', '3.1', '3.2', '3.3', '3.4',
             '4',
             '5', '5.1', '5.2.x', '5.2',
             '5.3.x', '5.3',
             '6',
             '7']


ANDROID_PLATFORM = 'android'
IOS_PLATFORM = 'ios'
PATTERN = "Pipeline"

platform = IOS_PLATFORM


class TxtReader(object):
    def __init__(self, txt_path):
        self.f = open(txt_path, 'rb')
        self.patten = PATTERN
        self.key_list = map(self._format_func, temp_list)
        self.vid_key = 'nan'

    @staticmethod
    def _highlight_cells(s):
        # provide your criteria for highlighting the cells here
        if s.name == 'pts':
            print 'pts'
            return ['background-color: yellow' if isinstance(v, np.float) and np.isnan(v) else '' for v in s]
        else:
            print s.name
            return ['background-color: yellow' if isinstance(v, np.float) and np.isnan(v) else '' for v in s]

    def _format_func(self, string):
        return self.patten + '.' + string

    def __del__(self):
        self.f.close()

    def _get_pts(self, line):
        # print "line = {}".format(line)
        split_comma_list = line.split(',')
        for item in split_comma_list:
            if 'pts =' in item:
                item = item.replace('.', '')
                return int(item.split('pts =')[-1])
            else:
                continue
        return None

    def _get_vid(self, line):
        # print "line = {}".format(line)
        split_comma_list = line.split(',')
        for item in split_comma_list:
            if 'vid =' in item:
                item = item.replace('.', '')
                try:
                    return int(item.split('vid =')[-1])
                except:
                    raise TypeError("line = {}, must be convert to int type".format(line))
            else:
                continue
        return self.vid_key

    def _get_key_item(self, line):
        split_comma_list = re.split(r"\,|\ ", line)  # 将字符串以"," 或 “空格” 分割;
        for item in split_comma_list:
            if self.patten in item and item in self.key_list:
                return item
            else:
                continue
        return None

    def _get_time(self, line):
        if ' ' not in line or len(line.split(' ')) < 2:
            return None and item in self.key_list

    def _time_transform(self, time):
        """
        将 hh:min:sec.mirsec 转换成 min * 60 * 1000 + sec * 1000 + mirsec;
        :param time:
        :return:
        """
        assert isinstance(time, str)
        #print "time = {}".format(time)
        time_split = re.split(r"\:|\.", time)
        time_multiple = [60 * 1000, 1000, 1]
        ms_time = 0
        for i, item in enumerate(time_split):
            if i == 0:
                continue
            try:
                ms_time += int(item) * time_multiple[i - 1]
            except:
                raise TypeError("{} must be convert to int type".format(item))
        return ms_time

    def _gen_result(self):
        """

        :return:
        """
        pts_result = {}
        for i, line in enumerate(self.f.readlines()):
            line = line.strip()
            if not len(line):
                continue

            pts = self._get_pts(line)  # 获取 pts = 后面的值;
            key_item = self._get_key_item(line)  # 获取 以 "," 或 “空格”分割后的字符串的，包含有 “CQD” 的字符串;
            time = self._get_time(line)  # 获取当前行中时间戳，转换成 ms 为单位;
            vid = self._get_vid(line)

            if key_item is None:
                warnings.warn("line {} {} cqd is None.".format(i, line))
                continue
            elif pts is None:
                warnings.warn("line {} {} pts is None.".format(i, line))
                continue
            elif time is None:
                warnings.warn("line {} {} time is None.".format(i, line))
                continue

            if not pts_result.has_key(pts):
                assert vid is not None  # when pts output first, vid must not be None.
                pts_result[pts] = collections.OrderedDict({vid: [key_item, time]})
            else:
                if pts_result[pts].has_key(vid):
                    pts_result[pts][vid].extend([key_item, time])
                    # pts_result[pts].append(time)
                else:
                    pts_result[pts][vid] = [key_item, time]
        return pts_result

    def _init_cqd_count(self):
        count_dict = {}
        for item in self.key_list:
            count_dict[item] = 0
        return count_dict

    def gen_csv(self, output_path):
        assert output_path.endswith('.xls')
        upper_limit = 20000
        pts_result = self._gen_result()

        items = pts_result.items()
        items.sort()
        head = ['pts'] + ['vid'] + self.key_list
        df = pd.DataFrame(columns=head)

        for pts, vid_dict in items:
            pts_df = pd.DataFrame([[np.nan] * len(head)] * upper_limit, columns=head)
            line_index = 0
            last_line_index = -1
            #        print v
            for k, v in vid_dict.items():
                cqd_item_count_dict = self._init_cqd_count()
                for ind in range(len(v) / 2):
                    item = v[ind * 2]
                    max_count = max(cqd_item_count_dict.values())
                    #
                    # if not cqd_item_count_dict.has_key(item):
                    #     continue
                    #
                    cqd_item_count_dict[item] += 1
                    if cqd_item_count_dict[item] > max_count > 0:
                        line_index += 1
                    if last_line_index != line_index:
                        pts_df.iloc[line_index, 0] = pts      # 根据行号，列号设置单元格的值 pts;
                        if k != 'nan':
                            pts_df.iloc[line_index, 1] = k
                        # else:
                        #     pts_df.iloc[line_index, 1] = np.nan
                        last_line_index = line_index

                    try:
                        time_stamp = float(v[ind * 2 + 1])
                        pts_df.loc[line_index, item] = time_stamp  # 通过行号与列的字符串来设置单元做的值;
                    except ValueError:
                        if v[ind * 2 + 1] is None:
                            warnings.warn("pts in {} value is None".format(v))
                        else:
                            warnings.warn("{} must be convert to int type".format(v[ind * 2 + 1]))


                line_index += 1
            df = df.append(pts_df.dropna(axis=0, how='all'), ignore_index=True)
        df.to_excel(output_path, header=True, index=False)


class AndriodTxtReader(TxtReader):
    def __init__(self, txt_path):
        super(AndriodTxtReader, self).__init__(txt_path)

    def _get_time(self, line):
        super(AndriodTxtReader, self)._get_time(line)
        # print "line = {}".format(line)
        complete_time = line.split(' ')[1]
        ms_time = self._time_transform(complete_time)
        return ms_time


class IOSTxtReader(TxtReader):
    def __init__(self, txt_path):
        super(IOSTxtReader, self).__init__(txt_path)

    def _get_time(self, line, time_index=1):
        super(IOSTxtReader, self)._get_time(line)
        complete_time = line.split(' ')[0]
        return complete_time


def test():
    txt_path = input_file_path  # sys.argv[1]
    out_path = txt_path.replace('txt', 'xls').replace('log', 'xls')

    if platform == ANDROID_PLATFORM:
        AndriodTxtReader(txt_path).gen_csv(out_path)
    elif platform == IOS_PLATFORM:
        IOSTxtReader(txt_path).gen_csv(out_path)
    else:
        raise ValueError("platform must be {} or {}.".format(ANDROID_PLATFORM, IOS_PLATFORM))


if __name__ == '__main__':
    test()
