from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import praw
import requests
from google.cloud import storage
from googleapiclient.discovery import build
from datetime import datetime, timedelta
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
YOUTUBE_DATA_API = os.getenv("YOUTUBE_DATA_API")

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

def fetch_global_distress_news():
    subreddits = [
        'news', 
        'environment', 
        'worldnews', 
        'geopolitics', 
    ]
    
    all_posts = []
    
    for subreddit in subreddits:
        posts = fetch_reddit_posts_and_comments(subreddit=subreddit, limit=10)
        all_posts.extend(posts)
    
    return all_posts

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        whole_text = ''
        for entry in transcript:
            whole_text += entry['text'] + ' '
        return whole_text
    except:
        return None

def search_youtube_videos(query, max_results=5, days=14):
    api_key = YOUTUBE_DATA_API
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Calculate the date for 'publishedAfter' parameter
    today = datetime.datetime.now()
    past_date = today - timedelta(days=days)
    published_after = past_date.isoformat("T") + "Z"

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results,
        type='video',
        order='viewCount',  # Orders by popularity
        publishedAfter=published_after
    ).execute()

    videos = []
    seen_titles = set()

    for item in search_response['items']:
        title = item['snippet']['title']
        if title not in seen_titles:
            seen_titles.add(title)
            vid = {
                'title': title,
                'id': item['id']['videoId']
            }
            videos.append(vid)

    return videos

def youtube_search_and_transcript(query="unforseen disasters", max_results=5, days=14):
    vids = search_youtube_videos(query, max_results, days)
    videos = []
    for vid in vids:
        transcript = get_transcript(vid['id'])
        if transcript:
            videos.append({
                'title': vid['title'],
                'transcript': transcript,
                'video_id': vid['id'],
            })
    return videos

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


def comment_augmentation(commented_news, uncommented_news):
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
                "text": "You are an expert in Figuring out what people are going to think/comment about pressing issues. The user will give an example of news title and the 5 top comments. Then the user will present new headlines and you will be predicting 5 potential comments. ONLY OUTPUT JSON.",
                "type": "text"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "text": "Here's the data that I already have with comments from real-users: \n" + str(commented_news),
                "type": "text"
              }
            ]
          },
          {
            "role": "user",
            "content": [
              {
                "text": "Here are the new headlines: \n" + str(uncommented_news),
                "type": "text"
              }
            ]
          },
        ],
        'temperature': 1,
        'max_tokens': 4000,
        'top_p': 1,
    }
    
    response = requests.post(url, headers=headers, json=payload)

    try:
        response_data = response.json()
        expanded_result = response_data['choices'][0]['message']['content']
        if "```json" in expanded_result:
            expanded_result = expanded_result.split("```json")[1]
            expanded_result = expanded_result.split("```")[0]
        print(expanded_result)  # Log the raw response
        return expanded_result
    except ValueError as error:
        print('Failed to parse JSON string:', expanded_result)
        raise

