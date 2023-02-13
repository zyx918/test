# -*- coding: utf-8 -*-
import datetime
import os
import shutil
import sys

__author__ = 'xumeng'

"""
@author:xumeng
@time: 19/14/8 16:37
"""
import subprocess
import click
import time
import utils as U
import adbUtils as aU
from threading import Thread
import native as N
import hprof as H
import FdsUtils as F
import cmdlog as C
import terminal as T
command = "adb logcat -b all"  # 具体命令
keyword_crash = "am_crash"
keyword_anr = "am_anr"
package_name = "com.miui.hybrid"


@click.group()
def cli():
    pass


@cli.command()
@click.option('-s', default="", prompt=u'-s 请指定一个或多个测试设备', help=u"设备id")
@click.option('--mode', type=click.Choice(['uiautomatormix', 'uiautomatordfs']), default="uiautomatormix",
              help=u"uiautomatormix是随机点击控件加monkey模式，uiautomatordfs是遍历控件模式")
@click.option('--runningminutes', default="1", help=u"执行时间")
@click.option('--pctuiautomatormix', default="70", help=u"仅仅只有uiautomatormix模式需要填写uiautomator和monkey的比例")
@click.option('--throttle', default="400", help=u"点击间隔")
def runmonkey(s, mode, runningminutes, pctuiautomatormix, throttle):
    try:
        U.Logging.info(s)
        C.devices(s)
        subprocess.getoutput("adb -s " + s + " root")
        subprocess.getoutput("adb -s " + s + " logcat -b all -c")
        flag = __initialization_arrangement(s)
        if flag:
            # 执行monkey测试
            threads = []
            t1 = Thread(target=__start_new_monkey, args=(s, mode, runningminutes, pctuiautomatormix, throttle))
            threads.append(t1)
            t2 = Thread(target=N.exec_native_heap, args=(s, runningminutes))
            threads.append(t2)
            t4 = Thread(target=T.testing_monkey,args=())
            threads.append(t4)
            t3 = Thread(target=trace_logcat, args=(s, runningminutes))
            threads.append(t3)
            for t in threads:
                t.setDaemon(True)
                t.start()
            t.join()
            time.sleep(120)
            print("threading end")
            __teardown_arrangement(s)
            fds_monkey_logcat(runningminutes)

    except Exception as e:
        # 异常退出保存log
        U.Logging.error('error is %s' % e)


def __initialization_arrangement(serial):
    # 初始化log
    try:
        adb = aU.ADB(serial)
        U.Logging.info("init logs in device %s" % serial)
        adb.c_logcat()
        # 推送必要的jar包和配置文件到手机
        U.Logging.info("get network state on %s" % serial)
        wifi_state = adb.get_network_state()
        data_state = adb.get_data_state()
        U.Logging.info('wifi_state is %s , data_state is %s ' % (wifi_state, data_state))
        if wifi_state | data_state:
            U.Logging.info("push the monkey jars to %s" % serial)
            process = adb.adb('push framework.jar /sdcard/')
            stdout, stderr = process.communicate()
            if str.encode('error') in stdout:
                U.Logging.error('error is %s' % stdout)
                return False
            adb.adb('push monkey.jar /sdcard/')
            adb.adb('push max.config /sdcard/')
            adb.adb('push apps.strings /sdcard/')
            adb.adb('push awl.strings /sdcard/')
            U.Logging.info("reset disk to %s" % serial)
            adb.shell('rm -rf /sdcard/aimonkey')
            adb.deldir("output")
            adb.mkdir("output")
            adb.mkdir("output/native")
            adb.mkdir("output/hprof")
            adb.mkdir("output/bugreport")
            adb.mkdir("output/ANRInfo")
            U.Logging.info("install apk to %s" % serial)
            flag_install = adb.is_install("com.miui.qmonkey")
            # 屏蔽通知栏
            adb.install_app('apk/simiasque-debug.apk')
            adb.shell('am broadcast -a org.thisisafactory.simiasque.SET_OVERLAY --ez enable true')
            if not flag_install:
                adb.install_app('apk/quickcenter.apk')
                U.Logging.info("install set ")
            return True
        else:
            U.Logging.warn("no network on %s" % serial)
            return False
    except Exception as e:
        # 异常退出保存log
        U.Logging.error('error is %s' % e)
        return False


