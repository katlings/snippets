# -*- coding: utf-8 -*-
import scrapy
import re


class Ao3Spider(scrapy.Spider):
    tag_search_url = 'http://archiveofourown.org/tags/search?page={}&query%5Bcanonical%5D=true&query%5Bname%5D=&query%5Btype%5D=Relationship&utf8=%E2%9C%93'
    name = 'ao3'
    allowed_domains = ['archiveofourown.org']
    start_urls = [tag_search_url.format(1)]

    def parse(self, response):
        pages = response.xpath('//ol[2]/li/a/text()').extract()
        for i in range(1, int(pages[-2])+1):
            yield scrapy.Request(self.tag_search_url.format(i), callback=self.parse_page)

    def parse_page(self, response):
        # yield data from this page
        tags = response.xpath('//ol[1]/li/span')
        for tag in tags:
            pairing = tag.xpath('a/text()').extract()[0]
            count = re.match(r'.*a. .*\((\d+)\)', tag.extract()).group(1)
            yield {'count': count, 'pairing': pairing}
