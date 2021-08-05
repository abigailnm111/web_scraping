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


def line_clean(x):
     l1= re.sub(r"\r\n",'', x)
     line=re.sub(r"\n", '', l1)
     if line==' 'or line=='':
         line= None
     else:
         line= line.lstrip(" ")
     return line

def audiance_determination(x):
    new=[]
    if re.findall('Misses|Men|Women|Unisex',x):
        new.append('Adult')
    if re.findall('Boy|Girl|Children|Infant|Toddler',x):
        new.append('Children')
    if re.findall('Petite',x):
        new.append("Petite")
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
    new=[]
    if re.findall('Top|Blouse|Tunic|Shirt',x):
        new.append("Top")
    if re.findall('Dress',x):
        new.append("Dress")
    if re.findall("Shorts",x):
        new.append("Shorts")
    if re.findall("Pants|Legging",x):
        new.append("Pants")
    if re.findall("Skirt",x):
        new.append("Skirt")
    if re.findall("Vest", x):
        new.append("Vest")
    if re.findall("Cardigan|Sweater",x):
        new.append("Cardigan/Sweater")
    if re.findall("Jacket|Coat|Hoodie|Poncho",x):
        new.append("Jacket/Coat")
    if re.findall("Jumpsuit|Romper|Overalls",x):
        new.append("Jumpsuit/Romper/Overalls")
    if new==[]:
        new.append("Not Available")
    return new
          
def fabric_clean(x):
    
     line= re.sub("[*].+|FABRICS:|\.|Note:|Fabric requirement allows for nap,",'', x)
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
            
        #new= [i.split(', ') for i in x]
    return new 

def fabric_output(x):
   # new=none_output(x)
    new=comma_splits(x)
    for n in new:
        for i in n:
             if len(i)>79 or len(i)<3:
                 n.remove(i)
    return new


def none_output(x):
    new=[i for i in x if i!=None]
    return new

class Pattern(Item):
    name= Field(
        output_processor=TakeFirst(),
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
            DESCRIPTION_SELECTOR= '//article[@id="descriptionTab"]//text()' 
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
            

#<article id="productDescriptionInline">
# sub sections of article above: id="descriptionTab" id="fabricsTab" id="notionsTab" id="sizeTab"

# span class="sewing-rating">

#div class="form-field option--size"#product-listing-container > 

