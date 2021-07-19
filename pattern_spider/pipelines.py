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
password= 'clown')

item=['Adult']
cursor=conn.cursor()
cursor.execute(
 """
 INSERT INTO audiance(audiance_type)
 VALUES(%s)
 """,
 ('Adult',)
 )
conn.commit()

class PatternSpiderPipeline:
    
    def open_spider(self, spider):
        self.conn= psycopg2.connect(
        host= 'localhost',
        database= 'patterndb',
        user= 'postgres',
        password= 'clown')
        self.cursor=self.conn.cursor()
        
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
        
    def process_item(self, item, spider):
        self.cursor.execute(
            """
            INSERT INTO pattern(brand, url, name)
            VALUES (%s,%s,%s)
            ON CONFLICT ON CONSTRAINT unique_name_brand DO NOTHING
            """,
            (item['brand'], item['url'], item['name'])
            )
        self.conn.commit()
        for i in item['audiance']: 
            self.cursor.execute(
                """
                INSERT INTO audiance(audiance_type)
                VALUES(%s)
                """,
                (i,)
                )
            self.conn.commit()
            #fields:
            #audiance
            #garment_type
            #description
            #fabric
            #sizes
            
        return item
    
