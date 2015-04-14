**ngwallpaper is a tiny Python script useful to programmatically download and decorate your OSX desktop with randomly selected wallpapers provided by [National Geographic](http://www.nationalgeographic.com).** Supported repositories are:

- [NGM latest wallpapers](http://ngm.nationalgeographic.com/wallpaper).
- [NGM archived wallpapers](http://ngm.nationalgeographic.com/wallpaper/download).
- Miscellaneous galleries: 'Life in Color' (i.e. ['kaleidoscope'](http://photography.nationalgeographic.com/photography/photos/life-color-kaleidoscope/), ['red'](http://photography.nationalgeographic.com/photography/photos/life-color-red/), ['orange'](http://photography.nationalgeographic.com/photography/photos/life-color-orange/), etc.), ['Visions of Earth'](http://photography.nationalgeographic.com/photography/photos/visions-of-earth-wallpapers), ['Bird Wallpapers'](http://animals.nationalgeographic.com/animals/photos/bird-wallpapers/), ['Underwater Wreckage'](http://photography.nationalgeographic.com/photography/photos/underwater-wrecks/), 'Patterns in Nature' (i.e. ['flora'](http://photography.nationalgeographic.com/photography/photos/patterns-flora/), ['reflections'](http://photography.nationalgeographic.com/photography/photos/patterns-nature-reflections/), etc.), etc.

I created this script for my own personal use. It should work in older OSX versions, and it should be easily extended to support other platforms, multi-screen configurations, etc. Anyway, I haven't tested this in other platforms / configurations, and I don't plan to do that in the future :)

Usage
=====

1. Clone this repository somewhere in your computer.
    ```
    $ cd ~
    $ git clone https://github.com/carlosabalde/ngwallpaper.git
    ```

2. Install the Python libraries required by the script.
    ```
    $ sudo pip-2.7 install BeautifulSoup
    ```

3. Manually execute the script for the first time.
    ```
    $ python2.7 ~/ngwallpaper/ngwallpaper.py --use-ngm-latest --use-ngm-archive --use-miscellaneous-galleries --destination ~/Pictures/ngwallpapers/ --store --retries 100
    ```
    This should change the background of your desktop and create a couple of files in `~/Pictures/ngwallpapers/`: the wallpaper image and a text file containing some information about the image.

4. Add a new entry to your personal crontab (`crontab -e`) to periodically change your wallpaper.
    ```
    0 * * * * /opt/local/bin/python2.7 ~/ngwallpaper/ngwallpaper.py --use-ngm-latest --use-ngm-archive --use-miscellaneous-galleries --destination ~/Pictures/ngwallpapers/ --store --retries 100 > /dev/null
    ```

5. When using the `--store`, previously downloaded wallpapers are not removed. You may want to use the folder containing all those images as a source for your screen saver.
