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




def get_fabric_type(x):
    fab_type=[]
    types={"Stretch/Knit":"Jersey|[Kk]nit|Stretch|Interlock|Tricot|Swimwear|Sweatshirt", 
           "Denim/Canvas":"Denim|Jean|Canvas|Cordoroy", 
           "Leather/Suede/Fur":"Leather|Suede|Fur",
           "Sheer/Lace":"Sheer|Lace|Mesh|Overlay",
           "NonStretch/Woven":"Woven|Challis|Crepe|Chiffon|Gingham|Poplin|Linen|" 
                               "Charmeuse|Taffeta|Silk|Satiin|Broadcloth|Gabardine|"
                               "Batiste|Brocade|Tweed|Velvet|Lace|Lawn|Poplin"
                               "Seersucker|Twill|Velvet|Ripstop|Jacquard|Voile"                      
           }
    for key in types:
        if re.findall(types[key],x):
            if key not in fab_type:
                fab_type.append(key)
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
                fabric_type=[]
                type_search=[]
                for x in i:
                    if len(x)<79 and len(x)>3:
                        type_search= get_fabric_type(x)
                        fabric_type=[x for x in type_search if x not in fabric_type]
                        for f_type in fabric_type:
                            for f in f_type:
                                self.cursor.execute(
                                    """
                                    INSERT INTO fabric_type(id, fabric_type)
                                    VALUES(%s, %s)
                                    ON CONFLICT (id, fabric_type) DO NOTHING
                                    """,
                                    (row_id[0], f_type)
                                    )
                                self.conn.commit()
                        self.cursor.execute(
                            """
                            INSERT INTO fabrics(id, fabric)
                            VALUES(%s, %s)
                            ON CONFLICT (id, fabric) DO NOTHING
                            """,
                            (row_id[0], x)
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
    
