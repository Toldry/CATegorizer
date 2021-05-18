import re
import itertools
import csv
import praw
import prawcore
import logging
import numpy as np
# import pandas as pd

def connect_to_reddit():
    global reddit
    # if reddit is not None:
    #     logging.info('reddit object already instantiated')
    #     return

    username = 'CATegorizer_bot'
    developername = 'orqa'
    version= '0.0.1'
    clientname = username
    useragent = f'{clientname}/{version} by /u/{developername}'
    password, app_client_id, app_client_secret = open('.credentials', 'r').read().splitlines()

    logging.info(f'Connecting to reddit via praw to instantiate connection instance. username={username}')
    reddit = praw.Reddit(client_id=app_client_id,
                        client_secret=app_client_secret,
                        user_agent=useragent,
                        username=username,
                        password=password)


def get_cat_subreddits():
    #built from https://www.reddit.com/r/Catsubs/wiki/index
    cat_subreddits_path = 'cat_subreddits.csv' 
    cat_subreddits = list(itertools.chain.from_iterable(csv.reader(open(cat_subreddits_path, "r"), delimiter='\n')))
    return cat_subreddits
    

def get_top_submissions_of_subreddit(subreddit_name, num_submissions=5000):
    global reddit
    return list(reddit.subreddit(subreddit_name).top(time_filter='all', limit=num_submissions))

def is_image_submission(submission):
    image_suffixes = ['png', 'jpg', 'jpeg']
    image_rx = re.compile('|'.join([f'{str}$' for str in image_suffixes]))
    return image_rx.match(submission.url) is not None

def subreddit_filter(subreddit_name):
    global reddit
    try:
        return reddit.subreddit(subreddit_name).subscribers > 500
    except Exception as e:
        # Some subreddits are private or quarantined or do not exist, these will return an 403 HTTP response or a redirect
        print(f'sub: {subreddit_name}, error: {e}')
        return False


def create_filtered_cat_subreddits_csv():
    cat_subreddits = get_cat_subreddits()

    connect_to_reddit()
    filtered_cat_subreddits = [sub for sub in cat_subreddits if subreddit_filter(sub)]
    f = open('filtered_cat_subs.csv', 'w')
    f.write('\n'.join(filtered_cat_subreddits))

def main():
    create_filtered_cat_subreddits_csv()

if __name__ == '__main__':
    main()