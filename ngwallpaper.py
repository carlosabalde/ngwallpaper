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
import time
import subprocess
import argparse
import urllib2
import hashlib
import re
import glob
import abc
import random
import tempfile
import urlparse
from xml.etree import ElementTree
from BeautifulSoup import BeautifulSoup

FILENAME = 'ngwallpaper'
EXTENSIONS = ['.jpg', '.jpeg', '.png']

HTTP_TIMEOUT = 30

MISCELANEOUS_GALLERIES = [
    # Life in Color.
    'http://photography.nationalgeographic.com/photography/photos/life-color-kaleidoscope/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-red/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-orange/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-yellow/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-green/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-blue/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-purple/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-gold/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-silver/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-white/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-brown/',
    'http://photography.nationalgeographic.com/photography/photos/life-color-black/',
    # Patterns in Nature.
    'http://photography.nationalgeographic.com/photography/photos/patterns-flora/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-nature-reflections/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-landscapes/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-nature-trees/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-animals/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-butterflies/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-nature-rainbows/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-island-aerials/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-snow-ice/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-rocks-lava/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-water/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-coral/',
    'http://photography.nationalgeographic.com/photography/photos/patterns-aurorae/',
    # Other.
    'http://photography.nationalgeographic.com/photography/photos/visions-of-earth-wallpapers',
    'http://animals.nationalgeographic.com/animals/photos/bird-wallpapers/',
    'http://photography.nationalgeographic.com/photography/photos/underwater-wrecks/',
    'http://photography.nationalgeographic.com/photography/photos/mysterious-earth/',
    'http://photography.nationalgeographic.com/photography/photos/ocean-soul/',
    'http://photography.nationalgeographic.com/photography/photos/extreme-earth/',
    'http://photography.nationalgeographic.com/photography/photos/megatransect-gallery/',
    'http://photography.nationalgeographic.com/photography/photos/cave-exploration/',
    'http://photography.nationalgeographic.com/photography/photos/volcano-exploration/',
    'http://photography.nationalgeographic.com/photography/photos/north-pole-expeditions/',
    'http://adventure.nationalgeographic.com/adventure/everest/climbing-everest-photo-gallery/',
    'http://adventure.nationalgeographic.com/adventure/mount-everest-photo-gallery',
]


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

    @property
    def _timeout(self):
        return HTTP_TIMEOUT

    def _expand_href(self, url, href):
        if href.startswith('http://') or href.startswith('https://'):
            return href
        elif href.startswith('//'):
            return 'http:' + href
        else:
            parsed = urlparse.urlparse(url)
            return parsed.scheme + '://' + parsed.netloc + href


class NGMOrigin(LeafOrigin):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(NGMOrigin, self).__init__()
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


class NGMLatest(NGMOrigin):
    def __init__(self):
        super(NGMLatest, self).__init__()

    @property
    def _path(self):
        return '/wallpaper'

    @property
    def _div_id(self):
        return 'entries-wallpaper'

    @property
    def _value_re(self):
        return r'^/wallpaper/\d{4}/'

    def _parse_photo_urls(self, contents):
        result = []
        gallery = BeautifulSoup(contents).find('div', {'id': 'gallery'})
        for item in gallery.findAll('a', {'target': '_blank', 'href': re.compile(r'^/wallpaper/img/')}):
            result.append(self._expand_href(self._root_url, item['href']))
        return result


class NGMArchive(NGMOrigin):
    def __init__(self):
        super(NGMArchive, self).__init__()

    @property
    def _path(self):
        return '/wallpaper/download'

    @property
    def _div_id(self):
        return 'gallery_middle_content'

    @property
    def _value_re(self):
        return r'^/wallpaper/\d{4}/.*\.xml$'

    def _parse_photo_urls(self, contents):
        result = []
        root = ElementTree.fromstring(contents)
        for photo in root.findall('photo'):
            wallpaper = photo.find('wallpaper')
            url = \
                wallpaper.text.strip() or \
                wallpaper[-1].text.strip()
            if url:
                result.append(self._expand_href(self._root_url, url))
        return result


class MiscellaneousGalleriesOrigin(LeafOrigin):
    def __init__(self, urls):
        super(MiscellaneousGalleriesOrigin, self).__init__()
        self._urls = urls

    @property
    def photo(self):
        # Initializations.
        gallery_url = random.choice(self._urls)
        wallpaper_url = None
        result = None

        # Select random wallpaper page URL from gallery.
        fp = urllib2.urlopen(gallery_url, None, self._timeout)
        if fp.getcode() == 200:
            options = []
            for item in BeautifulSoup(fp.read()).\
                    find('div', {'id': 'gallery'}).\
                    findAll('p', {'class': 'wallpaper_link'}):
                options.append(item.find('a')['href'])
            if len(options) > 0:
                wallpaper_url = self._expand_href(
                    gallery_url,
                    random.choice(options))
        fp.close()

        # Fetch wallpaper page URL and extract image URL.
        if wallpaper_url is not None:
            fp = urllib2.urlopen(wallpaper_url, None, self._timeout)
            if fp.getcode() == 200:
                result = {
                    'index': gallery_url,
                    'url': self._expand_href(
                        wallpaper_url,
                        BeautifulSoup(fp.read()).
                            find('div', {'id': 'content_top'}).
                            find('div', {'class': 'download_link'}).
                            find('a')['href']),
                }
            fp.close()

        # Done!
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


