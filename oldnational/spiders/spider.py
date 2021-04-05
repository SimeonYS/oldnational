import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OoldnationalItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class OoldnationalSpider(scrapy.Spider):
	name = 'oldnational'
	start_urls = ['https://www.oldnational.com/about/news-center']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//span[@class="news-date"]/text()').get().split('Posted: ')[1]
		title = response.xpath('(//h1)[2]/span/text()').get()
		content = response.xpath('//div[@class="news-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content)).replace('###','')

		item = ItemLoader(item=OoldnationalItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
