'''a module to define a cache class for pictures'''
# -*- coding: utf-8 -*-

#   This file is part of emesene.
#
#    emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import Cache

class PictureCache(Cache.Cache):
    '''a class to maintain a cache of pictures
    '''
    '''a class to maintain a cache of an user avatars
    '''

    def __init__(self, config_path, user):
        '''constructor
        config_path -- the path where the base configuration is located
        user -- the user account or identifier
        '''
        Cache.Cache.__init__(self, os.path.join(config_path,
            user.strip()), 'pictures', True)

    def parse(self):
        '''parse the file that contains the dir information
        return a list of tuples containing (stamp, hash) in the order found
        on the file
        '''
        lines = {}
        with file(self.info_path) as handle:
            for line in handle.readlines():
                stamp, hash_ = line.split(' ', 1)
                lines[int(stamp)] = hash_.strip()

        return lines

    def list(self):
        '''return a list of tuples (stamp, hash) of the elements on cache
        '''
        return self.parse().items()

    def insert(self, item):
        '''insert a new item into the cache
        return the information (stamp, hash) on success None otherwise
        item -- a path to an image
        '''
        hash_ = Cache.get_file_path_hash(item)

        if hash_ is None:
            return None

        path = os.path.join(self.path, hash_)
        last_path = os.path.join(self.path, 'last')
        shutil.copy2(item, path)
        shutil.copy2(item, last_path)
        return self.__add_entry(hash_)

    def insert_url(self, url):
        '''download and insert a new item into the cache
        return the information (stamp, hash) on success None otherwise
        item -- a path to an image
        '''
        path = os.path.join(tempfile.gettempdir(), "avatars")
        try:
            urlretrieve(url, path)
        except IOError:
            log.warning("Can't read url avatar")
            return None

        return self.insert(path)

    def insert_raw(self, item):
        '''insert a new item into the cache
        return the information (stamp, hash) on success None otherwise
        item -- a file like object containing an image
        '''
        if item is None:
            return None

        position = item.tell()
        item.seek(0)
        hash_ = Cache.get_file_hash(item)

        if hash_ is None:
            return None

        path = os.path.join(self.path, hash_)
        last_path = os.path.join(self.path, 'last')
        self.create_file(path, item)

        shutil.copy2(path, last_path)

        item.seek(position)
        return self.__add_entry(hash_)

    def __add_entry(self, hash_):
        '''add an entry to the information file with the current timestamp
        and the hash_ of the file that was saved
        return (stamp, hash)
        '''
        time_info = int(time.time())
        handle = file(self.info_path, 'a')
        handle.write('%s %s\n' % (str(time_info), hash_))
        handle.close()

        return time_info, hash_

    def __remove_entry(self, hash_to_remove):
        '''remove an entry from the information file
        '''
        entries = self.list()

        handle = file(self.info_path, 'w')

        for stamp, hash_ in entries:
            if hash_ != hash_to_remove:
                handle.write('%s %s\n' % (str(stamp), hash_))

        handle.close()

    def remove(self, item):
        '''remove an item from cache
        return True on success False otherwise
        item -- the name of the image to remove
        '''
        if item not in self:
            return False

        os.remove(os.path.join(self.path, item))
        self.__remove_entry(item)
        return True

    def __contains__(self, name):
        '''return True if name is in cache, False otherwise
        this method is used to do something like
        if image_hash in cache: asd()
        '''
        return os.path.isfile(os.path.join(self.path, name))

