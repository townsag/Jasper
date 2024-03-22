import scrapy

from bs4 import BeautifulSoup


class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains =[
        "jax.readthedocs.io"
    ]
    start_urls = [
        "https://jax.readthedocs.io/en/latest/user_guides.html",
    ]
    custom_settings = {
        "AUTOTHROTTLE_ENABLED":True
    }

    def parse(self, response):
        for article in response.css("article"):
            yield {
                # I think chunking should happen in the pipeline class etc
                "chunks":article.get(),
                "source":response.url
            }

        for next_page in response.css("a::attr(href)").getall():
            yield response.follow(next_page, callback=self.parse)