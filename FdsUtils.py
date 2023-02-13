import os
from fds import GalaxyFDSClient, FDSClientConfiguration
import time
from zipfile import ZIP64_LIMIT, ZipFile
import zipfile
import os.path
from datetime import date
import shutil
import utils as U

abs_path = os.path.dirname(__file__)



def current_date():

    monkey_names = str(date.today())  + "test_monkey_log.zip"
    return monkey_names

mongkey_log_path = "./output"

class FdsUtils:
    def __init__(self, bucket_name, object_name,file_path,env='prod'):
        endpoint = 'cnbj1-fds.api.xiaomi.net'
        if env == 'test':
            endpoint = 'staging-cnbj2-fds.api.xiaomi.net'
        elif env == 'russia':
            endpoint = 'ksyru0-fusion-fds.api.xiaomi.net'

        self.bucket_name = bucket_name
        self.object_name = object_name
        self.file_path = file_path
        self.client = GalaxyFDSClient(
            access_key="AK66PWVCN65F4VK3QS",
            access_secret="2uJIxbMjskXZ7ehAUd5tCaJCJSCki3hqWm7AQCaw",
            config=FDSClientConfiguration(
                endpoint=endpoint,
                enable_cdn_for_upload=False,
                enable_cdn_for_download=False,
            ),
        )

    def upload_fds(self,):
        try:
            upload_file = open(self.file_path, 'rb')
            upload_result = self.client.put_object(
                self.bucket_name, self.object_name, upload_file, metadata=None)
            print(upload_result)
            return os.path.join(self.bucket_name, self.object_name)
        except Exception as e:
            print(e)
        return None
        '''
    def download_fds(self, bucket_name, object_name, data_file):
        try:
            download_result = self.client.download_object(bucket_name, object_name, data_file)
            print("success")
        except Exception as e:
            print(e)
        return None
        '''
    def generate_fds(self,):
        try:
            generate_uri = self.client.generate_download_object_uri(self.bucket_name, self.object_name,)
            print(f"下载附件:{generate_uri}")
        except Exception as e:
            print(e)
        return None
        '''
    def get_str_from_fds(self, bucket_name, object_name):#r
        try:
            fds_object = self.client.get_object(bucket_name, object_name)
            content = fds_object.get_next_chunk_as_string()
            print(content)
        except Exception as e:
            print(e.message)
        return None
        '''
class Zipfile:

    def __init__(self,zip_name,dir_name) -> None:
        self.zip_name = zip_name
        self.dir_name = dir_name

    def compress_file(self,):
        try:
            result = os.path.exists(mongkey_log_path)
            if result != 0:
                z = zipfile.ZipFile(self.zip_name,'w', zipfile.ZIP_DEFLATED,allowZip64=True) 
                for dirpath, dirnames, filenames in os.walk(self.dir_name):
                    fpath = dirpath.replace(self.dir_name, '')
                    print(fpath)
                    fpath = fpath and fpath + os.sep or ''
                    for filename in filenames:
                        z.write(os.path.join(dirpath, filename), fpath + filename)
                        time.sleep(1)
                    U.Logging.info('压缩成功')
                z.close()

        except Exception as e:
            print(e)


class Initialization_moneky:

    def __init__(self,dir_path,file_path,judge_monkey) -> None:
        self.remove_path = dir_path
        self.file_path = file_path
        self.judge_monkey = judge_monkey
    def rmdir(self,):
        try:
            shutil.rmtree(self.remove_path,ignore_errors = False,onerror = None)
            U.Logging.info("Delete dir success")
        except Exception as e:
            print(e)
    def rmfile(self,):
        try:
            os.remove(self.file_path)
            time.sleep(1)
            os.remove(self.judge_monkey)
            U.Logging.info("Delete file success")

        except Exception as e:
            print(e)