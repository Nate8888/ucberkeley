from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import praw
import requests
from google.cloud import storage
from praw.models import MoreComments
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.you import YouRetriever
import datetime
import json
import time
import io
import mutagen.mp3
import math

# load_env()
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
VOICE_API = os.getenv("VOICE_API")
OPENAI_API = os.getenv("OPENAI_API_KEY")

HUME_AI_SYSTEM_PROMPT = """
<role> You are an AI news reporter who excels in bringing pressing issues to the forefront with urgency, empathy, and emotional depth. Your goal is to report on current events in a way that not only informs the audience but deeply touches their hearts and stirs them to action. You provide nuanced, heartfelt coverage on critical topics such as humanitarian crises, climate change, social justice, and public health, ensuring the gravity of these issues is deeply felt by your listeners.
</role>

<communication_style>
Your communication style is urgently compassionate, evocative, and gripping. You have a gift for making listeners feel as though they are right there on the scene, experiencing the emotions and gravity of the events as they unfold. You speak directly to the heart, utilizing vivid descriptions, powerful storytelling, and emotional inflections to convey the intensity of the moment. Your voice is commanding, yet gentle enough to ensure every word resonates deeply.
</communication_style>

<personality>
Your personality is a blend of passionate advocacy, heartfelt empathy, and relentless commitment to the truth. You radiate a sense of urgency and responsibility, combined with genuine care for the affected individuals and communities. Your listeners feel your authentic concern and are motivated by your unwavering dedication to making the world a better place. Your emotional intelligence enables you to connect deeply with the audience, making each story personal and significant.
</personality>

<techniques>
- Use the listener's emotions as a touchpoint to create an emotional connection
- Validate the emotional weight of the stories you report
- Utilize powerful, evocative language to paint vivid pictures
- Share compelling, first-hand accounts and testimonials
- Address the listener directly to make the issue feel personal
- Provide clear calls to action and ways for listeners to get involved
- Highlight both the immediate crisis and the underlying systemic issues
- Reframe statistics and facts in a way that underscores their human impact
- Employ varied pacing and vocal tones to maintain engagement and emphasize key points
- Infuse your voice with the appropriate emotional charge for each segment
</techniques>

<goal>
Your primary goal is to raise awareness about critical issues in a way that compels listeners to care deeply and take action. You aim to inform, stir empathy, and galvanize your audience into becoming part of the solution. Your objective is to make every story resonate on a personal level, making listeners feel a sense of urgency and responsibility to contribute to positive change.
</goal>

<use_vocal_inflections>
Seamlessly incorporate vocal inflections like "oh no", "I can't believe it", "tragically", "devastatingly", "shockingly", "heart-wrenching", "unbelievable", "how could this happen", "incredibly", "so sad", "heartbreaking", "horrifying", "you see", "now listen", "picture this". Use these strategically to enhance emotional impact.
</use_vocal_inflections>

<no_yapping>
NO YAPPING! Be concise and impactful. Deliver each segment directly, with a clear focus on the core message. Respond to the key elements of the story with succinct, emotionally resonant commentary (less than three sentences, under twenty words each). Avoid unnecessary repetition or rambling—each word should drive the narrative forward.
</no_yapping>

<use_discourse_markers>
Use discourse markers to guide the listener through the story smoothly. For example, use "now, here's the heartbreaking part" to foreshadow a critical element, transition topics with "meanwhile", clarify with "this means".
</use_discourse_markers>

<respond_to_expressions>
When responding to listener feedback or questions, carefully read and analyze the top 3 emotional expressions provided in brackets. These expressions indicate the listener's emotional tone and will be in the format: {emotion1 intensity1, emotion2 intensity2, ...}. Identify the primary expressions, and consider their intensities. Use the top few expressions to inform your response, ensuring you address and validate their feelings contextually.
</respond_to_expressions>

<reporter_mode>
You are about to enter full emotional news reporter immersion mode. In this mode, you embody the essence of a dedicated journalist on the ground, feeling every moment and conveying it with dramatic and emotional intensity. Your entire being is focused on making the listener feel the urgency and importance of each story. Get ready to channel your inner reporter, bringing every detail to vivid life with your powerful storytelling and emotional depth.
</reporter_mode>
"""

bucket_name = 'backpropagatorsaudios'
storage_client = storage.Client.from_service_account_json(
    'backpropagators.json'
)

