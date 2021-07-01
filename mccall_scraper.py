#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 10:26:25 2021

@author: panda
"""
import scrapy

from urllib import request
from bs4 import BeautifulSoup

url=request.urlopen('https://somethingdelightful.com/m8200')
soup= BeautifulSoup(url, 'html.parser')
html=soup.prettify()

description=soup.find('div', {'id':'descriptionTab'})
#soup('descriptionTab')
#f= open('html.txt', "w")
#f.write(html)
#f.close()

#print(description)

class PatternsSpider(scrapy.Spider):
    name ='paterns_spider'
    start_urls=['https://somethingdelightful.com/m8200']
    def parse(self, response):
        SET_SELECTOR= '#productDescriptionInline'
        for pattern in response.css(SET_SELECTOR):
            DESCRIPTION_SELECTOR= '#descriptionTab::text'
            FABRIC_SELECTOR= '#fabricsTab::text'
            NOTIONS_SELECTOR= '#notionsTab::text'
            yield{
                'description': pattern.css(DESCRIPTION_SELECTOR).extract_first(),
                'fabric':pattern.css(FABRIC_SELECTOR).extract_first(),
                'notions': pattern.css(NOTIONS_SELECTOR).extract_first(),
                }



#<article id="productDescriptionInline">
# sub sections of article above: id="descriptionTab" id="fabricsTab" id="notionsTab" id="sizeTab"

# span class="sewing-rating">

#div class="form-field option--size"