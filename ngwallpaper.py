#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
National Geographic Wallpaper
=============================

Please, check out https://github.com/carlosabalde/ngwallpaper
for a detailed description and other useful information.

:copyright: (c) 2014 by Carlos Abalde <carlos.abalde@gmail.com>.
:license: BSD, see LICENSE for more details.
'''

from __future__ import absolute_import
import sys
import os
import subprocess
import traceback
import argparse
import urllib2
import re
import abc
import random
import tempfile
import urlparse
from xml.etree import ElementTree
from BeautifulSoup import BeautifulSoup

FILENAME = 'ngwallpaper'

HTTP_TIMEOUT = 30


class Origin(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractproperty
    def photo(self):
        pass


class LeafOrigin(Origin):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(LeafOrigin, self).__init__()
        self._cache = []

    @property
    def photo(self):
        result = None
        if self._indices:
            index = random.choice(self._indices)
            fp = urllib2.urlopen(index, None, self._timeout)
            if fp.getcode() == 200:
                urls = self._parse_photo_urls(fp.read())
                if urls:
                    result = {
                        'index': index,
                        'url': random.choice(urls),
                    }
            fp.close()
        return result

    @property
    def _indices(self):
        if not self._cache:
            fp = urllib2.urlopen(self._root_url + self._path, None, self._timeout)
            if fp.getcode() == 200:
                options = BeautifulSoup(fp.read()).\
                    find('div', {'id': self._div_id}).\
                    findAll('option', {'value': re.compile(self._value_re)})
                self._cache = [self._root_url + option['value'] for option in options]
            fp.close()
        return self._cache

    @property
    def _root_url(self):
        return 'http://ngm.nationalgeographic.com'

    @property
    def _timeout(self):
        return HTTP_TIMEOUT

    @abc.abstractproperty
    def _path(self):
        pass

    @abc.abstractproperty
    def _div_id(self):
        pass

    @abc.abstractproperty
    def _value_re(self):
        pass

    @abc.abstractmethod
    def _parse_photo_urls(self, contents):
        pass


class Latest(LeafOrigin):
    def __init__(self):
        super(Latest, self).__init__()

    @property
    def _path(self):
        return '/wallpaper'

    @property
    def _div_id(self):
        return 'entries-wallpaper'

    @property
    def _value_re(self):
        return '^/wallpaper/\d{4}/'

    def _parse_photo_urls(self, contents):
        result = []
        gallery = BeautifulSoup(contents).find('div', {'id': 'gallery'})
        for item in gallery.findAll('a', {'target': '_blank', 'href': re.compile('^/wallpaper/img/')}):
            result.append(self._root_url + item['href'])
        return result


class Archive(LeafOrigin):
    def __init__(self):
        super(Archive, self).__init__()

    @property
    def _path(self):
        return '/wallpaper/download'

    @property
    def _div_id(self):
        return 'gallery_middle_content'

    @property
    def _value_re(self):
        return '^/wallpaper/\d{4}/.*\.xml$'

    def _parse_photo_urls(self, contents):
        result = []
        root = ElementTree.fromstring(contents)
        for photo in root.findall('photo'):
            wallpaper = photo.find('wallpaper')
            url = \
                wallpaper.text.strip() or \
                wallpaper[-1].text.strip()
            if url:
                result.append(self._root_url + url)
        return result


class ComposedOrigin(Origin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, origins):
        super(ComposedOrigin, self).__init__()
        self._origins = origins

    @property
    def photo(self):
        result = None
        if self._origins:
            result = random.choice(self._origins).photo
        return result


def download_wallpaper(url, destination):
    # Extract extension & set detination file name.
    file = os.path.join(
        destination,
        FILENAME + os.path.splitext(urlparse.urlparse(url).path)[1])

    # Download URL.
    ifp = urllib2.urlopen(url, None, HTTP_TIMEOUT)
    assert(ifp.getcode() == 200)
    with open(file, 'wb') as ofd:
        ofd.write(ifp.read())

    # Done!
    return file


def script(code):
    return subprocess.call(
        ['bash', '-c', code],
        shell=False,
        stdin=None,
        stdout=sys.stdout,
        stderr=sys.stdout)


def set_wallpaper(file):
    # See http://superuser.com/a/689804.
    assert(script('''
        sqlite3 ~/Library/Application\ Support/Dock/desktoppicture.db "update data set value = '%(file)s'"
        killall Dock
    ''' % {
        'file': file,
    }) == 0)


def main(origins, destination, retries):
    # Do not continue if all reties have been exhausted.
    if retries > 0:
        try:
            # Fetch some random photo.
            wallpaper = ComposedOrigin(origins).photo
            assert(wallpaper is not None)

            # Download selected photo.
            file = download_wallpaper(wallpaper['url'], destination)
            assert(file is not None)

            # Store meta data of the selected photo
            with open(os.path.join(destination, FILENAME + '.txt'), 'w') as fd:
                fd.write(wallpaper['index'] + '\n')

            # Set the downloaded photo as wallpaper.
            set_wallpaper(file)
        except:
            main(origins, destination, retries - 1)
    else:
        sys.stderr.write('Failed to set wallpaper!\n')
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--latest', dest='origins', required=False,
        action='append_const', const=Latest(),
        help='enable "latest" repository')

    parser.add_argument(
        '--archive', dest='origins', required=False,
        action='append_const', const=Archive(),
        help='enable "archive" repository')

    parser.add_argument(
        '--destination', dest='destination', type=str, required=False,
        default=tempfile.gettempdir(),
        help='set location of downloaded wallpapers')

    parser.add_argument(
        '--retries', dest='retries', type=int, required=False,
        default=5,
        help='number of retries before failing')

    options = parser.parse_args()

    if options.origins and options.retries > 0:
        main(options.origins, options.destination, options.retries)
    else:
        parser.print_help()
        sys.exit(1)
