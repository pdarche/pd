import fitbit
import moves
import json
import datetime
from settings import settings
from pymongo import MongoClient
import requests

client = MongoClient('localhost', 27017)
db = client.fitbit


def fetch_fitbit(f, token, url):
    response = f.ApiCall(token, apiCall=url)
    return json.loads(response)


def main():
	f = fitbit.FitBit()
	token = 'oauth_token_secret=%s&oauth_token=%s' % (settings['fitbit_access_secret'], settings['fitbit_access_key'])
	today = datetime.datetime.now().strftime('%Y-%m-%d')
	sleep = fetch_fitbit(f, token, '/1/user/-/sleep/date/%s.json' % today)
	activity = fetch_fitbit(f, token, '/1/user/-/activities/date/%s.json' % today)
	nutrition = fetch_fitbit(f, token, '/1/user/-/foods/log/date/%s.json' % today)

	return requests.post(
		settings['mailgun_post_url'],
		auth=("api", settings['mailgun_api_key']),
		data={"from": "Pete <pdarche@gmail.com>",
			"to": ["pdarche@gmail.com"],
			"subject": "Fitbit cron job complete",
			"text": "Fitbit cron job complete"})	


if __name__ == '__main__':
	main()