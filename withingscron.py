from withings import WithingsAuth, WithingsApi, WithingsCredentials
from settings import settings
from pymongo import MongoClient
import requests

client = MongoClient('localhost', 27017)
db = client.withings

creds = WithingsCredentials(
			settings['withings_access_token'], settings['withings_access_token_secret'],
			settings['withings_consumer_key'],settings['withings_consumer_secret'],
			settings['withings_user_id'])

client = WithingsApi(creds)
measures = client.get_measures(limit=5)

def main():
	for measure in measures:
		data = measure.data
		past_measures = list(db.measures.find({'date': data['date']}))
		if len(past_measures) == 0:
			db.measures.insert(data)

	return requests.post(
		settings['mailgun_post_url'],
		auth=("api", settings['mailgun_api_key']),
		data={"from": "Pete <pdarche@gmail.com>",
			"to": ["pdarche@gmail.com"],
			"subject": "Withings cron job complete",
			"text": "Withings cron job complete"})


if __name__ == '__main__':
	main()