def __start_new_monkey(serial, mode, runningminutes, pctuiautomatormix, throttle):
    U.Logging.info("run the AI monkey cmd")
    if mode == 'uiautomatormix':
        cmd = 'adb -s %s shell "CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin tv.panda.test.monkey.Monkey ' \
              '-p com.miui.hybrid -p com.miui.qmonkey --%s --running-minutes %s --ignore-crashes --ignore-timeouts --throttle %s --act-blacklist-file /sdcard/awl.strings --system /sdcard/apps.strings -v -v --output-directory /sdcard/aimonkey > /sdcard/monkeyout.txt 2>/sdcard/monkeyerr.txt" ' % (
                  serial, mode, runningminutes, throttle)
    else:
        cmd = 'adb -s %s shell "CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin tv.panda.test.monkey.Monkey ' \
              '-p com.miui.hybrid -p com.miui.qmonkey --%s --running-minutes %s --pct-uiautomatormix %s --ignore-crashes --ignore-timeouts --throttle %s --act-blacklist-file /sdcard/awl.strings -v -v --output-directory /sdcard/aimonkey > /sdcard/monkeyout.txt 2>/sdcard/monkeyerr.txt"' % (
                  serial, mode, runningminutes, pctuiautomatormix, throttle)
    U.Logging.info(cmd)
    U.Logging.info("waiting for 10s")
    U.Logging.info("testing for %s minutes" % runningminutes)
    C.test_all_times(runningminutes)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def trace_logcat(s, runningminutes):
    adb = aU.ADB(s)
    begin_time = time.time()
    U.Logging.info("logcat分析开始时间：%s" % begin_time)
    C.log_start_times(begin_time)
    # 实时监控并过滤每一行生成的日志里的关键字
    p_obj = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    U.Logging.info("Logcat catching and filtering...")
    tag = 0
    anr_file_list = []
    rootDir = os.path.abspath(os.getcwd())
    for line in p_obj.stdout:
        ok_line = line.decode('utf-8', 'ignore')
        # 处理crash
        if keyword_crash in ok_line and package_name in ok_line:
            U.Logging.info(ok_line)
            U.Logging.info("Found crash")
            C.crash(ok_line)
            r = get_bugReport(s)
            # bugreport获取完成后，获取当前时间，如果当前时间 - monkey开始时间< runningminutes,则继续分析logcat，否则不再分析logcat
            if r:
                execute_time = r - begin_time
                if int(execute_time) > int(runningminutes) * 60:
                    break
        # 处理anr
        elif keyword_anr in ok_line and package_name in ok_line:
            U.Logging.info(ok_line)
            U.Logging.info("Found anr")
            C.anr(ok_line)
            r = get_bugReport(s)
            time.sleep(3)
            anr_file = adb.popen_1('shell ls -l /data/anr')
            for i in range(anr_file.count('\n') - 1):
                anr_file_name = anr_file.split('\n')[i + 1].split(' ')[-1]
                anr_file_list.append(anr_file_name)
            adb.adb('pull /data/anr output/ANRInfo')
            for i in range(len(anr_file_list)):
                if not anr_file_list[i].__contains__(datetime.datetime.now().strftime("%Y")):
                    file_dir = os.path.join(rootDir, 'output', 'ANRInfo', 'anr', anr_file_list[i])
                    while not os.path.exists(file_dir):
                        time.sleep(1)
                    if file_dir.__contains__('txt'):
                        os.rename(file_dir, os.path.join(rootDir, 'output', 'ANRInfo', 'anr',
                                                         'anr' + '_' + anr_file_list[
                                                             i].split('.txt')[0] + datetime.datetime.now().strftime(
                                                             "%Y-%m-%d-%H-%M-%S")))
                    else:
                        os.rename(file_dir, os.path.join(rootDir, 'output', 'ANRInfo', 'anr',
                                                         'anr' + '_' + anr_file_list[
                                                             i] + datetime.datetime.now().strftime(
                                                             "%Y-%m-%d-%H-%M-%S")))
            # bugreport获取完成后，获取当前时间，如果当前时间 - monkey开始时间< runningminutes,则继续分析logcat，否则不再分析logcat
            if r:
                execute_time = r - begin_time
                if int(execute_time) > int(runningminutes) * 60:
                    break
        else:
            #当前行没有crash或anr，那么设置一个标志位，每判断一行，标志位+1，当标志位的值是100(这个值自己设置)的倍数时，获取当前时间，校验和开始时间的时间差
            tag += 1
            if tag % 100 == 0:
                now = time.time()
                temp = now - begin_time
                if int(temp) > int(int(runningminutes) * 60):
                    U.Logging.info('monkey 结束了，日志分析结束...')
                    os.system("touch ./judge_monkey")
                    break


