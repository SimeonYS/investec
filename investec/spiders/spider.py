import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IinvestecItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IinvestecSpider(scrapy.Spider):
	name = 'investec'
	start_urls = ['https://www.investec.com/en_au/welcome-to-investec/press.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="col-12 col-sm-6 col-lg-3 sub-nav__link"]/secondary-cta/@ng-href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="articles-header__date"]/p/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('(//div[@class="detailed-information__copy-holder rich-text__list-items"])[position()<last()]//text()').getall()
		if not content:
			content = response.xpath('//div[@id="content"]/div[last()]/div[position() mod 2 = 1]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=IinvestecItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
