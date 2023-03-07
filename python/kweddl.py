""" kweddl """
import os
import platform
from urllib.parse import quote
from http.client import HTTPSConnection
import requests
import feedparser


class KwedDl():
    """ Kweddl backbone. """

    def __init__(self):
        """ Prepare class for action. """
        prefix = "_" if platform.system() == "Windows" else "."
        home = os.path.expanduser("~")
        self.counter_file = f"{home}/{prefix}kwedrc"
        self.desktop = f"{home}/Desktop"
        with open(self.counter_file, "r", encoding='utf8') as counter:
            self.base_counter = int(counter.readline().strip())


    def execute(self):
        """ Run the handler. """
        feedparser.USER_AGENT = 'kwed/5.0'
        rss = feedparser.parse('https://remix.kwed.org/rss.xml')
        if rss.bozo > 0:
            exc = str(rss.bozo_exception)
            print(str(exc.getLineNumber()) + ': ' + exc.getMessage())
            input("Press enter to exit")
            return

        counter = self.base_counter
        for item in rss['items']:
            tid = int(item['link'].split('/')[-1])
            if tid <= self.base_counter:
                continue

            url = self.get_download_url(tid)
            if url is None:
                print(str(tid) + ": no download url")
                continue

            filename = self.get_filename(item['title'])
            destination = f"{self.desktop}/{filename}.mp3"
            print("Downloading " + str(tid) + " to " + destination)
            if self.download(destination, url):
                if tid > counter:
                    counter = tid

        if counter > self.base_counter:
            with open(self.counter_file, "w+", encoding='utf8') as counter_file:
                counter_file.write(str(counter))


    @staticmethod
    def get_download_url(file_id):
        """ Get download link for link.
            Arguments:
                file_id: remix.kwed.org id
        """
        connection = HTTPSConnection('remix.kwed.org')
        connection.request('HEAD', '/download.php/' + str(file_id))
        response = connection.getresponse()
        location = response.getheader('Location')
        if location is None:
            return None

        return 'https://remix.kwed.org' + quote(location)


    @staticmethod
    def get_filename(title):
        """ Derive filename from title. Remove OS filesystem invalid
            characters.
            Arguments:
                title: KWED title.
        """
        prefix = 'New C64 remix released: '
        prefix_len = len(prefix)

        if title.startswith(prefix):
            title = title[prefix_len:]

        return title.translate({ord(c): None for c in "<>&:\\/"})


    @staticmethod
    def download(destination, url):
        """ Download the file to the destination on the desktop.
            Arguments:
                destination: full path to destination file.
                url: url to download from.
        """
        response = requests.get(url, stream=True, timeout=30)
        if response is None:
            return False

        with open(destination, "w+b") as music:
            for chunk in response.iter_content(chunk_size=4096):
                music.write(chunk)

        return True


if __name__ == '__main__':
    KwedDl().execute()
