import time


def PrintLog(content):
    cur_time = time.time()
    local_time = time.localtime(cur_time)
    strftime_date = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    strftime_secs = (cur_time - int(cur_time)) * 10000
    formated_time_stamp = "%s.%04d" % (strftime_date, strftime_secs)
    print(formated_time_stamp + " " + content)