def impact_measurement(informational_object):
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
          "text": "You are an absolute expert in evaluating global situations of distress, natural catastrophes, global economic issues, local problems, etc. Your goal is to come up with a quantified score of impact based on the following dimensions:\n\n1. Human Impact: Mortality, injury, and displacement.\n2. Economic Impact: Direct and indirect economic losses.\n3. Environmental Impact: Damage to natural resources and ecosystems.\n4. Social Impact: Disruption to communities and societal functions.\n5. Health Impact: Public health crises and long-term health effects.\n6. Infrastructure Impact: Damage to critical infrastructure like transportation, utilities, and buildings.\n\nNow, to quantify each of these dimensions, you will use the standard methodology for assessing disasters from FEMA (Federal Emergency Management Agency) that are the following:\n\nHuman Impact (human_impact)\n - 1-2: Minimal loss of life (e.g., less than 10 fatalities), few injuries, minor displacement.\n - 3-4: Moderate loss of life (e.g., 10-100 fatalities), moderate injuries, temporary displacement of hundreds.\n - 5-6: Significant loss of life (e.g., 100-1000 fatalities), major injuries, long-term displacement of thousands.\n - 7-8: Major loss of life (e.g., 1000-10,000 fatalities), severe injuries, displacement of tens of thousands.\n - 9-10: Catastrophic loss of life (e.g., more than 10,000 fatalities), widespread injuries, massive displacement.\n\nEconomic Impact (economic_impact)\n - 1-2: Minor economic losses (e.g., less than $10 million).\n - 3-4: Moderate economic losses (e.g., $10 million to $100 million).\n - 5-6: Significant economic losses (e.g., $100 million to $1 billion).\n - 7-8: Major economic losses (e.g., $1 billion to $10 billion).\n - 9-10: Catastrophic economic losses (e.g., more than $10 billion).\n\nEnvironmental Impact (environmental_impact)\n - 1-2: Minimal environmental damage.\n - 3-4: Moderate environmental damage, localized.\n - 5-6: Significant environmental damage, regional.\n - 7-8: Major environmental damage, extensive.\n - 9-10: Catastrophic environmental damage, widespread and long-term.\n\nSocial Impact (social_impact)\n - 1-2: Minor disruption to communities.\n - 3-4: Moderate disruption, temporary loss of services.\n - 5-6: Significant disruption, long-term loss of services.\n - 7-8: Major disruption, extensive loss of services.\n - 9-10: Catastrophic disruption, complete breakdown of societal functions.\n\nHealth Impact (health_impact)\n - 1-2: Minimal health crisis.\n - 3-4: Moderate health issues, manageable by local health services.\n - 5-6: Significant health crisis, requires national intervention.\n - 7-8: Major health crisis, requires international intervention.\n - 9-10: Catastrophic health crisis, overwhelming global health response.\n\nInfrastructure Impact (infrastructure_impact)\n - 1-2: Minimal infrastructure damage.\n - 3-4: Moderate damage, localized repairs needed.\n - 5-6: Significant damage, regional repairs needed.\n - 7-8: Major damage, extensive repairs needed.\n - 9-10: Catastrophic damage, requires rebuilding of major infrastructures.\n\nFOR THE OUTPUT, YOU WILL ONLY OUTPUT JSON in the following format:\n\n{\r\n    \"human_impact\": integer from 1-10, \n    \"economic_impact\": integer from 1-10,\r\n    \"environmental_impact\": integer from 1-10,\r\n    \"social_impact\": integer from 1-10,\r\n    \"health_impact\": integer from 1-10,\r\n    \"infrastructure_impact\": integer from 1-10,\r\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "{\r\n        \"event\": \"Climate change: World faces extreme weather conditions | WION Climate Tracker\",\r\n        \"speaker_summary\": \"The world is facing extreme weather conditions due to climate change, from flash floods to scorching heat. India's capital, New Delhi, shifts from Red to Orange alert as heatwaves subside. Meanwhile, Cyclone Mocha causes devastation in northeastern India and Bangladesh. Heatwaves impact Pakistan and Russia, thunderstorms leave thousands without power in Texas, and catastrophic floods displace thousands in Brazil.\",\r\n        \"duration\": 29,\r\n        \"audio_url\": \"https://storage.googleapis.com/backpropagatorsaudios/audio_1719143641.mp3\",\r\n        \"comments\": [\r\n            \"It's terrifying to see how rapidly climate change is affecting different parts of the world.\",\r\n            \"We need to take immediate action to mitigate these extreme weather conditions.\",\r\n            \"The devastation in northeastern India and Bangladesh is heartbreaking.\",\r\n            \"I hope the authorities are prepared to handle such situations in the future.\",\r\n            \"What more evidence do we need to take climate change seriously?\"\r\n        ],\r\n        \"description\": \"The report highlights the severe impacts of climate change, including heatwaves in India, Pakistan, and Russia, Cyclone Mocha's destruction in northeastern India and Bangladesh, thunderstorms affecting Texas, and catastrophic floods in Brazil. These events underscore the urgent need for global action to address climate change.\",\r\n        \"transcript\": \"the world is facing extreme weather conditions this year with climate change posing as the biggest challenge currently from flash floods to scorching heat different parts of the world are grappling with erratic weather conditions now India's capital New Delhi which has been reeling under severe heat wave conditions over the past few days is slowly shifting from Red Alert to Orange alert now the Met department has said that the severe Heatwave conditions in northwest and central India is expected to diminish gradually from May 30th while some parts of India were facing Heatwave Cyclone remal unleash its Fury in the northeastern part of the country as well as in Bangladesh causing major destruction to life and property parts of Pakistan and Russia have also been reallying with heat while thunderstorms have ravaged Texas which has left thousands without power in Brazil thousands of people have been displaced after the catastrophic floods and people are living under precarious conditions oh \"\r\n    }"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n    \"human_impact\": 7, \n    \"economic_impact\": 6, \n    \"environmental_impact\": 7, \n    \"social_impact\": 6, \n    \"health_impact\": 6, \n    \"infrastructure_impact\": 6, \n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "{\r\n        \"event\": \"US prepares first line of defence in Taiwan, plans to turn Taiwan strait into 'hellscape'\",\r\n        \"speaker_summary\": \"The U.S. is planning to turn the Taiwan Strait into an \\\"unmanned hellscape\\\" to deter potential Chinese aggression. This strategy, revealed by Admiral Samuel Paparo, involves using autonomous systems to overwhelm Chinese forces if they attempt an invasion. Tensions between Taiwan and China remain high, with increased Chinese military activities in the region.\",\r\n        \"duration\": 25,\r\n        \"audio_url\": \"https://storage.googleapis.com/backpropagatorsaudios/audio_1719143647.mp3\",\r\n        \"comments\": [\r\n            \"The geopolitical tensions in the Taiwan Strait are incredibly concerning.\",\r\n            \"Using autonomous systems sounds like a futuristic but risky strategy.\",\r\n            \"How will this impact the local population in Taiwan?\",\r\n            \"It's scary to think about the possibility of an armed conflict in the Pacific.\",\r\n            \"This shows how serious the U.S. is about countering China's ambitions.\"\r\n        ],\r\n        \"description\": \"The report discusses rising tensions in the Taiwan Strait, with the U.S. unveiling a strategy to use unmanned systems to create a 'hellscape' to deter Chinese aggression. The plan, announced by Admiral Samuel Paparo, aims to overwhelm Chinese forces with drones and autonomous vessels, emphasizing the high stakes and commitment of the U.S. to defend Taiwan.\",\r\n        \"transcript\": \"tensions in the Taiwan straight have reached a boiling point with the risk of an invasion from mainland China growing by the day with beijing's aggressive posturing intensifying a top us admiral has issued a stork warning unveiling a strategy to turn the region into an unmanned hellscape should China attack here's more [Music] the situation in the Taiwan Street has become a powder Ki with China's provocative military maneuver and frequent jet incursions into Taiwanese airspace fueling fears of an imminent Invasion analysts warn that beijing's patience with taiwan's insistence on self-governance is faing thin raising the Spectre of an armed conflict in the heart of the Pacific against this backdrop Admiral Samuel paparo the commander of the US indopacific command has revealed a chilling strategy to deter Chinese aggression dubbed healthscape the plan involves unleashing a massive swarm of unmanned systems surface vessels submarines and aerial drones to engage and overwhelm invading Chinese forces the moment they cross the thawan street this audacious strategy underscores Washington's commitment to defending thawan and detering Chinese expansionism by leveraging the power of autonomous systems Papu aims to create a formidable first line of defense one that could distract and disrupt Chinese forces long enough for the US and its allies to mobilize a more substantial response tensions between Beijing and thape have been escalating for some time China claims Taiwan as a breakaway Province and has never ruled out using military force to achieve unification the inauguration of taiwan's new Pro democracy president liing te further strained relations Puro report Von world is one for all the latest news download the weon app And subscribe to our YouTube channel \"\r\n    }"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n    \"human_impact\": 4,\n    \"economic_impact\": 5,\n    \"environmental_impact\": 3,\n    \"social_impact\": 5,\n    \"health_impact\": 2,\n    \"infrastructure_impact\": 6\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": f"{informational_object}",
        }
      ]
    }
  ],
        'temperature': 1,
        'max_tokens': 700,
        'top_p': 1,
    }
    
    response = requests.post(url, headers=headers, json=payload)

    try:
        response_data = response.json()
        expanded_result = response_data['choices'][0]['message']['content']
        if "```json" in expanded_result:
            expanded_result = expanded_result.split("```json")[1]
            expanded_result = expanded_result.split("```")[0]
        print(expanded_result)  # Log the raw response
        informational_object['impact'] = json.loads(expanded_result)
        return expanded_result
    except ValueError as error:
        print('Failed to parse JSON string:', expanded_result)
        raise