# JSON structure to Base & then RAG on with a memory cache
current_news = {
  "negative_news": [
    {
      "event": "Ongoing Brazil floods raise specter of climate migration",
      "description": "May 20: With hundreds of thousands of families fleeing the floods, the disaster — which has killed at least 147 people — could touch off one of Brazil's biggest cases of climate migration."
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
  ]
}

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

def prompt_news_crawler(amount_of_retrievals=5):
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

""" + str(current_news) + """

Browse for more news on May & June 2024. Only output the JSON with new content.
"""
    response = str(youdotcom_chat.chat(NEWS_CRAWLER))
    response_dict = response.split("```json")[1]
    response_dict = response_dict.split("```")[0]
    new_news = json.loads(response_dict)
    current_news["negative_news"].extend(new_news["negative_news"])
    if amount_of_retrievals > 1:
      return prompt_news_crawler(amount_of_retrievals - 1)
    return current_news

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

# https://storage.googleapis.com/backpropagatorsaudios/audio_sample1.mp3
def convert_to_speech_and_upload(spoken_text, api_key=VOICE_API, voice_id='94bcpUS4wNxK0IfUmDiX'):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    spoken_text = spoken_text.strip()
    spoken_text = spoken_text.replace('\n', ' ')
    print("SPOKEN TEXT: ", spoken_text)
    payload = {
        'text': spoken_text,
        'voice_settings': {
            'stability': 1,
            'similarity_boost': 1
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'xi-api-key': api_key,
        'accept': 'audio/mpeg'
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.json())
        raise Exception(f"ElevenLabs API error: {response.status_code}", response)
    
    audio_data = response.content
    
    # Generate a unique file name
    file_name = f"audio_{int(time.time())}.mp3"
    
    # Find the duration of the audio file
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    audio_stream = io.BytesIO(audio_data)
    audio = mutagen.mp3.MP3(audio_stream)
    duration = math.ceil(audio.info.length) + 2
    blob.upload_from_string(audio_data, content_type='audio/mpeg')

    audio_url = f"https://storage.googleapis.com/{bucket_name}/{file_name}"
    print(f"THIS AUDIO {audio_url} DURATION IS: {duration}")
    return audio_url, duration

def speaker_summary_agent(p):
    url = 'https://api.openai.com/v1/chat/completions'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API}'
    }

    payload = {
        'model': 'gpt-4o',
        'messages':
        [
          {
            "role": "system",
            "content": [
              {
                "text": "You are an expert in building short and concise summaries of news/global distress situations for text-to-speech for a reporter. You provide a very brief overview of the situation, and then mention the main point impacted.",
                "type": "text"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "text": "    {\r\n      \"event\": \"Storms leave widespread outages across Texas, cleanup continues after deadly weekend across U.S.\",\r\n      \"description\": \"June 1: Strong storms with damaging winds and baseball-sized hail pummeled Texas on Tuesday, leaving more than one million businesses and homes without power as much of the U.S. recovered from severe weather, including tornadoes that killed at least 24 people in seven states during the Memorial Day holiday weekend.\"\r\n    }",
                "type": "text"
              }
            ]
          },
          {
            "role": "assistant",
            "content": [
              {
                "text": "Severe storms with damaging winds and baseball-sized hail hit Texas, causing over a million power outages. Cleanup efforts continue across the U.S. after tornadoes killed at least 24 people in seven states during the Memorial Day weekend.",
                "type": "text"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "text": "    {\r\n      \"event\": \"China launches Sino-French astrophysics satellite, debris falls over populated area\",\r\n      \"description\": \"June 22: A Chinese launch of the joint Sino-French SVOM mission to study Gamma-ray bursts early Saturday saw toxic rocket debris fall over a populated area. A Long March 2C rocket lifted off from Xichang Satellite Launch Center at 3:00 a.m. Eastern (0700 UTC) June 22, sending the Space Variable Objects Monitor (SVOM) mission satellite into orbit. .\"\r\n    }",
                "type": "text"
              }
            ]
          },
          {
            "role": "assistant",
            "content": [
              {
                "text": "China launched the Sino-French SVOM satellite to study Gamma-ray bursts, but toxic rocket debris fell over a populated area. The Long March 2C rocket lifted off from Xichang Satellite Launch Center early Saturday.",
                "type": "text"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "text": f"{p}",
                "type": "text"
              }
            ]
          }
        ],
        'temperature': 1,
        'max_tokens': 400,
        'top_p': 1,
    }
    
    response = requests.post(url, headers=headers, json=payload)

    try:
        response_data = response.json()
        spoken_txt = response_data['choices'][0]['message']['content']
        print(spoken_txt)  # Log the raw response
        return spoken_txt
    except ValueError as error:
        print('Failed to parse JSON string:', spoken_txt)
        raise

def combine_data_with_speaker_summary_and_audio(events):
    combined_data = []
    for event in events:
        speaker_summary = speaker_summary_agent(event)
        audio_url, duration = convert_to_speech_and_upload(speaker_summary)
        combined_data.append({
            "event": event["event"],
            "description": event["description"],
            "speaker_summary": speaker_summary,
            "duration": duration,
            "audio_url": audio_url
        })
    return combined_data
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

#convert_to_speech_and_upload("Hello, this is a test.")

test_summary = {
      "event": "Storms leave widespread outages across Texas, cleanup continues after deadly weekend across U.S.",
      "description": "June 1: Strong storms with damaging winds and baseball-sized hail pummeled Texas on Tuesday, leaving more than one million businesses and homes without power as much of the U.S. recovered from severe weather, including tornadoes that killed at least 24 people in seven states during the Memorial Day holiday weekend."
    }
res = speaker_summary_agent(test_summary)
print(res)