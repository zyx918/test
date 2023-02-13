import os
import time
import sys
import subprocess
import re
'''
需要配置执行命令后终端不关闭
右键终端-首选项-命令-命令退出时(E)：保持终端打开

执行过程中monkey程序异常后将自动重启任务：8H
判断标准：2H不产生新的crash/anr信息

'''
d1 = os.popen("adb devices").readlines()
d2 = d1[1].split('\t')[0]

#p_obj = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
def testing_monkey():
    default_value = 0
    start_time = time.time()
    while True:
        end_time = time.time()
        if (end_time-start_time) >= 10:
            print("判断是否正常",end_time)
            log_value = os.path.getsize("./test.txt")
            if log_value != default_value:
                default_value = log_value 
                start_time = end_time
                print("normal operation...")
            else:
                print("Program exception, stop this execution, create subroutine execution...")
                subprocess.call(['gnome-terminal', '--', 'python3', "run.py","runmonkey","-s",f"{d2}","--runningminutes","480"])
                sys.exit()