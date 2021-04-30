import scrapy


class FatsecretSpiderSpider(scrapy.Spider):
    name = 'fatsecret_spider'
    allowed_domains = ['fatsecret.ru']
    start_urls = ['https://www.fatsecret.ru/Default.aspx?pa=rs']


    def parse(self, response):
        for href in response.css(".borderBottom a::attr(href)"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_recipe_contents)

        NEXT_PAGE_SELECTOR = '.strong + a::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

        # for recipe_name in response.css(".prominent::text").extract():
        #     preprocessed_recipe_name = recipe_name[9:len(recipe_name)-8].replace(' ', '-')
        #     url = response.urljoin(f"рецепты/{preprocessed_recipe_name}/Default.aspx")
        #     yield scrapy.Request(url, callback=self.parse_recipe_contents)

    def parse_recipe_contents(self, response):
        if response.css(".fn::text").extract_first():
            scrapped_info = {
                'recipe_name': response.css(".fn::text").extract_first(),
                'measured_ingredients': response.css('.ingredient a::text').extract(),
                'number_of_servings': response.css(".yield::text").extract_first()[0],
                'cooking_time': response.css(".cookTime::text").extract_first(),
                'nutrients': response.css(".nutrient.black.right.tRight::text").extract(),
                'kind_of_dish': response.css('.tag::text').extract_first(),
                'rating': response.css("div#rating img::attr(src)").extract_first(),
                'img_url': response.css('.imgFrame img::attr(src)').extract_first(),
                'reviews': []
            }

            reviews = response.css(".listrow div::text").extract()
            if reviews:
                for i in range(0, len(reviews), 5):
                     scrapped_info['reviews'].append(reviews[i][11:len(reviews[i])-11])

            # if response.css(".resultMetrics a::text").extract_first() == 'Следующая':
            #     next_review_page = response.css(".resultMetrics a::attr(href)").extract_first()
            #     yield scrapy.Request(response.urljoin(next_review_page), callback=self.parse_remaining_reviews(dictionary=scrapped_info))

            yield scrapped_info

    def parse_remaining_reviews(self, response, dictionary):
        reviews = response.css(".listrow div::text").extract()
        if reviews:
            for i in range(0, len(reviews), 5):
                dictionary['reviews'].append(reviews[i][11:len(reviews[i]) - 11])
        yield dictionary
