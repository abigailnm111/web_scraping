# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import re

import psycopg2

conn= psycopg2.connect(
host= 'localhost',
database= 'patterndb',
user= 'postgres',
password= 'clown')

import re

x= 'Medium-Weight Two-Way Stretch Knits: Swimwear Knits'
def get_fabric_type(x):
    fab_type=[]
    types={"Stretch/Knit":["Jersey", "Knit", "Stretch", "Interlock"], 
           "Denim/Canvas":["Denim", "Jean", "Canvas"], 
           "Leather/Suede/Fur":["Leather", "Suede", "Fur"],
           "NonStretch/Woven":["Woven","Challis","Crepe", "Chiffon","Gingham", "Poplin", "Linen", 
                               "Charmeuse", "Taffeta", "Silk", "Satiin", "Broadcloth", "Gabardine"
                               "Batiste", "Brocade", "Tweed", "Velvet", "Lace","Lawn", "Poplin"
                               "Seersucker","Twill"
                               ]
           }
    
    for t in types:
        for value in types[t]:

            if re.findall(value,x):
                if t not in fab_type:
                    fab_type.append(t)

    return fab_type

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
        item.setdefault('fabric', [])
        item.setdefault('garment_type', [])
        item.setdefault('sizes', [])
        item.setdefault('description', [])
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
        if item['fabric']!= []:
            for i in item['fabric']:
                for x in i:
                    if len(x)<79 and len(x)>3:
                        fabric_type=get_fabric_type(x)
                        if len(fabric_type)>1:
                            for f_type in fabric_type:
                                self.cursor.execute(
                                    """
                                    INSERT INTO fabrics(id, fabric, fabric_type)
                                    VALUES(%s, %s, %s)
                                    ON CONFLICT (id, fabric) DO NOTHING
                                    """,
                                    (row_id[0], x, fabric_type)
                                    )
                                self.conn.commit()
                            else:
                                self.cursor.execute(
                                    """
                                    INSERT INTO fabrics(id, fabric, fabric_type)
                                    VALUES(%s, %s, %s)
                                    ON CONFLICT (id, fabric) DO NOTHING
                                    """,
                                    (row_id[0], x, fabric_type)
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
        for i in item['sizes']:
            if "," in i:
                s_item=[s for s in i.split(",")]
            else:
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
                self.conn.commit()
        if item['description']!= []:
            for i in item['description']:
                self.cursor.execute(
                    """
                    INSERT INTO garment_features(id, garment_feature)
                    VALUES(%s, %s)
                    ON CONFLICT (id, garment_feature) DO NOTHING
                    """,
                    (row_id[0], i)
                    )
                self.conn.commit()
        return item
    
