import os
import requests
import pandas as pd
from tqdm import tqdm
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings
from datasets import load_dataset
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from google.cloud import storage
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from praw.models import MoreComments
import json
import time
import io
import math
from dotenv import load_dotenv

import mutagen.mp3

# Load environment variables
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
VOICE_API = os.getenv("VOICE_API")
YOUTUBE_DATA_API = os.getenv("YOUTUBE_DATA_API")
bucket_name = 'backpropagatorsaudios'

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


# Initialize Google Cloud Storage client
storage_client = storage.Client.from_service_account_json('backpropagators.json')

# RAGBot class definition
class RAGBot:
    def __init__(self, model='Falcon', dataset='robot maintenance'):
        self.model_path = ""
        self.data_path = dataset + '_dialogues.txt'
        self.user_input = ""
        self.context_verbosity = False
        self.model = model
        self.index = None
        self.llm = None

        # Only initialize and download the model and dataset once
        self.get_model()
        self.download_dataset()
        self.load_model(n_threads=64, max_tokens=50, repeat_penalty=1.50, n_batch=64, top_k=1, temp=0.7)
        self.build_vectordb(chunk_size=500, overlap=50)

    def get_model(self):
        self.model_path = "/home/common/data/Big_Data/GenAI/llm_models/nomic-ai--gpt4all-falcon-ggml/ggml-model-gpt4all-falcon-q4_0.bin"
        if not os.path.isfile(self.model_path):
            # Logic for model download (if needed)
            pass

    def download_dataset(self):
        if not os.path.isfile(self.data_path):
            datasets = {
                "robot maintenance": "FunDialogues/customer-service-robot-support", 
                "basketball coach": "FunDialogues/sports-basketball-coach", 
                "physics professor": "FunDialogues/academia-physics-office-hours",
                "grocery cashier": "FunDialogues/customer-service-grocery-cashier"
            }
            dataset = load_dataset(f"{datasets['robot maintenance']}")
            dialogues = dataset['train']
            df = pd.DataFrame(dialogues, columns=['id', 'description', 'dialogue'])
            dialog_df = df['dialogue']
            dialog_df.to_csv(self.data_path, sep=' ', index=False)
        else:
            print('data already exists in path.')

    def load_model(self, n_threads, max_tokens, repeat_penalty, n_batch, top_k, temp):
        callbacks = [StreamingStdOutCallbackHandler()]
        self.llm = GPT4All(model=self.model_path, callbacks=callbacks, verbose=False,
                           n_threads=n_threads, n_predict=max_tokens, repeat_penalty=repeat_penalty, 
                           n_batch=n_batch, top_k=top_k, temp=temp)

    def build_vectordb(self, chunk_size, overlap):
        loader = TextLoader(self.data_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        self.index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings(), text_splitter=text_splitter).from_loaders([loader])

    def get_response(self, user_input, conversation_history=None, top_k=1, rag_off=False):
        self.user_input = user_input
        results = self.index.vectorstore.similarity_search(self.user_input, k=top_k)
        context = "\n".join([document.page_content for document in results])

        if rag_off:
            template = """Question: {question}
            Answer: This is the response: """
            prompt = PromptTemplate(template=template, input_variables=["question"])
        else:
            template = """ Don't just repeat the following context, use it in combination with your knowledge to improve your answer to the question:{context}

            Question: {question}
            """
            prompt = PromptTemplate(template=template, input_variables=["context", "question"]).partial(context=context)

        if conversation_history:
            complete_input = f"Conversation History: {conversation_history}\n\nCurrent Question: {user_input}"
        else:
            complete_input = user_input

        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        response = llm_chain.run(complete_input)

        return response

# Initialize RAGBot
bot = RAGBot()

# Sample input for testing
sample_input = "Can you help me with my robot?"
conversation_history = "User: Hi\nBot: Hello, how can I assist you today?\nUser: I need help with my robot maintenance."

# Get response from the bot
response = bot.get_response(sample_input, conversation_history)
print(response)

