#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 10:26:25 2021

@author: panda
"""
import scrapy
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose

import re

def category_search(x, type_dict):
    categories=[]
    for key in type_dict:
        if re.findall(type_dict[key],x):
            if key not in categories:
                categories.append(key)
    return categories

def line_clean(x):
     l1= re.sub(r"\r\n",'', x)
     line=re.sub(r"\n", '', l1)
     if line==' 'or line=='':
         line= None
     else:
         line= line.lstrip(" ")
     return line

def audiance_determination(x):
    audiance_types={'Adult':'Misses|Men|Women|Unisex', 
                    'Children': 'Boy|Girl|Children|Infant|Toddler',
                    'Petite':"Petite",
                    }
    new=category_search(x, audiance_types)
    if new==[]:
        new.append('Unknown')
    return new

def garment_features(x):
   descriptors=['sweatheart', 'cowl', 'square', 'V-neck', 'princess seam', 'peplum', 'bubble', 'baby doll', 'pull.*over', 
                'pleat', 'dolman', 'sleeveless', 'puff', 'highwaist', 'wrap', 'shirr', 'ruffle', 'gathered', 'blouson',
                'tiered', 'fit.+flare', 'raglan', 'ruch'
                ]
   new=[]
   for d in descriptors:
       add=re.search(f'{d}',x )
       if add != None:
           new.append(add.group())
   if new==[]:
       new.append(None)
   return new

def garment_type_determination(x):
    garment_types={"Top":'Top|Blouse|Tunic|Shirt',
                   "Dress": "Dress",
                   "Shorts": "Shorts",
                   "Pants": "Pants|Legging",
                   "Skirt": "Skirt",
                   "Vest": "Vest",
                   "Cardigan/Sweater": "Cardigan|Sweater",
                   "Jacket/Coat": "Jacket|Coat|Hoodie|Poncho",
                   "Jumpsuit/Romper/Overalls":"Jumpsuit|Romper|Overalls"
                   }
    new=category_search(x, garment_types)

    if new==[]:
        new.append("Not Available")
    return new
          
def fabric_clean(x):
    
     line= re.sub("[*].+|FABRICS:|\.|Note:|Fabric requirement allows for nap|Contrast,",'', x)
     if line== '' or line== ' ':
         return None
     else:
        new=re.findall('.+,.+|.+', line)
        return new

# def notions_clean(x):
#     line=re.sub("NOTIONS:",'', x)
    
  
def sizes_clean(x):
    line=re.sub("Size\sCombinations:",'', x)
    if line== " ":
        new= [None]
    else:
        new= re.findall('\((.+?)\)', line)
    return new

def comma_splits(x):
    if type(x)== str:
        new= x.split(',')
        for n in new:
            n=n.strip()
    else:
        new=[]
        for n in x:
            new.append([i.strip() for i in n.split(',')])
    return new 

def fabric_output(x):
    new=comma_splits(x)
    return new

def name_clean(x):
    name= re.sub("\(Digital\)",'', x).rstrip()
    return name

def none_output(x):
    new=[i for i in x if i!=None]
    return new

class Pattern(Item):
    name= Field(
        input_processor= MapCompose(name_clean),
        output_processor=TakeFirst()
        )
    audiance=Field(
        input_processor= MapCompose(line_clean, audiance_determination),
        )
    garment_type= Field(
        input_processor= MapCompose(line_clean, garment_type_determination),
        )
    description=Field(
        input_processor= MapCompose(line_clean, garment_features),
        output_processor=Compose(none_output)
        )
    fabric= Field(
        input_processor= MapCompose(line_clean, fabric_clean),
        output_processor=Compose(fabric_output)
        )
    #lambda v: v[0] if(v[0]!=None)else [None]
    # notions= Field(
    #   input_processor= MapCompose(line_clean),
    #   )
    sizes= Field(
        input_processor= MapCompose(line_clean, sizes_clean),
        output_processor=Compose(none_output)
        )
    url=Field(
        output_processor= TakeFirst(),
        )
    brand=Field(
        output_processor=TakeFirst(),
        )
    
class PatternsSpider(scrapy.Spider):
    name ='pattern_spider'
    start_urls=['https://somethingdelightful.com/mccalls/misses']
    
    def parse(self, response):
        find_category=response.css('div.category__subcat-grid-item a::attr(href)').getall()
        for c in find_category:
            yield scrapy.Request(c, callback=self.category_parse)
             
    def category_parse(self, response):
        find_pattern= response.css('h4.card-title a::attr(href)').getall()
        for pattern in find_pattern: 
            yield scrapy.Request(pattern, callback=self.description_parse)
        # next_page= response.css("li.leans-right__item.leans-right__item--next a::attr(href)").get()
        # if next_page is not None:
        #     yield scrapy.Request(next_page, callback=self.parse)

    def description_parse(self, response):
            brand='McCalls'
            NAME_SELECTOR= '.productView-title::text'
            ALT_DESCRIPTION_SELECTOR= '.productView-altTitle::text'
            DESCRIPTION_SELECTOR= '//*[@id="descriptionTab"]//text()' 
            FABRIC_SELECTOR= '//div[@id="fabricsTab"]//text()'
            # NOTIONS_SELECTOR= '//div[@id="notionsTab"]//text()'
            SIZE_SELECTOR= '//div[@id="sizeTab"]//text()'
            p=ItemLoader(item=Pattern(), response=response)
            p.add_css('name',NAME_SELECTOR)
            p.add_css('audiance', ALT_DESCRIPTION_SELECTOR)
            p.add_css('garment_type', ALT_DESCRIPTION_SELECTOR)
            p.add_xpath('description', DESCRIPTION_SELECTOR)
            p.add_xpath('fabric', FABRIC_SELECTOR)
            # p.add_xpath('notions', NOTIONS_SELECTOR)
            p.add_xpath('sizes', SIZE_SELECTOR)
            p.add_value('url', response.url)
            p.add_value('brand', brand)
            return p.load_item()
            



