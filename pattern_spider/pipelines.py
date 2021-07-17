# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import psycopg2

conn= psycopg2.connect(
host= 'localhost',
database= 'patterndb',
user= 'postgres',
password= '***')

class PatternSpiderPipeline:
    def process_item(self, item, spider):
        return item
