from __future__ import unicode_literals
import datetime
import dateutil.parser
import traceback
import re
import logging
import get_name
from abc import ABCMeta, abstractmethod
import HTMLParser
import traceback
import json, urllib2
import urlparse
import logging
import time
import datetime
import dateutil.parser
import urlparse
import get_name
from selenium import webdriver 
from bs4 import BeautifulSoup
import time
import html2text


#from twisted.web import static

class Comment(object):
    author = ''
    body = ''
    date = ''
    url = ''
    error = None
    apikey = None
    def __init__(self, url, apikey = None):
        self.url = url
    
    @abstractmethod
    def verify_url(self):
        return False
        
    @abstractmethod
    def read_url(self):
        self.read_url_post_processing()
        pass
    
    @abstractmethod
    def read_url_post_processing(self):
        pass
    
    def process_header(self):
        text = ""
        text = text + "[" + self.author + " wrote on " + self.date + "](" + self.url + ")" 
        text = text + ":"+ '\n\n'
        return text
    
    def process_body(self):
        try:
            body = self.body.decode('utf-8').replace('\n', "  " + '\n'+">") # re.sub("\[\{quoted\}\]\([^)]+\)", "", result['main']['body'].replace('\n', "  " + '\n'+">"))  #.decode('utf-8')
        except:
            body = self.body.replace('\n', "  " + '\n'+">")
        # for quotes within the message, extract out the name and timestamp, if they are available
        # body = re.sub(r"(\[\{quoted\}\])\(name=([^,]{1,16}).*timestamp=(.{1,10}).*\)", r"[\2 wrote on \3]:", body)
                # replace {{}} structure with what we need
        
#         icon_replace = re.findall("{{.*?}}", body)
#         icon_replace = list(set(icon_replace))
#         if icon_replace is not None:
#             logging.info("We have located some {{}} to replace. Let's investigate...")
#             icon_dict = {key: get_name.get_name(key, apikey) for key in icon_replace}
#             logging.info("Investigation complete. The dictionary is: " + str(icon_dict))
#             body = get_name.multiple_replace(body, icon_dict)
        return ">" + body
    
    def process_tail(self):
        return (" This comment was created by a bot. Find out more [here](https://www.reddit.com/r/sufficiencybot/comments/3bnxfc/riotsboardmessageincommentbot/)." ).replace(" ", " ^") + "  " + '\n'
    
    def create_comment(self):
        self.read_url()
        if self.error is None:
            return self.process_header() + self.process_body() + '\n\n' + "*****" + '\n\n' +self.process_tail()
        else:
            return None
    
    @staticmethod
    def separate_message(str):
        assert str is not None, "separate_message(): input string is None."
        if len(str) <= 9999:
            return(str)
        else:
            a = []
            old_str = str
            while len(old_str) >= 9900:
                index = old_str[:9900].rindex( '\n')
                a.append(old_str[:index]  + '\n' + "... continued on next comment ...")
                old_str = old_str[index:]
            a.append(old_str)
            return a


# TODO: refactor this class using beautifulsoup.
class BoardComment(Comment):
    
    
    isreply = None
    link = None
    title = None
    apikey = None
    
    def __init__(self, url, apikey = None):
        self.apikey = apikey
        super(BoardComment,self).__init__(url)
    
    def verify_url(self):
        condition = re.compile('boards\.[a-z]+\.leagueoflegends\.com')
        return condition.search(self.url) is not None

    def process_header(self):

        text = ""
        text = text + "[" + self.author + " wrote on " + dateutil.parser.parse(self.date).strftime('%Y-%m-%d') + " UTC](" + self.url + ")" 
        if (self.link is not None):
            text = text + " with [link](" + self.link + "):"+ '\n\n'
        else:
            text = text + ":"+ '\n\n'
        
        if (not self.isreply):
            text = text + " **" + self.title + "**" + '\n\n'
        return text


    def process_body(self):
        body = re.sub(r"(\[\{quoted\}\])\(name=([^,]{1,16}).*timestamp=(.{1,10}).*\)", r"[\2 wrote on \3]:", self.body)
        icon_replace = re.findall("{{.*?}}", body)
        icon_replace = list(set(icon_replace))
        if icon_replace is not None:
            logging.info("We have located some {{}} to replace. Let's investigate...")
            icon_dict = {key: get_name.get_name(key, self.apikey) for key in icon_replace}
            logging.info("Investigation complete. The dictionary is: " + str(icon_dict))
            body = get_name.multiple_replace(body, icon_dict)
        self.body = body
        return super(BoardComment, self).process_body()

    @staticmethod
    def search_JSON(j, key, value):
        def search_JSON1(j, key, value):
            if j is None:
                return None
            if isinstance(j, basestring):
                return None
            for k in j:
                if j[k] == value and k == key:
                    return j
                if isinstance(j[k], dict):
                    r = search_JSON1(j[k], key, value)
                    if r is not None:
                        return r
                if isinstance(j[k], list):
                    for i in j[k]:
                        r = search_JSON1(i, key, value)
                        if r is not None:
                            return r
        return search_JSON1(j, key, value)

    def read_url(self):
        try:
            # read from the URL
            url = self.url
            response = urllib2.urlopen(url, timeout = 5)
            html_content = response.read()
    
            parsed_url = urlparse.urlsplit(url)
            param_dict = urlparse.parse_qs(parsed_url.query)
            commentid = param_dict.get('comment')
            if commentid is not None:
                commentid = commentid[0]
            else:
                commentid = ""
    
            html_content = u"".join(unicode(html_content, 'utf-8').splitlines())
    
            JSON = re.compile("document.apolloPageBootstrap.push\(\{\s*?name:\s*?'DiscussionShowPage',\s*?data: (\{.*?\})\s*?\}\);" , re.DOTALL)
    
            
            matches = JSON.search(html_content)
            
            j = json.loads(matches.group(1))
            
        
            html_parser = HTMLParser.HTMLParser()
            if commentid != "":
                message_json = self.search_JSON(j,  'id', commentid)
