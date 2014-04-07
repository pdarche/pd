from settings import settings
import oauth2
import time
import urllib
import urllib2
import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.openpaths

ACCESS = settings['openpaths_access']
SECRET = settings['openpaths_secret']
URL = "https://openpaths.cc/api/1" 

def build_auth_header(url, method):
    params = {                                            
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
    }
    consumer = oauth2.Consumer(key=ACCESS, secret=SECRET)
    params['oauth_consumer_key'] = consumer.key 
    request = oauth2.Request(method=method, url=url, parameters=params)    
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    request.sign_request(signature_method, consumer, None)
    return request.to_header()

def main():
    last_measure = list(db.locations.find())
    now = int(time.time())
    if len(last_measure) == 0:
        start = now - 24*60*60
    else:
        times = sorted(map(lambda m: m['t'], last_measure))
        start = times[-1] + 1
        print "found some stuff starting at %s" % start

    params = {'start_time': start, 'end_time': now}    # get the last 24 hours
    query = "%s?%s" % (URL, urllib.urlencode(params))

    try:
        request = urllib2.Request(query)
        request.headers = build_auth_header(URL, 'GET')
        connection = urllib2.urlopen(request)
        data = json.loads(''.join(connection.readlines()))
        if len(data) > 0:
            db.locations.insert(data)

        return requests.post(
            settings['mailgun_post_url'],
            auth=("api", settings['mailgun_api_key']),
            data={"from": "Pete <pdarche@gmail.com>",
                "to": ["pdarche@gmail.com"],
                "subject": "Openpaths cron job complete",
                "text": "Openpaths cron job complete"})

    except urllib2.HTTPError as e:
        print(e.read())


if __name__ == '__main__':
    main()