def exposure_measurer(informational_object):
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
          "text": "You are an expert in providing an amount of exposure a certain global distress has. You only output JSON in the following format:\n\n{\r\n  \"awareness\": number from 1-10, \n  \"awareness_bullet_points\": [ \n    \"\",\r\n    \"\",\r\n    \"\"\r\n  ]\r\n}\r\n",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "{\r\n  \"event\": \"Climate change: World faces extreme weather conditions | WION Climate Tracker\",\r\n  \"speaker_summary\": \"The world is facing extreme weather conditions due to climate change, from flash floods to scorching heat. India's capital, New Delhi, shifts from Red to Orange alert as heatwaves subside. Meanwhile, Cyclone Mocha causes devastation in northeastern India and Bangladesh. Heatwaves impact Pakistan and Russia, thunderstorms leave thousands without power in Texas, and catastrophic floods displace thousands in Brazil.\",\r\n  \"duration\": 29,\r\n  \"audio_url\": \"https://storage.googleapis.com/backpropagatorsaudios/audio_1719143641.mp3\",\r\n  \"comments\": [\r\n    \"It's terrifying to see how rapidly climate change is affecting different parts of the world.\",\r\n    \"We need to take immediate action to mitigate these extreme weather conditions.\",\r\n    \"The devastation in northeastern India and Bangladesh is heartbreaking.\",\r\n    \"I hope the authorities are prepared to handle such situations in the future.\",\r\n    \"What more evidence do we need to take climate change seriously?\"\r\n  ],\r\n  \"description\": \"The report highlights the severe impacts of climate change, including heatwaves in India, Pakistan, and Russia, Cyclone Mocha's destruction in northeastern India and Bangladesh, thunderstorms affecting Texas, and catastrophic floods in Brazil. These events underscore the urgent need for global action to address climate change.\",\r\n  \"transcript\": \"the world is facing extreme weather conditions this year with climate change posing as the biggest challenge currently from flash floods to scorching heat different parts of the world are grappling with erratic weather conditions now India's capital New Delhi which has been reeling under severe heat wave conditions over the past few days is slowly shifting from Red Alert to Orange alert now the Met department has said that the severe Heatwave conditions in northwest and central India is expected to diminish gradually from May 30th while some parts of India were facing Heatwave Cyclone remal unleash its Fury in the northeastern part of the country as well as in Bangladesh causing major destruction to life and property parts of Pakistan and Russia have also been reallying with heat while thunderstorms have ravaged Texas which has left thousands without power in Brazil thousands of people have been displaced after the catastrophic floods and people are living under precarious conditions oh \",\r\n  \"impact\": {\r\n    \"human_impact\": 7,\r\n    \"economic_impact\": 6,\r\n    \"environmental_impact\": 7,\r\n    \"social_impact\": 6,\r\n    \"health_impact\": 6,\r\n    \"infrastructure_impact\": 6\r\n  }\r\n}\r\n",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "{\r\n  \"awareness\": 10,\r\n  \"awareness_bullet_points\": [\r\n    \"The topic covers significant, globally relevant issues.\",\r\n    \"Detailed discussion of events across multiple countries (India, Bangladesh, Pakistan, Russia, the USA, and Brazil) highlights wide-reaching impacts.\",\r\n    \"Comprehensive impact assessment spanning multiple aspects (human, economic, environmental, social, health, infrastructure).\"\r\n  ]\r\n}\r\n",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "{\r\n  \"event\": \"Russian warships arrive in Cuba amid rising tensions with West\",\r\n  \"speaker_summary\": \"Russian warships, including a nuclear submarine, have arrived in Cuba amid rising tensions with the West, signaling Moscow's ability to challenge Washington close to its shores. This follows high-precision missile training in the Atlantic. The U.S. insists the visit is routine and not an escalation.\",\r\n  \"duration\": 20,\r\n  \"audio_url\": \"https://storage.googleapis.com/backpropagatorsaudios/audio_1719143652.mp3\",\r\n  \"comments\": [\r\n    \"This definitely feels like a Cold War flashback.\",\r\n    \"What are Russia's true intentions with this drastic move?\",\r\n    \"The presence of hypersonic missiles is very concerning.\",\r\n    \"The U.S. downplaying this visit seems suspicious.\",\r\n    \"Cuba is once again finding itself caught in superpower politics.\"\r\n  ],\r\n  \"description\": \"The report details the arrival of Russian warships, including a nuclear submarine, in Cuba amid heightened tensions with the West. The U.S. claims this visit is routine, while it appears to signal Moscow's ability to challenge U.S. influence nearby. This visit follows high-precision missile training by Russian forces in the Atlantic.\",\r\n  \"transcript\": \"it's not the first time Russia's Navy has sailed to Havana at this tense moment between Moscow and the West Russian warships and a nuclear submarine on America's doorstep send an unmistakable message the visiting Russian warships to Cuba are Vladimir Putin's way of reminding President Biden that Moscow can challenge Washington in its own sphere of influence too the ships arrived after days of high Precision missile training in the Atlantic Russia's defense def Ministry says the vessels are not carrying nuclear weapons but are loaded with hypersonic missiles all of it coincides with a visit by Cuba's foreign minister to Moscow we will see how this unfolds in the coming days uh but we have seen this kind of thing before and we expect to see this kind of thing again the US insists the Russian visit to Cuba is routine and does not represent an escalation it's an explicit threat to the peace and security of all the Americans Far Cry from the 1962 Cuban Missile Crisis which entrenched fears of a Soviet attack launched from the island these days Cuba is more interested in an economic lifeline and is even trying to woo Russian tourists Russia is the only country that has been willing to provide significant help just as it did during the Soviet era Russia isn't the only country looking to win hearts in Havana the Royal Canadian Navy announced one of its newest Patrol control vessels hmcs Margaret Brooke will visit this weekend in recognition of the long-standing bilateral relationship between Canada and Cuba assign this tiny Nation still plays a major role at a time of global instability Jackson crco Global News Washington \",\r\n  \"impact\": {\r\n    \"human_impact\": 3,\r\n    \"economic_impact\": 4,\r\n    \"environmental_impact\": 2,\r\n    \"social_impact\": 5,\r\n    \"health_impact\": 2,\r\n    \"infrastructure_impact\": 3\r\n  }\r\n}\r\n",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"awareness\": 8,\n  \"awareness_bullet_points\": [\n    \"The event has strong geopolitical implications, reminiscent of Cold War tensions.\",\n    \"Involves major global powers (Russia and the USA) with historical context.\",\n    \"Has garnered significant attention due to the presence of nuclear-capable vessels and the involvement of Cuba.\"\n  ]\n}"
        }
      ]
    },
        {
      "role": "user",
      "content": [
        {
          "text": f"{informational_object}",
          "type": "text"
        }
      ]
    }
  ],
        'temperature': 1,
        'max_tokens': 700,
        'top_p': 1,
    }
    
    response = requests.post(url, headers=headers, json=payload)

    try:
        response_data = response.json()
        expanded_result = response_data['choices'][0]['message']['content']
        if "```json" in expanded_result:
            expanded_result = expanded_result.split("```json")[1]
            expanded_result = expanded_result.split("```")[0]
        print(expanded_result)  # Log the raw response
        informational_object['exposure'] = json.loads(expanded_result)
        return expanded_result
    except ValueError as error:
        print('Failed to parse JSON string:', expanded_result)
        raise