def run_ragbot_prompt(prompt):
    conversation_history = ""  # Optionally track conversation history
    response = bot.get_response(prompt, conversation_history)
    result = response.strip()  # Assuming you may need to process the string here
    return result

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
    response = run_ragbot_prompt(NEWS_CRAWLER)
    response_dict = response.split("```json")[1]
    response_dict = response_dict.split("```")[0]
    new_news = json.loads(response_dict)
    current_news["negative_news"].extend(new_news["negative_news"])
    if amount_of_retrievals > 1:
        return prompt_news_crawler(amount_of_retrievals - 1)
    return current_news

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
            if relevant_comment_count >= 5:  # Limiting to 5 comments per post
                break
            if top_level_comment.body and top_level_comment.body != '[removed]':
                reddit_post['comments'].append(top_level_comment.body)
                relevant_comment_count += 1
        posts.append(reddit_post)
    return posts

def fetch_global_distress_news():
    subreddits = ['news', 'environment', 'worldnews', 'geopolitics']
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
    today = datetime.now()
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
            vid = {'title': title, 'id': item['id']['videoId']}
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

def convert_to_speech_and_upload(spoken_text, api_key=VOICE_API, voice_id='94bcpUS4wNxK0IfUmDiX'):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    spoken_text = spoken_text.strip().replace('\n', ' ')
    print("SPOKEN TEXT: ", spoken_text)
    payload = {'text': spoken_text, 'voice_settings': {'stability': 1, 'similarity_boost': 1}}
    headers = {'Content-Type': 'application/json', 'xi-api-key': api_key, 'accept': 'audio/mpeg'}

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
    prompt = f"""You are an expert in building short and concise summaries of news/global distress situations for text-to-speech for a reporter. 
    You provide a very brief overview of the situation and then mention the main point impacted.
    
    Here is the data:
    {p}
    """
    response = run_ragbot_prompt(prompt)
    return response

def comment_augmentation(commented_news, uncommented_news):
    prompt = f"""You are an expert in predicting what people are going to think/comment about pressing issues. 
    The user will give an example of news title and the 5 top comments. 
    Then the user will present new headlines and you will be predicting 5 potential comments. 
    ONLY OUTPUT JSON.
    
    Here's the data that I already have with comments from real-users: 
    {commented_news}
    
    Here are the new headlines: 
    {uncommented_news}
    """
    response = run_ragbot_prompt(prompt)
    expanded_result = response.split("```json")[1].split("```")[0]
    return json.loads(expanded_result)

def impact_measurement(informational_object):
    prompt = f"""You are an absolute expert in evaluating global situations of distress, natural catastrophes, global economic issues, local problems, etc. 
    Your goal is to come up with a quantified score of impact based on the following dimensions:
    - Human Impact: Mortality, injury, and displacement.
    - Economic Impact: Direct and indirect economic losses.
    - Environmental Impact: Damage to natural resources and ecosystems.
    - Social Impact: Disruption to communities and societal functions.
    - Health Impact: Public health crises and long-term health effects.
    - Infrastructure Impact: Damage to critical infrastructure like transportation, utilities, and buildings.
    
    Provide the impact scores for the following event in JSON format:
    {informational_object}
    """
    response = run_ragbot_prompt(prompt)
    expanded_result = response.split("```json")[1].split("```")[0]
    informational_object['impact'] = json.loads(expanded_result)
    return expanded_result

def exposure_measurer(informational_object):
    prompt = f"""You are an expert in providing an amount of exposure a certain global distress has. 
    Provide the exposure scores and bullet points in JSON format for the following:
    {informational_object}
    """
    response = run_ragbot_prompt(prompt)
    expanded_result = response.split("```json")[1].split("```")[0]
    informational_object['exposure'] = json.loads(expanded_result)
    return expanded_result

def opportunity_is_knocking(informational_object):
    prompt = f"""You are a super analyst consultant person that is able to find promising opportunities in the financial market like Futures, Stocks, 
    ETFs, as well as define what kind of markets & companies are affected by news. 
    Provide the information in JSON format for the following event:
    {informational_object}
    """
    response = run_ragbot_prompt(prompt)
    expanded_result = response.split("```json")[1].split("```")[0]
    return expanded_result

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

if __name__ == "__main__":
    combined_news = prompt_news_crawler()  # Using RAGBot to fetch and format news.
    reddit = fetch_global_distress_news()  # Using existing method to fetch data.

    # Integrate and process data using RAGBot instead of OpenAI
    enriched_data = combine_data_with_speaker_summary_and_audio(combined_news)
    for data in enriched_data:
        print(f"Event: {data['event']}, Summary: {data['speaker_summary']}, Audio URL: {data['audio_url']}")
