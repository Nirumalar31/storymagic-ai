import os
import json
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app = Flask(__name__, static_folder=frontend_path, static_url_path="")
CORS(app)  # Allow cross-origin requests

# --------- Initialize AI & TTS Clients Safely ---------
HAS_OPENAI = False
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-openai-key-goes-here":
    try:
        import openai
        # Handle both old and new openai versions loosely
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            HAS_OPENAI = True
        except ImportError:
            openai.api_key = OPENAI_API_KEY
            client = openai
            HAS_OPENAI = True
    except ImportError:
        print("Warning: openai package not installed.")

HAS_GCP = False
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    try:
        from google.cloud import texttospeech
        HAS_GCP = True
        tts_client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"Warning: google-cloud-texttospeech initialization failed: {e}")

# ── Page Routes ─────────────────────────────────────────
@app.route("/")
def home():
    return send_from_directory(frontend_path, "index.html")

@app.route("/story")
def story_page():
    return send_from_directory(frontend_path, "story.html")

@app.route("/characters")
def characters_page():
    return send_from_directory(frontend_path, "characters.html")

@app.route("/parent")
def parent_page():
    return send_from_directory(frontend_path, "parent.html")

# ── API: Generate Story (OpenAI or Fallback) ────────────
@app.route("/generate-story", methods=["POST"])
def generate_story():
    data      = request.json or {}
    prompt    = data.get("prompt", "adventure")
    name      = data.get("name", "Explorer")
    theme     = data.get("theme", "land")
    character = data.get("character", "🧚")
    age       = data.get("age", "4-5")

    # If OpenAI is ready, try to generate dynamically
    if HAS_OPENAI:
        try:
            system_prompt = f"""
            You are a creative children's book author. Write a 5-page interactive story.
            Theme: {theme}
            Child Name: {name}
            Main Character Companion: {character} (Custom topic/prompt: {prompt})
            Target Audience Age: {age} years old.

            CRITICAL: Adjust your vocabulary, sentence complexity, and story depth to perfectly match a {age}-year-old child.
            - If Age 4-5: Use very simple words, short sentences, and highly repetitive, sensory-focused concepts.
            - If Age 6-7: Use early-reader vocabulary, minor problem solving, and short paragraphs.
            - If Age 8+: Use chapter-book vocabulary, more complex emotions, longer sentences, and deeper morals.
            
            Return ONLY valid JSON in the exact following structure with no markdown formatting:
            {{
              "title": "Story Title",
              "pages": [
                "Page 1 text...",
                "Page 2 text...",
                "Page 3 text...",
                "Page 4 text...",
                "Page 5 text..."
              ],
              "moral": "A 1-sentence moral lesson of the story.",
              "quiz": {{
                "q": "A simple question about the story?",
                "a": "The simple answer!"
              }}
            }}
            """
            
            # Use OpenAI
            if hasattr(client, 'chat'):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content
            else:
                # Fallback for old openai v0.28
                response = client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_prompt}],
                    temperature=0.7
                )
                content = response["choices"][0]["message"]["content"]
            
            # Clean JSON if wrapped in markdown
            content = content.replace('```json', '').replace('```', '').strip()
            story_payload = json.loads(content)
            story_payload["theme"] = theme
            story_payload["character"] = character
            story_payload["name"] = name
            return jsonify(story_payload)
            
        except Exception as e:
            print(f"OpenAI Generation Failed: {e}")
            # Fall through to hardcoded fallback if API fails
            pass

    # HARDCODED FALLBACK logic
    stories = {
        "jungle": {
            "title": f"{name} and the Jungle Mystery",
            "pages": [
                f"One sunny morning, {name} woke up to the sound of a faraway drumbeat. {character} was already at the door, wings fluttering with excitement. \"Today is the day we explore the Emerald Jungle!\" cried {name}.",
                f"Deep inside the jungle, the trees grew so tall they tickled the clouds. Bright parrots called out greetings, and tiny glowing fireflies danced around {name}'s head like a living crown.",
                f"Suddenly, a family of friendly monkeys swung down from the vines. \"We need your help!\" squeaked the smallest one. \"Our golden banana is missing, and the jungle spirit will fall asleep forever!\"",
                f"{name} thought carefully and remembered seeing a sparkle near the Waterfall of Wishes. Racing through ferns and over mossy rocks, they spotted it — the golden banana, glowing like a tiny sun!",
                f"With the golden banana returned, the jungle erupted in celebration! Flowers bloomed in brilliant colors, and the ancient jungle spirit smiled warmly. \"Thank you, brave {name},\" it whispered. \"The jungle will always be your friend.\""
            ],
            "moral": "Helping others brings joy to everyone.",
            "quiz": {"q": "What were the monkeys missing?", "a": "A golden banana!"}
        },
        "space": {
            "title": f"{name}'s Starlight Journey",
            "pages": [
                f"{name} was staring at the night sky when {character} appeared in a flash of light. 'Planet Zooble is in trouble — its seven moons have gone dark. You are the chosen star-keeper!'",
                f"The spaceship was made of shimmering moonbeams and smelled like cinnamon. Through the porthole, {name} saw nebulae in a thousand colors.",
                f"At Planet Zooble, cloud-like creatures called Blibblings floated sadly. 'Our moons ran away to hide,' said the Queen Blibbling, 'because they are afraid of the Shadow Comet.'",
                f"{name} had an idea — if the moons heard a lullaby, they would feel safe and return! {name} sang softly into the cosmic wind, and one by one, the seven moons crept out.",
                f"The Blibblings danced. The Queen placed a crown of starlight on {name}'s head. 'You have the bravest heart in the galaxy,' she declared."
            ],
            "moral": "Music and bravery can light up the darkest spaces.",
            "quiz": {"q": "What did the spaceship smell like?", "a": "Cinnamon!"}
        },
        "land": {
            "title": f"{name} and the Enchanted Kingdom",
            "pages": [
                f"A magical map fell from the sky and landed at {name}'s feet! {character} read aloud: 'Follow the silver road to the Enchanted Kingdom'. {name} didn't hesitate.",
                f"The silver road wound past talking flowers, over a bridge guarded by a riddle-loving troll, and through a forest where trees hummed lullabies.",
                f"The Kingdom's castle was made of moonstone. The Queen bowed low. 'Our kingdom is under a forgetting spell — soon we'll all forget how to be kind!'",
                f"{name} found the source: a grey stone tablet carved with one word: 'Remember.' {name} gathered everyone and told stories. Slowly, memory returned.",
                f"The spell shattered in golden confetti. The King declared {name} a Knight of Kindness. 'Kindness is the greatest magic,' he said."
            ],
            "moral": "Kindness is the greatest magic of all.",
            "quiz": {"q": "What was the castle made of?", "a": "Moonstone!"}
        }
    }

    # Use 'land' fallback if theme is missing from the limited mock dict
    story_data = stories.get(theme, stories["land"])
    
    return jsonify({
        "story":     story_data["pages"],
        "title":     story_data["title"],
        "theme":     theme,
        "character": character,
        "name":      name,
        "moral":     story_data.get("moral", "You did a fantastic job!"),
        "quiz":      story_data.get("quiz", None)
    })

