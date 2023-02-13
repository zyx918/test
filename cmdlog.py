
import time



tpath = "./test.txt"

def crash(crash):
    day = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(tpath,"a",encoding="utf-8") as file:
        file.write(f"\n{day}" + "[Info]:" + "Found crash"f"\n{day}" + "[Info]:" + crash)

def anr(anr):
    day = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(tpath,"a",encoding="utf-8") as file:
        file.write(f"\n{day}" + "[Info]:" + "Found anr"f"\n{day}" + "[Info]:" + anr)

def log_start_times(log_start_times):
    with open(tpath,"a",encoding="utf-8") as file:
        file.write(f"\nlogcat分析开始时间: {log_start_times}")

def devices(devices):
    with open(tpath,"a",encoding="utf-8") as file:
        file.write(f"测试设备号: {devices}")

def test_all_times(test_all_times):
    with open(tpath,"a",encoding="utf-8") as file:
        file.write(f"\n总测试时长: {test_all_times} minutes")
