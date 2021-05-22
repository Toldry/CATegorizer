import os
import shutil
import tempfile
import re
import itertools
import csv
import praw
# import prawcore
import logging
# import numpy as np
# import pandas as pd


FILTERED_CAT_SUBS_FILENAME = 'filtered_cat_subs.csv'
SUBMISSIONS_FILENAME = 'submission.csv'

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
    #source: https://www.reddit.com/r/Catsubs/wiki/index
    cat_subreddits_path = 'cat_subreddits.csv' 
    cat_subreddits = list(itertools.chain.from_iterable(csv.reader(open(cat_subreddits_path, "r"), delimiter='\n')))
    return cat_subreddits
    

def get_top_submissions_of_subreddit(subreddit_name, num_submissions=5000):
    global reddit
    return reddit.subreddit(subreddit_name).top(time_filter='all', limit=num_submissions)

def is_image_submission(submission):
    image_suffixes = ['png', 'jpg', 'jpeg']
    image_rx = re.compile('.*\.(' + '|'.join([f'{str}' for str in image_suffixes]) + ')$')
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

    with open(FILTERED_CAT_SUBS_FILENAME, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['subreddit_name', 'finished_scraping'])
        writer.writeheader()
        for subr in filtered_cat_subreddits:
            writer.writerow({'subreddit_name': subr, 'finished_scraping': False})

def read_filtered_cat_subreddits_csv():
    with open(FILTERED_CAT_SUBS_FILENAME, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        all_rows = list(csv_reader)
        return all_rows

def update_scraped(subreddit):
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False)

    fields = ['subreddit_name', 'finished_scraping']

    with open(FILTERED_CAT_SUBS_FILENAME, 'r') as csvfile, temp:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(temp, fieldnames=fields)
        for row in reader:
            if row['subreddit_name'] == subreddit:
                logging.info('updating row ', row['subreddit_name'])
                row['finished_scraping'] = True
            writer.writerow(row)

    shutil.move(temp.name, FILTERED_CAT_SUBS_FILENAME)


def create_csv_if_it_doesnt_exist(filename, fieldnames):
    if os.path.isfile(filename): 
        return
    with open(filename, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    


def create_submissions_file():
    attributes_to_save = ['id', 'url', 'permalink','score', 'title', 'total_awards_received','ups','upvote_ratio','is_original_content', 'gilded', 'num_comments', 'num_crossposts', 'num_duplicates', 'over_18']
    other_attributes = ['subreddit_name']
    fieldnames = other_attributes + attributes_to_save

    scraped_subreddits_table = read_filtered_cat_subreddits_csv()

    create_csv_if_it_doesnt_exist(SUBMISSIONS_FILENAME, fieldnames)

    with open(SUBMISSIONS_FILENAME, 'a+', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for sub_row in scraped_subreddits_table:
            subreddit_name = sub_row['subreddit_name']
            scraped = sub_row['finished_scraping'] == "True"
            if scraped:
                continue
            submissions = get_top_submissions_of_subreddit(subreddit_name)
            for s in submissions:
                if not is_image_submission(s):
                    continue
                submission_obj = {}
                submission_obj['subreddit_name'] = subreddit_name
                for attr in attributes_to_save:
                    submission_obj[attr] = str(getattr(s, attr))
                writer.writerow(submission_obj)
            update_scraped(subreddit_name)


def main():
    connect_to_reddit()
    # create_filtered_cat_subreddits_csv()
    create_submissions_file()

if __name__ == '__main__':
    main()