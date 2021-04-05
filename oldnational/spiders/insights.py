import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OoldnationalItem
from itemloaders.processors import TakeFirst
import json
from scrapy import Selector

pattern = r'(\xa0)?'
base = 'https://www.oldnational.com/api/blog/posts?page={}&pageSize=12&taxonFilters=9fb8a287-4d8c-48a4-b870-4dbc905c533d%2C0b10ead8-0bae-4b51-b0f9-27e42a7364ec%2C997eff78-aa4d-6e8c-82c6-ff000090c1be&orTaxons=&allFilters=9fb8a287-4d8c-48a4-b870-4dbc905c533d%2C0b10ead8-0bae-4b51-b0f9-27e42a7364ec%2C997eff78-aa4d-6e8c-82c6-ff000090c1be%2Ca09e0079-aa4d-6e8c-82c6-ff000090c1be%2C997eff78-aa4d-6e8c-82c6-ff000090c1be%2Cb89e0079-aa4d-6e8c-82c6-ff000090c1be%2C997eff78-aa4d-6e8c-82c6-ff000090c1be%2C9f7eff78-aa4d-6e8c-82c6-ff000090c1be%2Ca17eff78-aa4d-6e8c-82c6-ff000090c1be&defaultFilter=Categories%3A9fb8a287-4d8c-48a4-b870-4dbc905c533d%2CTopics%3A0b10ead8-0bae-4b51-b0f9-27e42a7364ec%2CContent+Type%3A997eff78-aa4d-6e8c-82c6-ff000090c1be'
class InsightsSpider(scrapy.Spider):
    name = 'insights'
    page = 1
    start_urls = [base.format(page)]
    ITEM_PIPELINES = {
        'insights.pipelines.OoldnationalPipeline': 300,

    }

    def parse(self, response):
        data = json.loads(response.text)
        container = Selector(text=data['Html']).xpath('//article')
        for article in container:
            link = 'https://www.oldnational.com/ONB/insights-detail'+ article.xpath('.//a/@href').get().replace('#BaseUrl#','')
            title = article.xpath('.//a/@title').get()
            yield response.follow(link, self.parse_post, cb_kwargs=dict(title=title))

        if data['HasMore']:
            self.page += 1
            yield response.follow(base.format(self.page), self.parse)

    def parse_post(self, response, title):
        date = response.xpath('//div[@class="row"]//script[@type="application/ld+json"]/text()').get()
        date = json.loads(date)
        date = date['datePublished'].split('T')[0]
        content = response.xpath('//div[@class="content-body"]//text()[not (ancestor::span[@class="author-info"] or ancestor::div[@class="CallToAction"] or ancestor::div[@class="copyright"] or ancestor::div[@class="content-disclosure"])]').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=OoldnationalItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()