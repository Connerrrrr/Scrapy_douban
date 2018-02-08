# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
import urllib.request
import re
import os


class MovieSpider(scrapy.Spider):
    name = 'movie'
    start_urls = ['https://accounts.douban.com/login']

    def parse(self, response):
        captcha = response.xpath("//img[@id='captcha_image']/@src").extract()
        if len(captcha) > 0:
            print("Need Captcha")
            # Get the path of the current .py file
            localpath = os.getcwd()
            path = localpath + "\captcha.jpg"
            urllib.request.urlretrieve(captcha[0], filename=path)
            print("Type the captcha")
            captcha_value = input()

            data = {
                "form_email": "****",
                "form_password": "****",
                "captcha-solution": str(captcha_value),
                "redir": "https://movie.douban.com/top250?start=0&filter="
            }

        else:
            print("No need for captcha")

            data = {
                "form_email": "*******",
                "form_password": "*******",
                "redir": "https://movie.douban.com/top250?start=0&filter="
            }
        print("Logging...")
        return FormRequest.from_response(response, formdata=data, callback=self.parse_top,)

    def parse_top(self, response):
        for href in response.css('a::attr(href)').extract():
            try:
                iden = re.findall(r"\d{7}", href)[0]
                url = 'https://movie.douban.com/subject/' + iden + '/'
                yield scrapy.Request(url, callback=self.parse_movie)
            except:
                continue

    def parse_movie(self, response):
        info_dict = {}
        sub_dict = {}
        # use css and xpath selector
        name = response.xpath('//head/title/text()').extract()[0].split('(')[0].strip()
        basic_info = response.css('h1')
        year = basic_info.css('.year::text').extract()[0][1:-1]
        sub_dict['Year'] = year
        # extract the director and update the sub_dict
        director = response.xpath('//a[@rel="v:directedBy"]/text()').extract()
        sub_dict['Director'] = director
        # extract the actor list and update the sub_dict
        actor = response.xpath('//span[@class="attrs"]//a[@rel="v:starring"]/text()').extract()
        sub_dict['Main actors(actresses)'] = actor
        # each tag has its own LIST of value
        key_list = ['Genre', 'Release date', 'Runtime', 'IMDB']
        # info extracted by xpath will temporarily stored in list, except for length and imdb
        genre = response.xpath('//span[@property="v:genre"]/text()').extract()
        release_date = response.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
        runtime = response.xpath('//span[@property="v:runtime"]/text()').extract()[0][:-2]
        imdb = response.xpath('//div[@id="info"]//a[@rel="nofollow"]/text()').extract()[-1]
        val_list = [genre, release_date, runtime, imdb]
        # update all other available info to sub_dict
        for num in range(len(key_list)):
            sub_dict[key_list[num]] = val_list[num]
        # Rating Part
        # Using list to store rating such as [rating, {population for each rate}]
        rating_list = response.xpath('//strong[@property="v:average"]/text()').extract()
        rating_dict = dict()
        rating_key = ['five', 'four', 'three', 'two', 'one']
        rating_val = response.xpath('//span[@class="rating_per"]/text()').extract()
        for i in range(len(rating_key)):
            rating_dict[rating_key[i]] = rating_val[i][:-1]
        rating_list.append(rating_dict)
        sub_dict['Rating'] = rating_list
        # Description Part
        description = response.xpath('//span[@class="all hidden"]/text()').extract()
        if not description:
            description = response.xpath('//span[@property="v:summary"]/text()').extract()
        full_description = ''
        for des in description:
            full_description += des.strip()
        sub_dict['Description'] = full_description
        # Tag part, use a list to store all the tags
        tag_list = response.xpath('//div[@class="tags-body"]/a/text()').extract()
        sub_dict['Tag'] = tag_list
        # generate the info_dict
        info_dict[name] = sub_dict
        # keep searching similar movies
        movie_list = response.xpath('//div[@class="recommendations-bd"]/dl[@class=""]/dd/a/@href').extract()
        # file testing
        file = open('test.txt', 'w')
        try:
            line = str(name)
            for key in sub_dict:
                line += '\n' + key + '     :     ' + str(sub_dict[key])
            file.write(line)
        except:
            pass
        file.close()
        yield info_dict
        # use Request to request for similar movies' site
        for href in movie_list:
            try:
                iden = re.findall(r"\d{7}", href)[0]
                url = 'https://movie.douban.com/subject/' + iden + '/'
                yield scrapy.Request(url, callback=self.parse_movie)
            except:
                continue
