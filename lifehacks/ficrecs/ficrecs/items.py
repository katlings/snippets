# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AO3Bookmark(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    fandom = scrapy.Field()
    kudos = scrapy.Field()
    hits = scrapy.Field()
    bookmarks = scrapy.Field()
