from gtts import gTTS
import base64
import io

def text_to_base64_audio(text):
    # Convert text to speech
    tts = gTTS(text)
    
    # Create a BytesIO object to hold the audio data
    audio_bytes = io.BytesIO()
    
    # Save the audio data to the BytesIO object
    tts.write_to_fp(audio_bytes)
    
    # Get the binary audio data from the BytesIO object
    audio_bytes.seek(0)
    audio_data = audio_bytes.read()
    
    # Encode the binary audio data to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return audio_base64

# Example usage
text = "Hello, this is a test."
base64_audio = text_to_base64_audio(text)
print(base64_audio)