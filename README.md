**ngwallpaper is a tiny Python script useful to programmatically download and decorate your OSX desktop with randomly selected wallpapers from the [collection provided by National Geographic](http://ngm.nationalgeographic.com/wallpaper).**

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
    $ python2.7 ~/ngwallpaper/ngwallpaper.py --latest --archive --destination ~/Pictures/ --retries 5
    ```
    This should change the background of your desktop and create a couple of files in `~/Pictures/`: the wallpaper image and a text file containing some information about the image.

4. Add a new entry to your personal crontab (`crontab -e`) to periodically change your wallpaper.
    ```
    0 * * * * /opt/local/bin/python2.7 ~/ngwallpaper/ngwallpaper.py --latest --archive --destination ~/Pictures/ --retries 5
    ```
