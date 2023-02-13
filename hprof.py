# -*- coding: utf-8 -*-
__author__ = 'xumeng'

"""
@author:xumeng
@time: 19/15/8 10:18
"""
import os


def hprof_to_txt(path):
    list_dirs = os.walk(path)
    for root, dirs, files in list_dirs:
        for d in dirs:
            print(os.path.join(root,d))
        for f in files:
            if f.endswith('hprof'):
                path_name = os.path.join(root, f)
                print(path_name)
                os.system(
                'shark-cli-2.6/bin/shark-cli -h ' + path_name + ' analyze > ' + path_name.replace('.hprof', '_hprof.txt'))


if __name__ == '__main__':
    hprof_to_txt('output/hprof')