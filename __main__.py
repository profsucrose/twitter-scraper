from dotenv import load_dotenv
load_dotenv()

import tweepy
import re
import json
import os
import datetime
import time

# datetime
epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

auth = tweepy.OAuthHandler(
	os.getenv('CONSUMER_KEY'), # consumer_key
	os.getenv('CONSUMER_SECRET') # consumer secret
)

auth.set_access_token(
	os.getenv('ACCESS_TOKEN'), # access_token 
	os.getenv('ACCESS_TOKEN_SECRET') #access_token_secret
)

api = tweepy.API(auth)

FETCH_CYCLES = 15

min_time = datetime.datetime(2019, 12, 1) # Approximate discovery time of COVID-19
min_time_millis = unix_time_millis(min_time)

influencer_handles = open('influencers.txt', 'r')
for handle in influencer_handles:
	handle = handle.strip()
	if os.path.exists(f'tweet_timelines/{handle}.json'):
		print(f'Tweet data for {handle} is already written, skipping')
		continue

	last_tweet_id = None	
	tweet_data = []

	# 20 tweet limit max per cycle
	while True:
		try:
			if last_tweet_id is None:
				tweets = api.user_timeline(screen_name=handle[1:], tweet_mode="extended", count=20)
			else:
				tweets = api.user_timeline(screen_name=handle[1:], tweet_mode="extended", count=20, max_id=last_tweet_id)

			for tweet in tweets:
				created_at = tweet.created_at
				print(created_at)
				text = tweet.full_text.split("https://t.co")[0].strip()
				compiled_tweet = {
					"text": text,
					"created_at": str(tweet.created_at)
				}
				tweet_data.append(compiled_tweet)
		except tweepy.RateLimitError:
			# Circumvent API limits
			time.sleep(60 * 15)
			continue
		except tweepy.TweepError:
			continue

		if (unix_time_millis(tweets[-1].created_at) < min_time_millis
		or last_tweet_id == tweets[-1].id):
			break
		last_tweet_id = tweets[-1].id
		
	f = open(f'tweet_timelines/{handle}.json', 'w')
	f.write(json.dumps(tweet_data, indent=4))
	f.close()
	print(f'Wrote tweets for {handle}')
