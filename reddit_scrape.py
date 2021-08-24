#!/usr/bin/env python

import argparse
import datetime
import json
import os
import random
import re
import sys

try:
    from urllib.request import Request, urlopen, urlretrieve
except ImportError:
    from urllib import urlretrieve
    from urllib2 import Request, urlopen

class RedditScrape(object):
    PROFILE_URL = 'https://www.reddit.com/user/{}/submitted.json'

    def __init__(self, username, directory, dry_run, prefix):
        self.username = username

        if not os.path.isdir(directory):
            raise RuntimeError('Invalid directory')

        self.directory = directory
        self.dry_run = dry_run
        self.prefix = prefix

    def scrape(self):
        user_url = self.PROFILE_URL.format(self.username)

        count = 0
        countWithoutFail = 0

        while True:
            req = Request(user_url)
            req.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0')
            response = urlopen(req)
            payload = json.loads(response.read())

            posts = payload['data']['children']

            for post in posts:
                countWithoutFail += 1
                try:
                    title = post['data']['title']
                    UTC_datetime_timestamp = float(post['data']['created_utc'])
                    local_datetime_converted = datetime.datetime.fromtimestamp(UTC_datetime_timestamp)
                    filename = str(local_datetime_converted) + ' - ' + title + '.jpg'
                    path = os.path.join(self.directory, filename)

                    #sys.stdout.write('Title: ' + title + '\n\n')
                    errorUrl = post['data']['url']
                    url = post['data']['secure_media']['oembed']['thumbnail_url']
                except (TypeError, KeyError) as e:
                    if errorUrl.find('/a/') != -1:
                        #print('---------Succeeding: ' + errorUrl + '\n')
                        downloadImgurAlbum(errorUrl[errorUrl.rindex('/')+1:], path)
                    else:
                        try:
                            download('https://i.imgur.com/' + errorUrl[errorUrl.index('/'):] + '.jpg', path)
                        except:
                            sys.stdout.write('\n<a href="' + errorUrl + '">' + title + '</a>\n')

                    continue

                if re.search('(jpg|jpeg|png|gif)', url):
                    if url[len(url)-2:] == 'fb':
                        url = url[:len(url)-3]

                    #filename = re.match('https://i.redd.it\/(\w+\.\w+)', url)
                    #if not filename:
                        # Old imgur links
                    #    filename = re.match('https://i.imgur.com\/(\w+\.\w+)', url)
                    #try:
                    #    filename = filename.group(1)
                    #except AttributeError:
                    #    # Unknown url format
                    #    continue

                    #if self.prefix:
                    #    filename = '{}-{}'.format(self.prefix, filename)

                    #filename = str(local_datetime_converted) + ' - ' + title + '.jpg'
                    #sys.stdout.write('\n' + filename + '\n')

                    if not self.dry_run:
                        #path = os.path.join(self.directory, filename)

                        download(url, path)

                        #set_comment(path, errorUrl)

                        #sys.stdout.write('.')
                        #sys.stdout.flush()
                        count += 1
                else:
                    sys.stdout.write('\n<a href="' + errorUrl + '">' + title + '</a>\n')
            if payload['data']['after']:
                user_url = self.PROFILE_URL.format(self.username) + '?after={}'.format(payload['data']['after'])
            else:
                break

        sys.stdout.write('\n')
        print('{} saved.'.format(count))
        print('{} attempted.'.format(countWithoutFail))

def main():
    parser = argparse.ArgumentParser(description="Reddit simple media scraper.")
    parser.add_argument('username', type=str)
    parser.add_argument('directory', nargs='?', default=os.path.dirname(os.path.realpath(__file__)))
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        default=False, help='Dry run')
    parser.add_argument('-p', '--prefix', dest='prefix', action='store',
        required=False, help='Filename prefix. Automatically hyphenates.')
    args = parser.parse_args()

    scraper = RedditScrape(args.username, args.directory, args.dry_run, args.prefix)
    scraper.scrape()

def downloadImgurAlbum(hash, path):
    try:
        req = Request('https://api.imgur.com/3/album/' + hash)
        req.add_header('Authorization', 'Client-ID a5a67e97ced5de3')
        data = urlopen(req).read().decode()
        albumJson = json.loads(data)

        for image in albumJson['data']['images']:
            link = json.dumps(image['link'])[1:-1]
            #sys.stdout.write(link + '\n')
            #filename = dateString + ' - ' + json.dumps(albumJson['data']['title'])[1:-1] + '.jpg'

            download(link, path)

    #else:
        #path = os.path.join(self.directory, filename[0:-4] + str(random.randint(1000,9999)) + '.jpg')
        #urlretrieve(url, path)
#except:
    except:
        #print('failed to get album')
        pass

#curl --location -g --request GET 'https://api.imgur.com/3/album/TAOoFD3' \
#--header 'Authorization: Client-ID a5a67e97ced5de3'

#def set_comment(file_path, comment_text):
    #import py_applescript
    #applescript.tell.app("Finder", 'set comment of (POSIX file "{}" as alias) to "{}" as Unicode text'.format(file_path, comment_text))

def download(url, path):
    # Check if file already exists
    if os.path.isfile(path):
        path = os.path.join(self.directory, filename[0:-4] + ' - ' + str(random.randint(100,999)) + '.jpg')

    urlretrieve(url, path)
    sys.out.write('.')

if __name__ == '__main__':
    main()