#                 return {'isreply':True, 'main':{'link':None, 'body':html_parser.unescape(message_json['message']), 'author':message_json['user']['name'], 'isrioter':message_json['user']['isRioter'],
#                         'title':None, 'createdat':message_json['createdAt'], 'modifiedat':message_json['modifiedAt']},
#                         'error':""}
                self.isreply = True
                self.link = None
                self.title = None
                self.body = html_parser.unescape(message_json['message'])
                self.author = message_json['user']['name']
                self.date = message_json['createdAt']
                
            else:
#                 link = None
#                 try:
#                     link = j['discussion']['content']['sharedLink']['url']
#                 except:
#                     link = None
#                     # do nothing
#                     
#                 if 'body' in j['discussion']['content']:
#                     return {'isreply':False, 'main':{'link':link, 'body':html_parser.unescape(j['discussion']['content']['body']), 'author':j['discussion']['user']['name'], 'isrioter':j['discussion']['user']['isRioter'],
#                         'title':j['discussion']['title'], 'createdat':j['discussion']['createdAt'], 'modifiedat':j['discussion']['modifiedAt']},
#                         'error':""}
#                 else:
#                     raise

                # see if there is a link
                try:
                    self.link = j['discussion']['content']['sharedLink']['url']
                except:
                    self.link = None
                
                if 'body' in j['discussion']['content']:
                    self.isreply = False
                    self.title = j['discussion']['title']
                    self.body = html_parser.unescape(j['discussion']['content']['body'])
                    self.author = j['discussion']['user']['name']
                    self.date = j['discussion']['createdAt']
                else:
                    raise NotImplementedError # this is likely caused by a htmlbody
    
        except Exception:
            self.error = str(traceback.format_exc())
    

    def read_url_post_processing(self):
        self.body = re.sub(r"(\[\{quoted\}\])\(name=([^,]{1,16}).*timestamp=(.{1,10}).*\)", r"[\2 wrote on \3]:", self.body)
        # replace {{}} structure with what we need
        
        icon_replace = re.findall("{{.*?}}", self.body)
        icon_replace = list(set(icon_replace))
        if icon_replace is not None:
            logging.info("We have located some {{}} to replace. Let's investigate...")
            icon_dict = {key: get_name.get_name(key, apikey) for key in icon_replace}
            logging.info("Investigation complete. The dictionary is: " + str(icon_dict))
            self.body = get_name.multiple_replace(self.body, icon_dict)
            
            
class LoLEsportsComment(Comment):
    
    title = None
    
    def __init__(self, url, apikey = None):
        self.apikey = apikey
        super(LoLEsportsComment,self).__init__(url)
    
    def verify_url(self):
        condition = re.compile('lolesports\.com')
        return condition.search(self.url) is not None


    def read_url(self):
        try:
            driver = webdriver.PhantomJS()  # sudo apt-get install phantomjs
            driver.get(self.url)
        except Exception:
            self.error = str(traceback.format_exc())
            return
        time.sleep(5)
        try:
            
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            try:
                text = soup.findAll("div", { "class" : "body-content" })[0]
                date = soup.findAll("span", { "id" : "date" })[0].text
                author = soup.findAll("span", { "id" : "author" })[0].text
            except:
                raise "Did not find the correct parts from the page. Probably not an article?"
            #print soup.title.string
            driver.close()
            self.body = html2text.html2text(text.decode()).encode('utf-8')
            self.author = author
            self.date = date
        except Exception:
            driver.close()
            self.error = str(traceback.format_exc())
    

    def read_url_post_processing(self):
        pass # do nothing
            
