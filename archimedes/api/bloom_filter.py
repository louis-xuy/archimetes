import pyreBloom
import time
import datetime
import ast
import sys

from redis_ul import RedisUl


# maxmemory 4096mb
# maxmemory-policy allkeys-lru

class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Bf():

    # __metaclass__ = Singleton

    def __init__(self):

        self.capacity = 500
        self.error_rate = 0.01
        self.redis_obj = RedisUl()

    def filter_ad_by_user(self, user_id, ad_id_list):

        p = pyreBloom.pyreBloom(user_id, self.capacity, self.error_rate)
        in_ele = set(p.contains([x[0] for x in ad_id_list]))
        return [x for x in ad_id_list if x[0] not in in_ele]

    def save(self, user_id, ad_id_list, method='rec'):

        if type(ad_id_list) != list:
            ad_id_list = [ad_id_list]
        p = pyreBloom.pyreBloom(user_id, self.capacity, self.error_rate)
        p.extend(ad_id_list)
        self.redis_obj.insert(user_id, ad_id_list, method)

    def build_from_redis(self):

        user_id_list = self.redis_obj.select('user_id', num=0, method='rec')
        user_id_list += self.redis_obj.select('user_id', num=0, method='view')
        for user_id in user_id_list:
            p = pyreBloom.pyreBloom(user_id, self.capacity, self.error_rate)
            p.delete()
            p.extend(self.redis_obj.select(user_id))

    def delete_user_list(self):

        user_id_list = self.redis_obj.select('user_id', num=0, method='rec')
        user_id_list += self.redis_obj.select('user_id', num=0, method='view')
        for user_id in user_id_list:
            p = pyreBloom.pyreBloom(user_id, self.capacity, self.error_rate)
            p.delete()
        self.redis_obj.delete_user_list()

def test():
    a = Bf()
    a.build_from_redis()
    # a.save_traffic('123', 'x')
    # a.save_traffic('123', ['y', 'm'])
    # print a.filter_ad_by_user('123', ['w', 'x', 'y', 'z'])


def build():
    a = Bf()
    a.build_from_redis()


def delete():
    a = Bf()
    a.delete_user_list()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'del':
        delete()
    else:
        build()

