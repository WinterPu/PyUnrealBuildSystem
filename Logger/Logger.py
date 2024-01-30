import time
import sys
import traceback

def PrintLog(content,errorcode = 0):
    cur_time = time.time()
    local_time = time.localtime(cur_time)
    strftime_date = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    strftime_secs = (cur_time - int(cur_time)) * 10000
    formated_time_stamp = "%s.%04d" % (strftime_date, strftime_secs)
    errorinfo = ""
    if errorcode != 0:
        errorinfo = "[Error] - ErrorCode: "+ str(errorcode) + " "
    print(formated_time_stamp + " " + errorinfo + str(str(content).encode(encoding='utf-8',errors = "replace")))

def PrintStageLog(content):
    cur_time = time.time()
    local_time = time.localtime(cur_time)
    strftime_date = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    strftime_secs = (cur_time - int(cur_time)) * 10000
    formated_time_stamp = "%s.%04d" % (strftime_date, strftime_secs)
    print(formated_time_stamp + " ================== [ " + str(content) + " ] ================= ")


def PrintErr(error_msg = "NoMsg"):
    PrintLog(error_msg,1)
    print(traceback.format_stack())
    
def PrintErrWithFrame(frame, error_msg = "NoMsg"):
    filename = frame.f_code.co_filename
    func_name = frame.f_code.co_name
    lineno = frame.f_lineno
    msg = "Error [%s] FuncName[%s] LineNumber[%s] In File <%s>"%(error_msg,func_name,lineno,filename)
    PrintLog(msg,1)
    print(traceback.format_stack())

    