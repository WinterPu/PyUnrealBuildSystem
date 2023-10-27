import requests
from urllib import request
# import wget


class FileDownloader:

    def DownloadWithRequests(url,dst_file_path):
        response = requests.get(url)
        open(dst_file_path,"wb").write(response.content)

    # def DownloadWithWget(url,dst_file_path):
    #     response = wget.download(url,dst_file_path)

    def DownloadWithUrllib(url,dst_file_path):
        response = request.urlretrieve(url,"aaa.ico")
