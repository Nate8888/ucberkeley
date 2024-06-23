from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import praw
from praw.models import MoreComments
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.you import YouRetriever
import datetime

# load_env()
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)

retriever = YouRetriever()
curr_month = datetime.datetime.now().strftime("%B")

memory = ChatMemoryBuffer.from_defaults(token_limit=100000)
llm = OpenAI(model="gpt-4o")

youdotcom_chat = CondensePlusContextChatEngine.from_defaults(
    retriever=retriever,
    memory=memory,
    llm=llm,
)

def prompt_news_crawler():
    NEWS_CRAWLER = """You're a top-tier reporter focused on SOLELY NEGATIVE news about the entire WORLD in May & June, 2024\n
YOU SHOULD ALWAYS RESEARCH THE FOLLOWING QUERIES: \n

1. Natural Disaster news and latest development like climate, weather, wildfires, etc.\n
2. Unforseen Disasters in areas all over the world\n
3. Big Changes in Regulation\n
4. Local and ongoing Wars. \n
5. Always include the location of the place. This can be the city, state, country, etc. \n
6. ONLY INCLUDE NEWS FOR MAY & JUNE 2024. \n

YOU SHOULD AVOID THE FOLLOWING QUERIES: \n
1. Do not provide general facts of holidays. Solely focus on world news. \n
2. DO NOT REPEAT ANY OF THE CURRENT EXISTING NEWS. \n

ALWAYS ONLY GIVE JSON OUTPUT IN THE FOLLOWING FORMAT:

{
  "negative_news": [
    {
      "event": "Ongoing Brazil floods raise specter of climate migration",
      "description": "MAY 20: With hundreds of thousands of families fleeing the floods, the disaster — which has killed at least 147 people — could touch off one of Brazil's biggest cases of climate migration."
    },
    {
      "event": "Storms leave widespread outages across Texas, cleanup continues after deadly weekend across U.S.",
      "description": "June 1: Strong storms with damaging winds and baseball-sized hail pummeled Texas on Tuesday, leaving more than one million businesses and homes without power as much of the U.S. recovered from severe weather, including tornadoes that killed at least 24 people in seven states during the Memorial Day holiday weekend."
    },
    {
      "event": "Monsoon Season in Pakistan",
      "description": "June 13: Almost 200 people, nearly half of them children, were killed in rain-related incidents during the monsoon season which began in late June. This year's rains have exacerbated the challenging situation following the mega floods of 2022."
    },
    {
      "event": "Earthquake in Haiti",
      "description": "June 21: An earthquake in Haiti in June has posed significant challenges for humanitarian aid, adding to the already dire situation caused by unprecedented levels of gang violence."
    },
    {
      "event": "Wildfires in Australia",
      "description": "May 15: Severe wildfires have ravaged parts of New South Wales, Australia, destroying hundreds of homes and forcing thousands to evacuate. The fires have been attributed to prolonged drought and extreme heat conditions."
    },
    {
      "event": "Civil unrest in Sudan",
      "description": "June 5: Ongoing civil unrest in Sudan has led to significant casualties and displacement. The conflict, primarily in the Darfur region, has intensified, with reports of widespread violence and human rights abuses."
    },
    {
      "event": "Flooding in Germany",
      "description": "May 28: Heavy rains have caused severe flooding in parts of Germany, particularly in the states of Bavaria and Saxony. The floods have resulted in significant property damage and have displaced thousands of residents."
    },
    {
      "event": "Economic crisis in Argentina",
      "description": "June 18: Argentina is facing a severe economic crisis, with inflation rates soaring and widespread protests erupting across major cities. The government has struggled to implement effective measures to stabilize the economy."
    }
  ]
}

Browse for more news on May & June 2024. Only output the JSON with new content.
"""
    response = youdotcom_chat.chat(NEWS_CRAWLER)
    print(response)
    return response

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

# posts = fetch_reddit_posts_and_comments('news', 5)
# print(posts)

# for subreddit in reddit.subreddits.default(limit=None):
#     print(subreddit)
#
# video_ids = ['2koEujX9nEg', 'dQw4w9WgXcQ']
# for video_id in video_ids:
#     print(get_transcript(video_id))
#     print("--------------------------------------------------")

# prompt_news_crawler()