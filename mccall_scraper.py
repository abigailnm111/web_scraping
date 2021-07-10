#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 10:26:25 2021

@author: panda
"""
import scrapy
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


import re

def line_filter_out(x):
   
     l1= re.sub(r"\r\n",'', x)
     line=re.sub(r"\n", '', l1)
        
     return line



# class PatternSpiderPipline(object):
#       def process_item(self, item, spider):
#         return item                     

class Pattern(Item):
    name= Field(
        output_processor=TakeFirst(),
        )
    alt_desc= Field(
        input_processor= MapCompose(line_filter_out),
                    )
    description=Field(
        input_processor= MapCompose(line_filter_out),
        )
    fabric= Field(
        input_processor= MapCompose(line_filter_out),
        )
    notions= Field(
        input_processor= MapCompose(line_filter_out),
                   )
    sizes= Field(
        input_processor= MapCompose(line_filter_out),
                 )
    

class PatternsSpider(scrapy.Spider):
    name ='pattern_spider'
    start_urls=['https://somethingdelightful.com/mccalls/misses/tops/']
    def parse(self, response):
        find_pattern= response.css('h4.card-title a::attr(href)').getall()
        
        for pattern in find_pattern: 
            yield scrapy.Request(pattern, callback=self.description_parse)
            
        next_page= response.css("li.leans-right__item.leans-right__item--next a::attr(href)").get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def description_parse(self, response):

            NAME_SELECTOR= '.productView-title::text'
            ALT_DESCRIPTION_SELECTOR= '.productView-altTitle::text'
            DESCRIPTION_SELECTOR= '//div[@id="descriptionTab"]//text()' 
            FABRIC_SELECTOR= '//div[@id="fabricsTab"]//text()'
            NOTIONS_SELECTOR= '//div[@id="notionsTab"]//text()'
            SIZE_SELECTOR= '//div[@id="sizeTab"]//text()'
            
            p=ItemLoader(item=Pattern(), response=response)
            p.add_css('name',NAME_SELECTOR)
            p.add_css('alt_desc', ALT_DESCRIPTION_SELECTOR)
            p.add_xpath('description', DESCRIPTION_SELECTOR)
            p.add_xpath('fabric', FABRIC_SELECTOR)
            p.add_xpath('notions', NOTIONS_SELECTOR)
            p.add_xpath('sizes', SIZE_SELECTOR)
            print(p.load_item())


#<article id="productDescriptionInline">
# sub sections of article above: id="descriptionTab" id="fabricsTab" id="notionsTab" id="sizeTab"

# span class="sewing-rating">

#div class="form-field option--size"#product-listing-container > 

#m7247