# ── API: Google Cloud TTS ───────────────────────────────
@app.route("/api/tts", methods=["POST"])
def generate_tts():
    """Takes text, invokes Google Cloud TTS, returns an MP3."""
    if not HAS_GCP:
        return jsonify({"error": "Google Cloud TTS is not configured."}), 503

    data = request.json or {}
    text = data.get("text", "")
    voice_name = data.get("voice", "en-US-Journey-F") # Default journey friendly voice
    
    if not text:
        return jsonify({"error": "No text provided."}), 400

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9, # Slightly slower for kids
            pitch=2.0
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Return audio as binary response
        res = make_response(response.audio_content)
        res.headers.set('Content-Type', 'audio/mpeg')
        res.headers.set('Content-Disposition', 'attachment; filename="narration.mp3"')
        return res

    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({"error": str(e)}), 500

# ── API: Story Choices ──────────────────────────────────
@app.route("/story-choices", methods=["POST"])
def story_choices():
    data  = request.json or {}
    page  = data.get("page", 0)
    theme = data.get("theme", "land")


    choices_map = {
        "jungle": {2: [{"emoji": "🐒", "text": "Follow the monkeys"}, {"emoji": "🌺", "text": "Search the flowers"}]},
        "space": {2: [{"emoji": "🎵", "text": "Sing a lullaby"}, {"emoji": "🔦", "text": "Use the starlight torch"}]},
        "ocean": {2: [{"emoji": "🐠", "text": "Ask the rainbow fish"}, {"emoji": "🔮", "text": "Follow the trail of bubbles"}]},
        "dinosaur": {2: [{"emoji": "🦖", "text": "Roar back loudly"}, {"emoji": "🍃", "text": "Offer a giant leaf"}]},
        "kindness": {2: [{"emoji": "🤝", "text": "Help a new friend"}, {"emoji": "🎁", "text": "Give a small gift"}]},
        "superpower": {2: [{"emoji": "⚡", "text": "Use super speed"}, {"emoji": "🛡️", "text": "Create a shield"}]},
        "mystery": {2: [{"emoji": "🔍", "text": "Look for clues"}, {"emoji": "🚪", "text": "Open the secret door"}]},
    }

    # Generic fallback choices if theme doesn't have specific ones defined for this page
    default_choices = [{"emoji": "🌟", "text": "Try something brave"}, {"emoji": "✨", "text": "Use some magic"}]
    choices = choices_map.get(theme, {}).get(page, default_choices if page == 2 else [])
    return jsonify({"choices": choices})

if __name__ == "__main__":
    app.run(debug=True)