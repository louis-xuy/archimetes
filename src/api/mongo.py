# -*- coding: UTF-8 -*-
import pymongo
from pymongo import MongoClient


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Mongo(metaclass=Singleton):

    # python2 metaclass
    # __metaclass__ = Singleton

    def __init__(self, db_name, is_pro=1):

        self.db_name = db_name

        dev_read_uri = 'mongodb://ro:ReadOnly@192.168.1.40:27017'
        dev_write_uri = 'mongodb://admin:SuperPower@192.168.1.40:27017'
        pro_read_uri = 'mongodb://ro:ReadOnly@192.168.1.40:27017'
        pro_write_uri = 'mongodb://admin:SuperPower@192.168.1.40:27017'

        if is_pro:
            self.read_uri = pro_read_uri
            self.write_uri = pro_write_uri

        else:
            self.read_uri = dev_read_uri
            self.write_uri = dev_write_uri

    def connect(self):

        self.read_db = MongoClient(self.read_uri)[self.db_name]
        self.write_db = MongoClient(self.write_uri)[self.db_name]

    def close_connect(self):

        self.read_db.close()
        self.write_db.close()

    def read(self, collect_name, search_json={}):

        query_data = self.read_db[collect_name]
        return query_data.find(search_json)

    def insert(self, collect_name, data):

        if len(data) == 0:
            return []

        query_obj = self.write_db[collect_name]
        result = query_obj.insert_many(data)
        return result.inserted_ids

    def delete(self, collect_name, search_json={}):

        if len(search_json) == 0:
            return []

        result = self.write_db[collect_name].remove(search_json)
        return 'success'

    def update(self, collect_name, key, update_list):

        coll = self.write_db[collect_name]
        for d in update_list:
            coll.update({key: d[key]}, d)

        return 'success'


def test():
    a = Mongo('chaoge')
    b = Mongo('chaoge')
    print(a == b)
    print(a is b)
    print(id(a))
    print(id(b))
    # print(a.read('RecommendationAd').next())
    # print([x for x in a.insert('RecommendationUserTagsOffline', [{'user_id': '3a64b7666eca18fa',
    #                                                              'tags': {u"服务": {u"家电维修": {u"空调维修": 2, u"葫芦岛": 2}}}}])])

# test()