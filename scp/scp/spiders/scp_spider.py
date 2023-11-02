import scrapy
from scrapy.shell import inspect_response
from scrapy.crawler import CrawlerProcess
from typing import NamedTuple
from scrapy.http import Request
import json
import os




class ScpSpider(scrapy.Spider):
    name = "scp"
    start_urls = ['http://scpfoundation.net/scp-series', 'http://scpfoundation.net/scp-series-2',
                  'http://scpfoundation.net/scp-series-3', 'http://scpfoundation.net/scp-series-4',
                  'http://scpfoundation.net/scp-series-5', 'http://scpfoundation.net/scp-series-6',
                  'http://scpfoundation.net/scp-series-7', 'http://scpfoundation.net/scp-list-ru']

    def parse(self, response, **kwargs):
        if response.url in self.start_urls:
            yield from self.parse_sitemap(response)
        else:
            yield self.parse_creature(response)


    def parse_sitemap(self, response):
        url_all = response.css("div#page-content a::attr(href)").extract()
        urls = self.check_url(url_all)
        for i in urls:
            yield Request(i)

    def check_url(self, url_all):
        urls = []
        for i in url_all:
            if i.startswith("/scp-"):
                urls.append('http://scpfoundation.net' + i)
        return urls

    def parse_creature(self, response):
        paragraphs = response.css("div#page-content p")
        page_title = " ".join(response.css("div#page-title::text").getall())
        object_number = self.find_paragraph(paragraphs, "Объект №:")
        object_class = self.find_paragraph(paragraphs, "Класс объекта")
        object_condition = self.find_paragraph(paragraphs, "Особые условия содержания:")
        indexes = list(range(len(paragraphs)))
        if object_number.index >= 0:
            indexes.remove(object_number.index)
        if object_class.index >= 0:
            indexes.remove(object_class.index)
        if object_condition.index >= 0:
            indexes.remove(object_condition.index)
        object_info = []
        for i in indexes:
            object_info.extend(paragraphs[i].css("::text").getall())
        object_info_text = " ".join(object_info)
        dict = {"object_number_text":object_number.text, "object_class_text":object_class.text,
                "object_condition_text":object_condition.text, "object_info_text":object_info_text,
                "url":response.url, "title":page_title}
        return dict

    def find_paragraph(self, paragraphs, paragraph_name):
        for i, p in enumerate(paragraphs):
            names = p.css("strong::text").getall()
            if any([paragraph_name in n for n in names]):
                text = " ".join(p.css("::text").getall())
                return Paragraph(i, p, text)
        return Paragraph(-1, None, "")


class Paragraph(NamedTuple):
    index: int
    paragpaph: object
    text: str


if __name__ == "__main__":
    if os.path.exists(r"C:\Users\UselessAqua\PycharmProjects\another_s_craper\scp\scp\spiders\items.json"):
        os.remove(r"C:\Users\UselessAqua\PycharmProjects\another_s_craper\scp\scp\spiders\items.json")
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
    })

    process.crawl(ScpSpider)
    process.start()
