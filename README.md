# Scrapy douban

This project is a movie crawler based on scrapy framework, which retrieving details about the movie as well as the rating percentage from [Douban](https://movie.douban.com)

## Getting Started

### Prerequisites

Before running this crawler, you need to install scrapy framework using (if pip is installed)

```
pip install Scrapy
```

Also, install MySQL for the purpose of storing all the data crawled from the website.

One more thing before running is that you need to change line 25 and 26 in movie.py file with your own email and password.

### Running

Running the framework will require the command prompt under the project directory

```
scrapy crawl movie
```

## Built With

* [Scrapy](https://github.com/scrapy/scrapy) - The crawler framework used
