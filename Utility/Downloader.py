import requests
from urllib import request
from Logger.Logger import *
# import wget


class FileDownloader:

    def DownloadWithRequests(url,dst_file_path):
        PrintLog("[Download Start] url[%s] to dst path[%s] " %(url,str(dst_file_path)))
        response = requests.get(url)
        PrintLog(str(response) + " url %s" % url)
        open(dst_file_path,"wb").write(response.content)
        PrintLog("[Download Complete] - url: " + url)

    # def DownloadWithWget(url,dst_file_path):
    #     response = wget.download(url,dst_file_path)

    def DownloadWithUrllib(url,dst_file_path):
        response = request.urlretrieve(url,"aaa.ico")
