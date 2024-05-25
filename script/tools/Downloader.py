from constants import *
import requests
import os
import time


class Downloader:

    @classmethod
    def remove_file(cls, path: str) -> bool:
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception:
            return False

    @classmethod
    def download_requests(cls, link: str, path: str) -> bool:
        try:
            r = requests.get(link, stream=True)
            total_size = int(r.headers.get("content-length", 0))
            dl = 0
            chunk_size = 1024
            with open(path, "wb") as apk:
                for data in r.iter_content(chunk_size=chunk_size):
                    dl += len(data)
                    apk.write(data)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def download_curl(cls, link: str, path: str, origin: str = None) -> bool:
        try:
            command = "curl \'{link}\' \
  -H \'authority: cloud.liteapks.com\' \
  -H \'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\' \
  -H \'accept-language: pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7\' \
  -H \'cookie: cf_clearance=fVBjQrFARKQz_M1fiV9to5CVA5T0dTq582n6cBAA1_0-1710690170-1.0.1.1-7G_UVySgiidQEWED2.F.QUe5aMEnje.ycegV.WwojxJjDddUgNTN9GN3h9VSQ0WZPpBwhERGn1glr8e3JvWZBQ\' \
   " + f'-H \'referer: {origin}\'' if origin else '' + " \
  -H \'sec-ch-ua: \'Chromium\';v=\'122\', \'Not(A:Brand\';v=\'24\', \'Google Chrome\';v=\'122\'\' \
  -H \'sec-ch-ua-mobile: ?0\' \
  -H \'sec-ch-ua-platform: \'Linux\'\' \
  -H \'sec-fetch-dest: document\' \
  -H \'sec-fetch-mode: navigate\' \
  -H \'sec-fetch-site: same-site\' \
  -H \'sec-fetch-user: ?1\' \
  -H \'upgrade-insecure-requests: 1\' \
  -H \'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\'"
            command += f" --output {path}"
            os.system(command)
        except Exception as e:
            print(e)
            return False
        return True

    @classmethod
    def download_chrome(self, link: str, path: str, timeout=100) -> bool:
        try:
            dowloads = os.listdir("/home/anfreire/Downloads")
            os.system(
                f"timeout 150 chromium-browser '{link}' 2> /dev/null > /dev/null &"
            )
            checks = timeout / 10 + 1
            new_file = None
            print()
            while checks:
                time.sleep(10)
                new_downloads = os.listdir("/home/anfreire/Downloads")
                new_files = list(set(new_downloads) - set(dowloads))
                checks -= 1
                if len(new_files) > 0 and new_files[0].endswith(".apk"):
                    new_file = new_files[0]
                    break
                print(f"Downloading manually: {10 - checks:.0f} / 10")
            if not new_file:
                return False
            os.rename(f"/home/anfreire/Downloads/{new_file}", path)
            return True
        except Exception as e:
            print(e)
            return False
