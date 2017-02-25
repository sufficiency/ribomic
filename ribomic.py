from __future__ import unicode_literals
import datetime 
import time
import re
import praw
import logging

import ConfigParser, os
import logging
import argparse
import traceback
#from read_comment import *

from comment_maker import *

# list of translators. They must be in the correct order
features = [BoardComment, LoLEsportsComment] 

if __name__ == "__main__":
    
    # read arguments
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",  '--config', help='config file name', default = "config.cfg")
    args = parser.parse_args()
    
    print "RIBOMIC is starting. Reading configuration from " + args.config
    
    # read the config file.
    
    
    
    config = ConfigParser.ConfigParser()
    config.readfp(open(args.config))
    
    if config.get("setting", "test") == "True":
        test_flag = True
    elif config.get("setting", "test") == "False":
        test_flag = False
    else:
        raise "Bad value for setting>test"
    
    apikey = config.get("riotapi", "key")
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s  %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='ribomic.log')
    
    logging.getLogger().addHandler(logging.StreamHandler())
    
    first_run = True
        
    while True:
        # log in
        try:
            reddit = praw.Reddit(client_id=config.get("reddit", "client_id"),
                     client_secret=config.get("reddit", "client_secret"),
                     password=config.get("reddit", "password"),
                     user_agent='Riot Board Message In Comment (RIBOMIC) Bot by /u/sufficiency',
                     username= config.get("reddit", "user"))
        except Exception as e:
            raise e
            logging.error("Having trouble logging onto reddit... is reddit down? Sleep for 60 seconds")
            time.sleep(60)
            continue # start anew
        
        try:
            # loops for getting comments
            i = 0
            worked_submissions = []
            while True:
                
                # if we are testing, we will only be getting submissions from /r/sufficiencybottest
                if test_flag:
                    submissions = reddit.subreddit('sufficiencybottest').new(limit=5)
                else:
                    #submissions = reddit.subreddit('all').get_domain_listing("leagueoflegends.com", "new", limit = 5)
                    submissions1 = reddit.domain('leagueoflegends.com').new(limit=5)
                    submissions2 = reddit.domain('lolesports.com').new(limit=5)
                    submissions = [x for x in submissions1] + [x for x in submissions2]
                
                # if we are running this for the first time, we will mark all submissions with ANY replies as worked.
                # if we are in testing mode, we will always resubmit
                if first_run and (not test_flag):
                    for s in submissions:
                        worked_submissions.append(s.id)
                    first_run = False
                    logging.info("First run. Adding " + str(worked_submissions) + " as worked submissions.")
                else:
                    for s in submissions:
                        if (not (s.id in worked_submissions)) and (time.time() - s.created_utc) / 60 / 60 <= 24:
                            for f in features:
                                translator = f(s.url, apikey)
                                if not translator.verify_url():
                                    #print translator.verify_url(), s.url
                                    continue
                                logging.info("RIBOMIC: found URL " + s.url + " to work with. Accept to translate...")
                                worked_submissions.append(s.id)
                                b = translator.create_comment()
                                if translator.error is None:
                                    logging.info("Translation success! Making replies...")
                                    #print b, translator.verify_url(), translator.error
                                    if (len(b) <= 10000):
                                        s.reply(b)
                                    else:
                                        messages = Comment.separate_message(b)
                                        logging.info("The reply is very long. Breaking into " + str(len(messages)) + " parts.")
                                        counter = 0
                                        if isinstance(messages, list):
                                            last_comment = s.reply(messages[0])
                                            for counter in range(1, len(messages)):
                                                if len(messages[counter]) == 1:
                                                    break
                                                last_comment = last_comment.reply(messages[counter])
                                                if counter >= 7:
                                                    logging.info("This reply has more than " + str(counter) + " parts. We will stop now fully knowing we are truncating the original post.")
                                                    break
                                    logging.info("Reply completed without any errors.")
                                else:
                                    logging.info("Translation failure! The error is: ")
                                    logging.info(translator.error)
                                break # we got the comment, let's exit

                    
                time.sleep(20)
                i = i + 1
                if i >= 6:
                    logging.info("Heartbeat log.")
                    i = 1
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error("Error retreiving comments. Sleep for 60 seconds, log in again, and try again.")
            time.sleep(60)
            continue
