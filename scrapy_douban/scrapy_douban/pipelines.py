# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import traceback


class ScrapyDoubanPipeline(object):
    def open_spider(self, spider):
        self.db = pymysql.connect(host='localhost', port=3306, user='testuser', passwd='test123', db='crawler',
                                  charset='utf8')
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        title = list(item.keys())[0]
        release = item[title]['Release date']
        tag = item[title]['Tag']
        rating = item[title]['Rating']
        year = item[title]['Year']
        des = item[title]['Description']
        runtime = item[title]['Runtime']
        imdb = item[title]['IMDB']
        director = item[title]['Director']
        genre = item[title]['Genre']
        actor = item[title]['Main actors(actresses)']
        ### Need to be changed
        # release = self.emerge_str(release)
        # director = self.emerge_str(director)
        # Query Part
        id_query = 'SELECT count(*) FROM douban_movie'
        search_query = 'SELECT Title FROM douban_movie WHERE Title=' + "'" + title + "'"
        # Execute search query first to check if the movie is already in the db
        self.cursor.execute(search_query)
        data = self.cursor.fetchone()
        # Check the size of the current table
        self.cursor.execute(id_query)
        num = self.cursor.fetchone()[0] + 1
        # Add current movie to the db if it is not there
        if data is None:
            char_query = 'alter table douban_movie charset=utf8'
            self.execute(char_query)
            adding_query = 'INSERT INTO douban_movie (id,Title,Year,Description,IMDB) ' \
                           'VALUES ' \
                           '(' + str(num) + ",'" + str(title) + "'," + year + ",'" + str(des) + "'" + ",'" + str(imdb)\
                           + "'" + ')'
            self.execute(adding_query)
            # Update the Rating table
            rating_adding_query = 'INSERT INTO douban_rating  ' \
                                  'VALUES ' \
                                  '(' + str(num) + ",'" + str(title) + "'," + rating[0] + "," + rating[1]['five'] +\
                                  "," + rating[1]['four'] + "," + rating[1]['three'] + "," + rating[1]['two'] + \
                                  "," + rating[1]['one'] + ')'
            self.execute(rating_adding_query)
            # Update the Other tables
            self.update_flexible_table('douban_tag', tag, num, title)
            self.update_flexible_table('douban_star', actor, num, title)
            self.update_flexible_table('douban_director', director, num, title)
            self.update_flexible_table('douban_genre', genre, num, title)

    def execute(self, query):
        try:
            # Execute the sql
            self.cursor.execute(query)
            # Post the data to the database
            self.db.commit()
        except:
            # Rollback if any error occurs
            self.db.rollback()
            traceback.print_exc()

    def check_col(self, table):
        '''
        :param table: the table name
        :return: the number of columns of current table
        '''
        check_query = 'SELECT count(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = ' + "'" + table + "'"
        self.cursor.execute(check_query)
        num_col = self.cursor.fetchone()[0] - 2
        return num_col

    def alter_table(self, table, num_tag):
        '''
        :param table: the table name
        :param num_tag: total number of tags that current movie has
        :return: None
        Add all the tags into the table, if the number of tags is larger that the number of column, add as many column 
        as needed
        '''
        initial_num = self.check_col(table)
        if num_tag > initial_num:
            for times in range(num_tag - initial_num):
                updated_num = self.check_col(table)
                alter_query = 'ALTER TABLE ' + table + ' ADD ' + table[7:] + str(updated_num+1) + ' VARCHAR(100) NULL'
                self.execute(alter_query)

    def update_flexible_table(self, table_name, l, num, title):
        self.alter_table(table_name, len(l))
        adding_query = 'INSERT INTO ' + table_name + ' VALUES (' + str(num) + ",'" + str(title) + "'"
        for times in range(len(l)):
            adding_query += ",'" + l[times] + "'"
        cur_table_col = self.check_col(table_name)
        if len(l) < cur_table_col:
            for times in range(cur_table_col - len(l)):
                adding_query += ',NULL'
        adding_query += ')'
        self.execute(adding_query)