def wallpaper_exists(destination, filename):
    for extension in EXTENSIONS:
        if len(glob.glob(destination + filename + extension)) > 0:
            return True
    return False


def download_wallpaper(url, destination, filename):
    # Initializations.
    file = None

    # Extract extension.
    extension = os.path.splitext(urlparse.urlparse(url).path)[1].lower()

    # Do not continue if the extension is not supported.
    if extension in EXTENSIONS:
        # Set destination file name.
        file = os.path.join(
            destination,
            filename + extension)

        # Download URL.
        ifp = urllib2.urlopen(url, None, HTTP_TIMEOUT)
        assert \
            ifp.getcode() == 200, \
            'Got unexpected HTTP response'
        with open(file, 'wb') as ofd:
            ofd.write(ifp.read())
        ifp.close()

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
    assert \
        script('''
            sqlite3 ~/Library/Application\ Support/Dock/desktoppicture.db "update data set value = '%(file)s'"
            killall Dock
        ''' % {
            'file': file,
        }) == 0, \
        'Failed to set wallpaper'


def main(origins, destination, store, retries):
    # Initializations.
    file = None

    # Try to download a new wallpaper until all retries have been exhausted.
    for i in xrange(retries, 0, -1):
        # Initializations.
        file = None

        # Add some delay.
        time.sleep(min(float((retries - i) * 100), 5000.0) / 1000.0)

        # Ignore exceptions.
        try:
            # Fetch some random photo.
            wallpaper = ComposedOrigin(origins).photo
            assert \
                wallpaper is not None, \
                'Failed to fetch wallpaper'

            # Calculate destination filename.
            filename = FILENAME
            if store:
                filename += '-' + hashlib.sha256(wallpaper['url']).hexdigest()

            # Skip if the file already exists.
            if not store or not wallpaper_exists(destination, filename):
                # Download selected photo.
                file = download_wallpaper(wallpaper['url'], destination, filename)
                assert \
                    file is not None, \
                    'Failed to download wallpaper'

                # Store meta data of the selected photo
                with open(os.path.join(destination, filename + '.txt'), 'w') as fd:
                    fd.write(wallpaper['index'] + '\n')
                    fd.write(wallpaper['url'] + '\n')

                # Done!
                break
            else:
                sys.stdout.write('%(attempt)d: %(message)s\n' % {
                    'attempt': i,
                    'message': 'wallpaper already exists (%s)' % wallpaper['url'],
                })
        except Exception as e:
            sys.stdout.write('%(attempt)d: %(message)s\n' % {
                'attempt': i,
                'message': 'unexpected failure (%s)' % e,
            })

    # If a new wallpaper was not downloaded, try to use an existing one.
    if store and file is None:
        downloaded = []
        for extension in EXTENSIONS:
            downloaded.extend(glob.glob(destination + FILENAME + '-*' + extension))
        if len(downloaded) > 0:
            file = random.choice(downloaded)

    # Set the selected wallpaper.
    if file is not None:
        set_wallpaper(file)
    else:
        sys.stderr.write('Failed to select a wallpaper!\n')
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--use-ngm-latest', dest='origins', required=False,
        action='append_const', const=NGMLatest(),
        help='enable "NGM latest" repository')

    parser.add_argument(
        '--use-ngm-archive', dest='origins', required=False,
        action='append_const', const=NGMArchive(),
        help='enable "NGM archive" repository')

    parser.add_argument(
        '--use-miscellaneous-galleries', dest='origins', required=False,
        action='append_const', const=MiscellaneousGalleriesOrigin(MISCELANEOUS_GALLERIES),
        help='enable "Miscellaneous galleries" repository')

    parser.add_argument(
        '--destination', dest='destination', type=str, required=False,
        default=tempfile.gettempdir(),
        help='set location of downloaded wallpapers')

    parser.add_argument(
        '--store', dest='store', required=False,
        action='store_true',
        help='if enabled previously downloaded wallpapers are not removed')

    parser.add_argument(
        '--retries', dest='retries', type=int, required=False,
        default=100,
        help='number of retries before failing / using a previously downloaded wallpaper')

    options = parser.parse_args()

    if options.origins and options.retries > 0:
        main(options.origins, options.destination, options.store, options.retries)
    else:
        parser.print_help()
        sys.exit(1)
