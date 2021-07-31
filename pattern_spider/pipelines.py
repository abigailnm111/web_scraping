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
        self.cursor.execute(
            """
            SELECT id 
            FROM pattern
            WHERE brand = %s AND
                  name = %s
            """, (item['brand'], item['name'])
            )
        row_id=self.cursor.fetchone()
        for i in item['audiance']: 
            self.cursor.execute(
                """
                INSERT INTO audiance(id,audiance_type)
                VALUES(%s, %s)
                ON CONFLICT (id, audiance_type) DO NOTHING
                """,
                (row_id[0],i)
                )
            self.conn.commit()
        for i in item['fabric']:
            self.cursor.execute(
                """
                INSERT INTO fabrics(id, fabric)
                VALUES(%s, %s)
                ON CONFLICT (id, fabric) DO NOTHING
                """,
                (row_id[0], i)
                )
            self.conn.commit()
        for i in item['garment_type']:
            self.cursor.execute(
                """
                INSERT INTO garment_type(id, garment_type)
                VALUES(%s, %s)
                ON CONFLICT (id, garment_type) DO NOTHING
                """,
                (row_id[0], i)
                )
            self.conn.commit()
        for i in item["sizes"]:
            s_item=[s for s in i.split("-")]
            for s in s_item:
                self.cursor.execute(
                   """
                   INSERT INTO sizes(id, size)
                   VALUES(%s, %s)
                   ON CONFLICT (id, size) DO NOTHING
                   """,
                   (row_id[0], s)
                   )
            #fields to add:
            #description
        return item
    
