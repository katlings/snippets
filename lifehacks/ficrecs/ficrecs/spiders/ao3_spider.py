import scrapy

from ficrecs.items import AO3Bookmark


class AO3Spider(scrapy.Spider):
    name = 'ao3'
    allowed_domains = ['archiveofourown.org']

    def start_requests(self):
        urls = [
            'http://archiveofourown.org/users/hartknyx/bookmarks'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # response is a TextResponse that holds page content
        # do shit
        # and probably store it in a db
        # usually parses, extracts data, finds new URLs, and creates new Requests
        bookmarks = response.xpath('//li[contains(@id,"bookmark")]')
        for b in bookmarks:
            bookmark = AO3Bookmark()

            basic_info = b.xpath('div[1]/h4')
            bookmark['name'] = basic_info.xpath('a[1]/text()').extract()
            bookmark['link'] = basic_info.xpath('a[1]/@href').extract()
            bookmark['author'] = basic_info.xpath('a[2]/@href').extract()  # TODO: handle pseuds

            bookmark['fandom'] = b.xpath('div[1]/h5/a[1]/text()').extract()  # TODO: handle multiple fandoms

            bookmark['kudos'] = b.xpath('dl/dd[@class="kudos"]/a/text()').extract()
            bookmark['hits'] = b.xpath('dl/dd[@class="hits"]/text()').extract()
            bookmark['bookmarks'] = b.xpath('dl/dd[@class="bookmarks"]/a/text()').extract()

            yield bookmark
