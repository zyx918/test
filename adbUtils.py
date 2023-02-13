# -*- coding: utf-8 -*-
__author__ = 'xumeng'

"""
@author:xumeng
@time: 19/15/8 10:18
"""
import platform
import subprocess
import re
import os

PATH = lambda p: os.path.abspath(p)

# 判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
else:
    find_util = "grep"


# 判断是否设置环境变量ANDROID_HOME
# if "ANDROID_HOME" in os.environ:
#     if system == "Windows":
#         command = os.path.join(
#             os.environ["ANDROID_HOME"],
#             "platform-tools",
#             "adb.exe")
#     else:
#         command = os.path.join(
#             os.environ["ANDROID_HOME"],
#             "platform-tools",
#             "adb")
# else:
#     raise EnvironmentError(
#         "Adb not found in $ANDROID_HOME path: %s." %
#         os.environ["ANDROID_HOME"])


class ADB(object):
    """
    单个设备，可不传入参数device_id
    """

    def __init__(self, device_id=""):
        if device_id == "":
            self.device_id = ""
        else:
            self.device_id = "-s %s" % device_id

    def adb(self, args):
        cmd = "%s %s %s" % ('adb', self.device_id, str(args))
        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def cmd(self, args):
        c = "%s %s shell %s" % ('adb', self.device_id, str(args))
        return os.system(c)

    def popen(self, args):
        c = "%s %s %s" % ('adb', self.device_id, str(args))
        return os.popen(c)

    def popen_1(self, args):
        c = "%s %s %s" % ('adb', self.device_id, str(args))
        if system == 'Windows':
            result = os.popen(c).read()
        else:
            result = subprocess.getoutput(c)
        return result

    def output(self,args):
        cmd = "%s %s shell %s" % ('adb', self.device_id, str(args),)
        return subprocess.check_output(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def shell(self, args):
        cmd = "%s %s shell %s" % ('adb', self.device_id, str(args),)
        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def output(self, args):
        cmd = "%s %s shell %s" % ('adb', self.device_id, str(args),)
        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).stdout.read()

    def deldir(self, args):
        #创建目录
        path=args.strip()
        path=path.rstrip("\\")
        for root, dirs, files in os.walk(path, topdown=False):
          for name in files:
              os.remove(os.path.join(root,name))
          for name in dirs:
              os.rmdir(os.path.join(root,name))

    def mkdir(self, args):
        # 创建目录
        path = args.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        return True

    def is_install(self, packageName):
        """
        判断应用是否安装，已安装返回True，否则返回False
        usage: isInstall("com.example.apidemo")
        """
        if self.get_matching_app_list(packageName):
            return True
        else:
            return False

    def remove_app(self, packageName):

        """
        卸载应用
        args:
        - packageName -:应用包名，非apk名
        """
        return self.adb("uninstall %s" % packageName)

    def install_app(self, app_file):

        """
        安装app，app名字不能含中文字符
        args:
        - appFile -: app路径
        usage: install("/Users/joko/Downloads/1.apk")
        """
        return self.adb("install -r %s" % app_file)

    def get_matching_app_list(self, keyword):

        """
        模糊查询与keyword匹配的应用包名列表
        usage: getMatchingAppList("qq")
        """
        matApp = []
        for packages in self.shell(
            "pm list packages %s" %
            keyword).stdout.readlines():
                 matApp.append(bytes.decode(packages).split(":")[-1].splitlines()[0])
        return matApp

    def get_pid(self, package_name):
        """
        获取进程pid
        args:
        - packageName -: 应用包名
        usage: getPid("com.android.settings")
        """
        if system is "Windows":
            pidinfo = self.shell(
                "ps | findstr %s$" %
                package_name).stdout.read()
        else:
            pidinfo = self.shell(
                "ps | %s -w %s" %
                (find_util, package_name)).stdout.read()
        if pidinfo == '':
            return "the process doesn't exist."

        pattern = re.compile(r"\d+")
        result = bytes.decode(pidinfo).split(" ")
        result.remove(result[0])

        return pattern.findall(" ".join(result))[0]

    def kill_process(self, pid):
        """
        杀死应用进程
        args:
        - pid -: 进程pid值
        usage: killProcess(154)
        注：杀死系统应用进程需要root权限
        """
        if bytes.decode(self.shell("kill %s" %
                      str(pid)).stdout.read()).split(": ")[-1] == "":
            return "kill success"
        else:
            return bytes.decode(self.shell("kill %s" %
                              str(pid)).stdout.read()).split(": ")[-1]

    def get_network_state(self):
        """
        获取WiFi连接状态
        :return:
        """
        #print(self.output('dumpsys wifi | %s ^Wi-Fi' % find_util))
        return str.encode('enabled') in self.output('dumpsys wifi | %s ^Wi-Fi' % find_util)

    def get_data_state(self):
        """
        获取移动网络连接状态
        :return:
        """
        return str.encode('2') in self.output('dumpsys telephony.registry | %s mDataConnectionState' % find_util)

    def c_logcat(self):
        """
        :return: 清理缓存中的log
        """
        return self.adb('logcat -c')


    def logcat(self, log_path):
        return self.adb('logcat -v time > %s&' % (log_path))


    def pull(self, remote_file, local_file):
        """
        :param remote_file: 拉取文件地址
        :param local_file: 存放文件地址
        :return:
        """
        return self.adb('pull %s %s' % (remote_file, local_file))

    def quit_app(self, package_name):
        """
        退出app，类似于kill掉进程
        usage: quitApp("com.android.settings")
        """
        self.cmd("am force-stop %s" % package_name)


    def get_disk(self):
        """
        获取手机磁盘信息
        :return: Used:用户占用,Free:剩余空间
        """
        for s in self.shell('df').stdout.readlines():
            if '/mnt/shell/emulated' in s or '/storage/sdcard0' in s:
                lst = []
                for i in s.split(' '):
                    if i:
                        lst.append(i)
                return 'Used:%s,Free:%s' % (lst[2], lst[3])

if __name__ == "__main__":
    A = ADB()
    print(A.get_network_state())
