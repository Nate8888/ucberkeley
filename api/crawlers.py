from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        whole_text = ''
        for entry in transcript:
            whole_text += entry['text'] + ' '
        return whole_text
    except:
        return None

# test
video_ids = ['2koEujX9nEg', 'dQw4w9WgXcQ']
for video_id in video_ids:
    print(get_transcript(video_id))
    print("--------------------------------------------------")
