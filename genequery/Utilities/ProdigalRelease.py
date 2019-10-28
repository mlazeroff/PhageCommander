import platform
import os
from subprocess import Popen, PIPE
import pathlib
import requests
import bs4
import re

GITHUB_URL = 'https://github.com'
PRODIGAL_RELEASE_URL = 'https://github.com/hyattpd/Prodigal/releases'
_LINUX = 'linux'
_WINDOWS = 'windows'
_OSX = 'osx'


class ProdigalRelease:
    """
    Class of operations to get the latest Prodigal Release
    """

    SUPPORTED_SYSTEMS = [_WINDOWS, _LINUX, _OSX]

    def __init__(self):
        self._releaseRequest = None
        self._releaseSoup = None
        self._version = ''
        self.releaseUrls = {system: None for system in self.SUPPORTED_SYSTEMS}
        self._getReleaseInfo()

    @property
    def version(self):
        return self._version

    def getBinary(self, system: str, location: str) -> str:
        """
        Download the latest Prodigal binary
        :param system: the target operating system
        :param location: directory of where to save the binary
        :return full path of file location
        """
        # check if path exists
        if not os.path.exists(location):
            raise IsADirectoryError('\"{} is not a valid directory\"'.format(location))

        system = system.lower()
        if system == 'darwin':
            system = _OSX

        # check if specified system is supported
        if system not in self.SUPPORTED_SYSTEMS:
            raise ValueError('Prodigal does not support this system: {}'.format(system))

        # download file
        with requests.get(self.releaseUrls[system]) as r:
            r.raise_for_status()
            fileName = 'prodigal-{}-{}'.format(self.version, system)
            if system == _WINDOWS:
                fileName += '.exe'
            location = pathlib.Path(location)
            fullPath = location / fileName
            with open(fullPath, 'wb') as file:
                for chunk in r.iter_content(chunk_size=10 * 1024):
                    if chunk:
                        file.write(chunk)

        # make linux and mac versions executable
        if system == _LINUX or system == _OSX:
            proc = Popen('chmod +x {}'.format(fullPath), stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = proc.communicate()

        return str(fullPath)

    def _getReleaseInfo(self):
        """
        Retrieves information about the latest release
        Information includes:
            * version
            * download URLs for each supported system
        """
        self._releaseRequest = requests.get(PRODIGAL_RELEASE_URL)
        self._releaseSoup = bs4.BeautifulSoup(self._releaseRequest.text, 'html.parser')
        latestRelease = self._releaseSoup.find(attrs={'class': 'release-entry'})

        # get latest release tag
        releaseTag = latestRelease.find(attrs={'class': 'css-truncate-target'})
        if releaseTag is not None:
            self._version = releaseTag.text

        # get download urls for each OS type (Windows, Linux, OSX)
        releaseUrls = latestRelease.find_all('a', attrs={'href': re.compile(r'/hyattpd/Prodigal/releases/download/')})
        for url in releaseUrls:
            for system in self.releaseUrls:
                if system in url['href']:
                    self.releaseUrls[system] = GITHUB_URL + url['href']


if __name__ == '__main__':
    release = ProdigalRelease()
    binary = release.getBinary(platform.system(), r'C:\Users\mdlaz\Desktop')
    print(binary)
