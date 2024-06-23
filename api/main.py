from intelligence_agents import *  # Assuming this is the module with your functions
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
VOICE_API = os.getenv("VOICE_API")
OPENAI_API = os.getenv("OPENAI_API_KEY")
YOUTUBE_DATA_API = os.getenv("YOUTUBE_DATA_API")

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

# Global mem
news_combined = []
ytb_complete_search_combined = []
multi_subreddit_data_combined = []

def populate_comments(information_chain, commented_news):
    for chain in information_chain:
        for block in chain:
            block['comments'] = comment_augmentation(commented_news, block)

def populate_opps(information_chain):
    all_market_opps = []
    for chain in information_chain:
        for block in chain:
            market_opps = opportunity_is_knocking(block)
            all_market_opps.append(market_opps)
    return all_market_opps

def populate_impact(information_chain):
    for chain in information_chain:
        for block in chain:
            # Impact measurement by reference no need to return
            impact_measurement(block)

def populate_exposure(information_chain):
    for chain in information_chain:
        for block in chain:
            # Exposure measurement by reference no need to return
            exposure_measurer(block)


def pipeline_of_agents_tools():
    global news_combined, ytb_complete_search_combined, multi_subreddit_data_combined
    ytb_complete_search = youtube_search_and_transcript()
    news_articles = prompt_news_crawler()
    multi_subreddit_data = fetch_global_distress_news()
    populate_comments([news_combined, ytb_complete_search_combined], multi_subreddit_data_combined)
    ytb_complete_search_combined = combine_data_with_speaker_summary_and_audio(ytb_complete_search)
    news_combined = combine_data_with_speaker_summary_and_audio(news_articles)
    multi_subreddit_data_combined = combine_data_with_speaker_summary_and_audio(multi_subreddit_data)
    populate_impact([news_combined, ytb_complete_search_combined, multi_subreddit_data_combined])
    populate_exposure([news_combined, ytb_complete_search_combined, multi_subreddit_data_combined])

@app.route('/getAllData', methods=['GET'])
def get_all_data():
    pipeline_of_agents_tools()
    return jsonify([news_combined, ytb_complete_search_combined, multi_subreddit_data_combined])

@app.route('/allMarketOpps', methods=['GET'])
def get_all_market_opps():
    global news_combined, ytb_complete_search_combined, multi_subreddit_data_combined
    all_mkt_data = populate_opps([news_combined, ytb_complete_search_combined, multi_subreddit_data_combined])
    return jsonify(all_mkt_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)