def get_bugReport(s):
    cmd = "adb  -s " + s + " bugreport"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print('抓284log的进程ID', p.pid)
    if p.returncode == 0:
        bugreport_endTime = time.time()
        return bugreport_endTime


def __teardown_arrangement(serial):
    # 处理log,将结果全部移动至output文件夹
    rootDir = os.getcwd()
    try:
        adb = aU.ADB(serial)
        U.Logging.info("quit app")
        adb.quit_app('com.miui.hybrid')
        U.Logging.info("push the result files to output")
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        adb.adb('logcat -d>output/' + timestamp + '.log')
        adb.shell('mv /sdcard/monkeyout.txt /sdcard/aimonkey')
        adb.shell('mv /sdcard/monkeyerr.txt /sdcard/aimonkey')
        adb.shell('mv /sdcard/crash-dump.log /sdcard/aimonkey')
        time.sleep(10)
        adb.adb('pull /sdcard/aimonkey output')
        adb.adb('pull /data/data/com.miui.hybrid/files/leakcanary output/hprof').communicate()
        adb.adb('pull /sdcard/Download/leakcanary-com.miui.hybrid output/hprof').communicate()
        adb.shell('rm -rf /sdcard/Download/leakcanary-com.miui.hybrid')
        adb.shell('rm -rf /data/data/com.miui.hybrid/files/leakcanary')
        H.hprof_to_txt("output/hprof")
        for file in os.listdir(rootDir):
            if file.startswith('bugreport-') and file.endswith('.zip'):
                shutil.move(rootDir + '/' + file, rootDir + '/output/bugreport')
        os.system("mv ./test.txt ./output/test.txt")
        U.Logging.info("######### test finished ##########")
    except Exception as e:
        # 异常退出保存log
        U.Logging.error('error is %s' % e)
        return False

def fds_monkey_logcat(runningminutes):
    # 检查程序是否正常运行完成，运行完成自动上传相关日志到fds
    try:
        judge = os.popen("ls ./").read().split('\n')
        if "judge_monkey" in judge:
            zip = F.Zipfile(f"{F.current_date()}","./output")
            zip.compress_file()
            fds = F.FdsUtils('qaquickapp',f'monkey/{F.current_date()}',f"{F.current_date()}",'prod')
            fds.upload_fds()
            fds.generate_fds()
            init = F.Initialization_moneky("./output",f"./{F.current_date()}","./judge_monkey")
            init.rmdir()
            init.rmfile()
            U.Logging.info("######### Log uploaded successfully ##########")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    cli(sys.argv[1:])