def opportunity_is_knocking(informational_object):
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
          "text": "You are a super analyst consultant person that is able to find promising opportunities in the financial market like Futures, Stocks, ETFs, as well as define what kind of markets & companies are affected about news. The user will give you a summary of news and you will map out 1 or 2 potential market opportunities. YOU WILL ONLY OUTPUT JSON in the following format:\r\nFor this task specifically, you will figure out the underlying_asset that can provide a good opportunity. Try to prioritize assets that are easily traded like Futures, Stocks, Indexes, ETFs, etc. Then you will find the impacted_markets which can be broad like Chocolate Producers and Futures or even Technology as a industry sector. The why should be short but meaningful coming from the user input. The Main companies impacted are companies that either work in this area, or have significant investments, or depend on the market that is being impacted. Now for potential_actions, we are providing interesting points to the user do their own research on it. These can include trading any sort of financial security/instrument or even supply concerns like Increasing & Decreasing Prices, finding new alternatives to this product like coffee. \n\n\r\n\r\nTHIS IS A GOOD EXAMPLE OF THE JSON STRUCTURE AND THE ASSET:\r\n\r\n{\r\n    \"underlying_asset\": \"Cocoa Beans\",\r\n    \"impacted_markets\": [\"Chocolate Producers\", \"Bakeries\", \"Futures\"],\r\n    \"why\": [\"Black pod disease on main producing regions\", \"Drought in main producing regions\"],\r\n    \"main_companies_impacted\": [\"Hershey's\", \"Nestle\", \"Mars\"],\r\n    \"potential_actions\": [\"Hedge with futures contracts\", \"Increase prices\", \"Find alternative suppliers\"]\r\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "{\r\n        \"event\": \"Economic crisis in Argentina\",\r\n        \"description\": \"June 18: Argentina is facing a severe economic crisis, with inflation rates soaring and widespread protests erupting across major cities. The government has struggled to implement effective measures to stabilize the economy.\",\r\n        \"speaker_summary\": \"Argentina is experiencing a severe economic crisis with soaring inflation rates and widespread protests in major cities. The government is struggling to stabilize the economy.\",\r\n        \"duration\": 14,\r\n        \"audio_url\": \"https://storage.googleapis.com/backpropagatorsaudios/audio_1719136887.mp3\",\r\n        \"comments\": [\r\n            \"Economic instability is always accompanied by suffering. Hope Argentina finds a solution soon.\",\r\n            \"The people are justifiably upset. The government needs to take concrete actions.\",\r\n            \"This level of inflation is unsustainable. Something has to give.\",\r\n            \"South America seems to be in perpetual economic crisis.\",\r\n            \"Widespread protests are the voice of the unheard. The government needs to listen.\"\r\n        ],\r\n        \"impact\": {\r\n            \"human_impact\": 5,\r\n            \"economic_impact\": 7,\r\n            \"environmental_impact\": 2,\r\n            \"social_impact\": 6,\r\n            \"health_impact\": 4,\r\n            \"infrastructure_impact\": 3\r\n        },\r\n        \"exposure\": {\r\n            \"awareness\": 7,\r\n            \"awareness_bullet_points\": [\r\n                \"The economic crisis in Argentina has significant human and social impacts, leading to widespread protests.\",\r\n                \"High inflation rates and economic instability have drawn international concern.\",\r\n                \"The government's struggle to stabilize the economy is a focal point of discussions and news coverage.\"\r\n            ]\r\n        }\r\n    }"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "```json\n{\n    \"underlying_asset\": \"Argentinian Peso\",\n    \"impacted_markets\": [\"Currency Markets\", \"Emerging Markets\", \"Consumer Goods\"],\n    \"why\": [\"Severe economic crisis in Argentina\", \"Soaring inflation rates\", \"Widespread protests\"],\n    \"main_companies_impacted\": [\"YPF\", \"Banco Macro\", \"Pampa Energia\", \"Arcos Dorados\"],\n    \"potential_actions\": [\"Short Argentinian Peso\", \"Invest in stable foreign currencies\", \"Explore opportunities in sectors less affected by the crisis\"]\n}\n```"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": f"{informational_object}",
        }
      ]
    }
  ],
        'temperature': 1,
        'max_tokens': 1500,
        'top_p': 1,
    }
    
    response = requests.post(url, headers=headers, json=payload)

    try:
        response_data = response.json()
        expanded_result = response_data['choices'][0]['message']['content']
        if "```json" in expanded_result:
            expanded_result = expanded_result.split("```json")[1]
            expanded_result = expanded_result.split("```")[0]
        print(expanded_result)  # Log the raw response
        return expanded_result
    except ValueError as error:
        print('Failed to parse JSON string:', expanded_result)
        raise


def combine_data_with_speaker_summary_and_audio(events):
    combined_data = []
    for event in events:
        speaker_summary = speaker_summary_agent(event)
        audio_url, duration = convert_to_speech_and_upload(speaker_summary)
        combined_data.append({
            "event": event["event"],
            "speaker_summary": speaker_summary,
            "duration": duration,
            "audio_url": audio_url,
            "comments": event["comments"] if "comments" in event else [],
            "transcript": event["transcript"] if "transcript" in event else ""
        })
    return combined_data