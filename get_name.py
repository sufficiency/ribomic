import HTMLParser
import traceback
import json, urllib2
import re

def get_champion_name(apikey, id):
    try:
        url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/" + str(id) + "?api_key=" + apikey
        response = urllib2.urlopen(url, timeout = 5)
        content = json.loads(response.read())
        return "{{champion:'" + content['name'] + "'}}" 
    except:
        return None



def get_item_name(apikey, id):
    try:
        url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/item/" + str(id) + "?itemData=from&api_key=" + apikey
        response = urllib2.urlopen(url, timeout = 5)
        content = json.loads(response.read())
        
        # we need to hack it for enchantment names. Really annoying!
        # First check if the name of the item has the word "enchantment".
        
        name = content['name']
        
        if re.match(r"^Enchantment:", name) is None:
            return "{{item:'" + name + "'}}" 
        else:
            source_item = content['from'][0]
            #print "source_item" , source_item
            source_item_name = json.loads(urllib2.urlopen("https://global.api.pvp.net/api/lol/static-data/na/v1.2/item/" + str(source_item) + "?itemData=from&api_key=" + apikey, timeout = 5).read())['name']
            #print "source_item_name", source_item_name
            return "{{item:'" + source_item_name + " - " + name + "'}}" 
    except:
        return None
    
    
def get_summoner_name(apikey, id):
    try:
        url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/summoner-spell/" + str(id) + "?api_key=" + apikey
        response = urllib2.urlopen(url, timeout = 5)
        content = json.loads(response.read())
        return "{{summoner:'" + content['name'] + "'}}" 
    except:
        return None
    
def get_name(str, apikey):
    
    try:
        patterns = {r"{{champion:([0-9]+)}}":get_champion_name, r"{{summoner:([0-9]+)}}":get_summoner_name, r"{{item:([0-9]+)}}":get_item_name}
        for p in patterns:
            match = re.match(p, str)
            if match is not None:
                result = patterns[p](apikey, match.group(1))
                if result is None:
                    return str # return as is if things go wrong
                else:
                    return result
        
        # no matches are found, return as is
        return str
    except:
        # if something goes wrong, just return what we got before.
        return str

def multiple_replace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text