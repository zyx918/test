# -*- coding: utf-8 -*-
import sys

__author__ = 'xumeng'

"""
@author:xumeng
@time: 19/14/8 16:37
"""
import time
import adbUtils as aU


def exec_native_heap(s,runningminutes):
    adb = aU.ADB(s)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    f = open("output/native/"+timestamp+"_native.txt", 'a')
    i = 0
    while i < int(runningminutes):
        t = time.ctime(time.time())
        mem = adb.output("dumpsys meminfo com.miui.hybrid |grep 'Native Heap:'")
        f.write(t)
        f.write(' ')
        f.write(mem.decode('utf-8'))
        time.sleep(60)
        i = i+1
    f.close()


if __name__ == '__main__':
    exec_native_heap(sys.argv[1],sys.argv[2])
