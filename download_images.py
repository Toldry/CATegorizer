import os
import pathlib
import urllib.request
import re
import pandas as pd


def download_images():
    cwd = os.getcwd()
    print(cwd)

    images_path = pathlib.Path(cwd + '/images')
    images_path.mkdir(parents=True, exist_ok=True)

    FILTERED_SUBMISSIONS_FILE_PATH ='filtered_submissions.csv'
    df = pd.read_csv(FILTERED_SUBMISSIONS_FILE_PATH)
    df = df.set_index('id')
    subreddits = ['blackcats', 'SphynxCats']
    subreddits = df['subreddit_name'].unique().tolist()


    image_suffixes = ['png', 'jpg', 'jpeg']
    image_rx = re.compile('.*\.(' + '|'.join([f'{str}' for str in image_suffixes]) + ')$')

    for sub in subreddits:
        sub_path = pathlib.Path(str(images_path) + '/' + sub)
        sub_path.mkdir(parents=True, exist_ok=True)
        submissions_in_sub = df[df['subreddit_name'].str.lower() == sub.lower()]
        for index, row in submissions_in_sub.iterrows():
            url = row['url']
            id = index
            suffix = image_rx.match(url).groups()[0]
            image_path = str(sub_path) +'/' + id + '.' + suffix

            if os.path.isfile(image_path):
                continue

            try:
                urllib.request.urlretrieve(url, image_path)
            except Exception as e:
                print(f'WARNING: could not download submission {id}. URL: {url}')
                print(f'Exception: {e}')


def main():
    download_images()

if __name__ == '__main__':
    main()