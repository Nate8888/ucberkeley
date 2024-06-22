from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import praw
from praw.models import MoreComments

# load_env()
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)


def fetch_reddit_posts_and_comments(subreddit='news', limit=10):
    posts = []
    
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        reddit_post = {
            'title': submission.title,
            'text': submission.selftext,
            'url': submission.url,
            'comments': []
        }
        relevant_comment_count = 0
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            if relevant_comment_count >= 5: # Limiting to 5 comments per post
                break
            if top_level_comment.body and top_level_comment.body != '[removed]':
                reddit_post['comments'].append(top_level_comment.body)
                relevant_comment_count += 1
        posts.append(reddit_post)
    return posts

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        whole_text = ''
        for entry in transcript:
            whole_text += entry['text'] + ' '
        return whole_text
    except:
        return None

posts = fetch_reddit_posts_and_comments('news', 5)
print(posts)

# for subreddit in reddit.subreddits.default(limit=None):
#     print(subreddit)
#
# video_ids = ['2koEujX9nEg', 'dQw4w9WgXcQ']
# for video_id in video_ids:
#     print(get_transcript(video_id))
#     print("--------------------------------------------------")
