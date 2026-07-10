# StoryMagic AI — PSM2 Final Year Project by Nirumalar Santharan, UTM
# PSM2 presentation completed on 10 July 2026. Alhamdulillah!

import os
import json
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

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

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
HAS_ELEVENLABS = bool(ELEVENLABS_API_KEY)

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

@app.route("/library")
def library_page():
    return send_from_directory(frontend_path, "library.html")

@app.route("/create")
def create_page():
    return send_from_directory(frontend_path, "create.html")

@app.route("/login")
def login_page():
    return send_from_directory(frontend_path, "login.html")

@app.route("/signup")
def signup_page():
    return send_from_directory(frontend_path, "signup.html")

# ── API: Generate Story (OpenAI or Fallback) ────────────
@app.route("/generate-story", methods=["POST"])
def generate_story():
    data      = request.json or {}
    prompt    = data.get("prompt", "adventure")
    name      = data.get("name", "Explorer")
    theme     = data.get("theme", "land")
    character = data.get("character", "")
    age       = data.get("age", "4-5")

    # Age-specific writing rules
    age_rules = {
        "4-5": """
AGE 4-5 RULES — STRICTLY FOLLOW EVERY POINT:

LANGUAGE:
- Use ONLY simple words a 4-year-old knows: go, big, small, happy, sad, run, jump, look, find, help, home, friend, warm, bright, funny, good, kind, play, share.
- Write like you are talking to a toddler. Keep it warm and playful.

SENTENCES:
- Every sentence: 5 to 8 words only. Short and easy to read aloud.
- GOOD: "Mia found a little lost bird."
- BAD: "Mia and Luna played together in the sunny park all afternoon." (TOO LONG)

STRUCTURE:
- Write EXACTLY 3 pages. EXACTLY 3 PAGES.
- EACH page MUST have EXACTLY 3 sentences. No exceptions.
- Page 1: Introduce the character and the setting.
- Page 2: A small problem or challenge appears.
- Page 3: The problem is solved and everyone is happy.
- Use fun sounds: "Boom!", "Splash!", "Wheee!"

STORY:
- Problem must be simple and solved in ONE kind act.
- Emotions: happy, sad, scared, surprised.

QUIZ: ask about something directly stated in the story — a colour, animal, or action.
MORAL: one very short sentence. Example: "Being kind feels good." """,

        "6-7": """
AGE 6-7 RULES — STRICTLY FOLLOW EVERY POINT:

LANGUAGE:
- Use words a Year 1–2 school child knows: brave, scared, treasure, magical, forest, discovered, excited, wonder, help, friend, dark, sparkle, secret.
- NEVER use: persevere, compassion, enormous complexity, philosophical ideas, long descriptions.
- Sentences should SOUND like an easy picture book read aloud.

SENTENCES:
- Each sentence: 10 to 14 words maximum.
- GOOD: "She felt a little scared, but she stepped forward anyway."
- BAD: "Despite her trepidation, she courageously proceeded into the unknown."

STRUCTURE:
- Write EXACTLY 3 pages. NOT 4. EXACTLY 3.
- EACH page MUST have EXACTLY 5 sentences. Count them — 1, 2, 3, 4, 5.
- Page 1: Introduce the character, setting and mood. 5 sentences.
- Page 2: A problem or challenge appears. Character tries to help. 5 sentences.
- Page 3: Problem is solved. Everyone feels happy and proud. 5 sentences.
- Include ONE fun surprise (a talking animal, a glowing door, a kind stranger).

EXAMPLE of a good page (5 sentences):
"{name} walked into the magical forest with {character} by their side. The trees were tall and sparkled with golden light. Suddenly, they heard a small cry from behind a big rock. A tiny rabbit was stuck in the mud, looking very scared. {name} smiled and said, I will help you!"

STORY:
- Clear beginning, middle, end.
- Emotions: excited, worried, brave, proud, relieved.

QUIZ: ask the child to remember one key thing that happened.
MORAL: a simple, clear friendship or kindness lesson in one sentence. """,

        "8": """
AGE 8+ RULES — STRICTLY FOLLOW EVERY POINT:

LANGUAGE:
- Use vocabulary a confident Year 3–4 reader knows: determined, mysterious, courage, doubt, realised, wondered, persevere, grateful, unexpected, challenge.
- Sentences can be longer and more varied — mix short punchy lines with longer descriptive ones.
- GOOD: "For a moment, {name} hesitated. The path ahead was dark and unfamiliar. But turning back was not an option."
- Avoid adult-level academic words: contemplated, juxtaposition, pursuant, ramification.

SENTENCES:
- Vary sentence length naturally for rhythm and tension.
- Each page: 6 to 9 sentences.

STRUCTURE:
- Write EXACTLY 3 pages. NOT 4. EXACTLY 3 pages.
- EACH page MUST have EXACTLY 6 sentences. Count them — 1, 2, 3, 4, 5, 6.
- Page 1: Set the scene and introduce the challenge.
- Page 2: The character struggles and tries different approaches.
- Page 3: The character succeeds and learns something.
- Include a real challenge that takes more than one try to solve.
- Show the character's inner thoughts and feelings — not just actions.
- Add a meaningful turning point or growth moment.

STORY WORLD — KEEP IT CHILD-SIZED:
- Set the story in a child's real or imaginative world: a lost or hurt animal, a new kid at school, learning a new skill (bike, swimming, a sport), a family pet, a magical creature, a treasure hunt.
- NEVER use adult professions, workplaces, scientific research papers, funding/business problems, or abstract philosophical mysteries. This is a story FOR a child, not ABOUT an adult's life.
- The challenge should be something a 7-8 year old would actually face or imagine facing.

STORY:
- Emotions: doubt, determination, gratitude, empathy, regret, hope.
- The character should LEARN something about themselves.

QUIZ: ask WHY the character made a decision — requires understanding, not just memory.
- Keep the question ONE short sentence and each answer option SHORT (3-7 words) — like a quick-pick choice, not a paragraph.
MORAL: a thoughtful 1–2 sentence lesson that makes the child think. """
    }

    rules = age_rules.get(age, age_rules["6-7"])

    # If OpenAI is ready, try to generate dynamically
    if HAS_OPENAI:
        try:
            system_prompt = f"""You are an expert children's book author who specialises in age-appropriate storytelling.

STORY DETAILS:
- Theme: {theme}
- Child's Name: {name}
- Character companion: {character}
- Custom prompt: {prompt}
- Target age: {age} years old

{rules}

CRITICAL: The "pages" array MUST have EXACTLY 3 items. No more, no less.
Each page must be real story content — do NOT copy the example structure or placeholder text.

Return ONLY valid JSON with NO markdown, NO code fences, NO extra text — just the raw JSON:
{{
  "title": "A real story title here",
  "pages": [
    "Full paragraph for Page 1 with 5 sentences of real story content.",
    "Full paragraph for Page 2 with 5 sentences continuing the story.",
    "Full paragraph for Page 3 with 5 sentences ending the story happily."
  ],
  "moral": "A real one-sentence lesson from this story.",
  "wrongMorals": [
    "A believable but wrong lesson",
    "Another believable but wrong lesson"
  ],
  "quiz": {{
    "q": "A question matching the age level above?",
    "a": "The correct answer",
    "wrong": [
      "Wrong answer 1",
      "Wrong answer 2",
      "Wrong answer 3"
    ]
  }}
}}"""
            
            # Use OpenAI
            if hasattr(client, 'chat'):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_prompt}],
                    temperature=0.8,
                    max_tokens=2500
                )
                content = response.choices[0].message.content
            else:
                # Fallback for old openai
                response = client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_prompt}],
                    temperature=0.8,
                    max_tokens=2500
                )
                content = response["choices"][0]["message"]["content"]

            # Clean JSON if wrapped in markdown
            content = content.replace('```json', '').replace('```', '').strip()
            story_payload = json.loads(content)

            # Keep only real pages — skip exact placeholder strings
            if 'pages' in story_payload and isinstance(story_payload['pages'], list):
                PLACEHOLDERS = {'page 1 text here', 'page 2 text here', 'page 3 text here',
                                'full paragraph for page 1', 'full paragraph for page 2', 'full paragraph for page 3'}
                real_pages = [p for p in story_payload['pages']
                              if isinstance(p, str) and p.strip().lower() not in PLACEHOLDERS]
                if real_pages:
                    story_payload['pages'] = real_pages[:3]

            story_payload["theme"] = theme
            story_payload["character"] = character
            story_payload["name"] = name
            print(f"OpenAI story generated OK — {len(story_payload.get('pages', []))} pages")
            return jsonify(story_payload)

        except Exception as e:
            print(f"OpenAI Generation Failed: {e}")
            # Fall through to hardcoded fallback if API fails
            pass

    # HARDCODED FALLBACK — age-aware AND theme-aware
    fallbacks = {
        "forest": {
            "4-5": {
                "title": f"{name} in the Magic Forest",
                "pages": [
                    f"{name} walked into the big green forest. {character} hopped along too! The trees were tall and the flowers were bright. \"I love it here!\" said {name}.",
                    f"A little bunny sat by a tree crying. \"I can't find my home!\" it said. {name} felt sorry for the bunny. \"We will help you find it!\" said {character}.",
                    f"They walked slowly and looked around. They found a cosy burrow under a big oak tree. \"That's it!\" cried the bunny. {name} gave the bunny a warm hug. Everyone was so happy!"
                ],
                "moral": "Helping a friend find their way home is a wonderful act of kindness!",
                "wrongMorals": ["It is best to stay home and not help.", "Only grown-ups can help lost animals."],
                "quiz": {"q": f"Who did {name} help in the forest?", "a": "A lost bunny!", "wrong": ["A big bear", "A green frog", "A red bird"]}
            },
            "6-7": {
                "title": f"{name} and the Magical Compass",
                "pages": [
                    f"One sunny morning, {name} discovered a glowing compass hidden under the old oak tree. When touched, the world dissolved into golden leaves — {name} was standing at the edge of the Magical Forest. {character} popped out of a hollow log, ready for adventure.",
                    f"The compass pointed to a sparkling river where a sad little mushroom sat on a rock. \"The flood swept away my bridge parts!\" it cried. \"I need to reach the giant treehouse.\"",
                    f"{name} gathered flat stones and sturdy sticks. With {character}'s encouragement, they rebuilt the bridge piece by piece. The mushroom cheered and offered a glowing acorn as thanks!",
                    f"Inside the giant treehouse, a wise old owl awaited. \"You showed real empathy today,\" it said. \"You are a true Forest Explorer.\" {name} beamed with pride all the way home."
                ],
                "moral": "Helping others in need is the best way to make new friends and find real adventures!",
                "wrongMorals": ["It is better to let others solve their own problems.", "Real explorers always work alone."],
                "quiz": {"q": f"What did {name} rebuild for the mushroom?", "a": "A bridge!", "wrong": ["A house", "A boat", "A ladder"]}
            },
            "8": {
                "title": f"{name} and the Lost Baby Owl",
                "pages": [
                    f"After a stormy night, {name} and {character} were exploring the forest when they heard a small, frightened hoot from under a fallen branch. A baby owl sat alone, his nest knocked down by the wind. \"I can't find my way home,\" he sniffled, feathers all ruffled. {name} knelt down and promised to help, even though the branch above was much too high to reach.",
                    f"The first idea was to lift the owl back up using a loop of rope, but the branch was too high and the owl was too scared to be pulled. A flicker of doubt crept in — what if this couldn't be fixed? So {name} tried something new instead: weaving a brand new nest from twigs and soft moss on a lower branch. It looked perfect — until the wind blew it apart before it was finished. {name} almost gave up, but the owl's hopeful eyes were enough to make {name} try once more, weaving the twigs in tighter this time.",
                    f"A family of squirrels noticed the trouble and tucked extra leaves between the branches to help it hold. At last the new nest stayed put. The baby owl hopped in, fluffed his wings, and let out the softest, happiest hoot {name} had ever heard. Walking home that evening, {name} felt proud — not because the plan had worked first time, but because it hadn't, and {name} had kept trying anyway. Asking for help, {name} realised, wasn't giving up. It was just being smart."
                ],
                "moral": "Trying again — and asking for help when you need it — is what turns a hard problem into a happy ending.",
                "wrongMorals": ["Asking for help means you have failed.", "If a plan doesn't work the first time, it's better to stop trying."],
                "quiz": {"q": f"Why did {name} keep trying to build the nest?", "a": "So the owl wouldn't be without a home.", "wrong": ["There was a prize for finishing", "The owl flew away forever", "A grown-up said so"]}
            }
        },
        "ocean": {
            "4-5": {
                "title": f"{name} Under the Sea",
                "pages": [
                    f"{name} put on blue flippers and jumped into the warm, clear sea. {character} swam right beside them. They saw pretty orange fish and a big purple crab. \"It is so beautiful!\" said {name}.",
                    f"A tiny starfish was crying on a pink rock. \"I am lost! I cannot find my coral home!\" it said. \"Don't worry,\" said {name}. \"We will find it for you!\"",
                    f"They swam slowly and looked all around. There! A big purple coral home! \"That's it!\" cheered the starfish. All the sea friends clapped their fins. {name} smiled the biggest smile!"
                ],
                "moral": "Helping a friend find their way home is the kindest thing in the world!",
                "wrongMorals": ["Sea creatures don't need help from anyone.", "The sea is too scary to swim in."],
                "quiz": {"q": "Who needed help finding their home?", "a": "A little starfish!", "wrong": ["A blue whale", "A red crab", "A green turtle"]}
            },
            "6-7": {
                "title": f"{name} and the Underwater Kingdom Quest",
                "pages": [
                    f"While playing near the water, {name} found a magical seashell. Whispering the secret word, {name} and {character} were suddenly diving deep into a breathtaking, glowing Underwater Kingdom!",
                    f"A young mermaid swam over quickly. \"The Ocean's Heartlight has gone dark! We need brave explorers to find the magical pearls in the glowing trenches!\"",
                    f"It was dark in the trench, and {name} felt a little scared. But taking a deep breath, they swam bravely down, befriending a glowing sea turtle who guided their way.",
                    f"Deep in the coral cave, they found the missing pearls. The Heartlight blazed brilliantly, flooding the ocean with colour. The mermaid awarded {name} with an Honorary Explorer Badge."
                ],
                "moral": "Courage isn't not being scared — it's doing the brave thing even when you are!",
                "wrongMorals": ["The ocean should be left alone and never explored.", "Brave explorers never feel scared."],
                "quiz": {"q": "Which animal guided you through the dark trench?", "a": "A glowing sea turtle!", "wrong": ["A friendly dolphin", "A wise octopus", "A tiny clownfish"]}
            },
            "8": {
                "title": f"{name} and the Tangled Dolphin",
                "pages": [
                    f"{name} and {character} were snorkelling near the reef when they spotted a young dolphin thrashing weakly, its fin caught in a clump of old fishing net. Panic flashed in its dark eyes. {name}'s heart pounded — this felt bigger than anything they'd handled before.",
                    f"The first attempt to tug the net loose only tightened it further, and the dolphin let out a frightened squeak. {name} pulled back, frustrated and unsure, wondering for a moment if they were doing more harm than good. Taking a slow breath, {name} remembered something from a nature show — staying calm helps a scared animal trust you. {name} floated quietly nearby until the dolphin's breathing settled, then worked one loop of net free at a time instead of pulling all at once.",
                    f"It took three more careful tries, inch by patient inch, before the last loop finally slipped away. The dolphin shot upward for a joyful breath, circled {name} once, then leapt high into the sunlight before swimming off to find its pod. Floating back to shore, {name} felt shaky but full of quiet pride. Helping hadn't been about being strong. It had been about being patient enough to get it right."
                ],
                "moral": "Real courage is staying calm and patient, even when the first try doesn't work.",
                "wrongMorals": ["The fastest solution is always the best one.", "Wild animals should always be left completely alone, even when they're in danger."],
                "quiz": {"q": f"Why did {name} stop pulling so hard?", "a": "Pulling hard scared the dolphin.", "wrong": ["The net was just seaweed", "It was time to go home", f"{name} got too tired"]}
            }
        },
        "kindness": {
            "4-5": {
                "title": f"{name}'s Kind Day",
                "pages": [
                    f"{name} and {character} went to the park. They saw a small girl standing alone. She looked very sad. \"What is wrong?\" asked {name} in a kind, soft voice.",
                    f"\"I dropped my ice cream and now I have none,\" said the girl. {name} thought for a moment, then shared their own ice cream! \"Here — have some of mine!\" The girl's face lit up like sunshine.",
                    f"They played together on the swings all afternoon. They laughed and laughed. When it was time to go home, {name} felt warm and happy inside. Being kind really does feel wonderful!"
                ],
                "moral": "Sharing what you have makes both you and your new friend smile!",
                "wrongMorals": ["It is best to keep treats all for yourself.", "You should never talk to strangers."],
                "quiz": {"q": f"What did {name} share with the sad girl?", "a": "Their ice cream!", "wrong": ["A ball", "A sticker", "A flower"]}
            },
            "6-7": {
                "title": f"{name} and the Kindness Treasure Hunt",
                "pages": [
                    f"The mayor called upon {name} and {character} for a very special mission — the Kindness Treasure Hunt! \"Find the three hidden Kindness Gems scattered around our town!\"",
                    f"At the library, a child couldn't reach a book on the top shelf. {name} helped without being asked, and ping! A glowing blue Kindness Gem appeared in their hand.",
                    f"At the playground, two friends were arguing over a swing. {name} calmly suggested they take turns. They agreed and laughed together. Ping! A pink Kindness Gem appeared!",
                    f"{name} shared their sandwich with a hungry stray cat. The golden Kindness Gem appeared. \"You see,\" smiled the mayor, \"the treasure was in your heart all along!\""
                ],
                "moral": "Kindness is the greatest treasure, and sharing it makes everyone richer!",
                "wrongMorals": ["Winning the hunt matters more than how you act along the way.", "Only grown-ups can perform real acts of kindness."],
                "quiz": {"q": f"How did {name} earn the pink gem?", "a": "By helping two friends share the swing fairly!", "wrong": ["By finding it buried under a tree", "By buying it from the shopkeeper", "By solving a very difficult puzzle"]}
            },
            "8": {
                "title": f"{name} and the Quiet New Kid",
                "pages": [
                    f"A new student named Theo joined {name}'s class, sitting alone at lunch every single day. {name} wanted to say hello but felt a strange flutter of nerves — what if Theo didn't want to talk?",
                    f"{name}'s first attempt was a loud, cheerful \"Hey, wanna sit with us?\" shouted across the cafeteria. Theo flinched and shook his head quickly, ducking behind his book. {name} felt a small sting of regret — that hadn't gone the way it was supposed to. Instead of giving up, {name} quietly noticed that Theo always doodled dragons in the corner of his notebook.",
                    f"The next day, {name} sat down nearby — not too close — and asked softly, \"Did you draw that dragon? It looks awesome.\" Theo's face lit up for the first time all week, and soon they were both laughing over silly dragon names. Walking home, {name} realised the loud, easy way hadn't worked — but the slower, gentler way had."
                ],
                "moral": "Kindness works best when you take the time to notice what someone really needs, instead of guessing.",
                "wrongMorals": ["If someone doesn't want to be friends right away, you should stop trying immediately.", "Being the loudest and most outgoing person always makes others feel comfortable."],
                "quiz": {"q": "Why did the second try work better?", "a": "It noticed what Theo liked.", "wrong": ["A teacher assigned them", "Theo got a gift", "It was louder"]}
            }
        },
        "dinosaur": {
            "4-5": {
                "title": f"{name} Meets Rex!",
                "pages": [
                    f"{name} looked out the window and saw something amazing — a little green dinosaur in the garden! \"Hello! I am Rex!\" said the tiny dino. He had big round eyes and a tiny tail. \"Hello, Rex!\" said {name} with a big smile.",
                    f"Rex had lost his favourite red ball. His bottom lip wobbled. \"I can't find it anywhere!\" he said sadly. \"Don't worry, Rex,\" said {name}. \"We will all look together!\" said {character}.",
                    f"They looked under the flowers. They looked behind the big rock. There it was — the red ball! \"Hooray!\" shouted Rex. He did a happy little dinosaur dance! {name} laughed. New friends are truly the very best!"
                ],
                "moral": "Looking for something together is always better than looking alone!",
                "wrongMorals": ["Dinosaurs are too scary to ever talk to.", "Lost things can never be found once lost."],
                "quiz": {"q": "What did Rex lose?", "a": "His favourite red ball!", "wrong": ["His green hat", "His yummy lunch", "His toy rocket"]}
            },
            "6-7": {
                "title": f"{name} and the Friendly T-Rex",
                "pages": [
                    f"\"ROAARR!\" {name} jumped. The backyard had turned into a prehistoric jungle! A tiny green T-Rex named Rex sat eating cookies from a picnic basket. \"I lost my bouncy ball in the Volcano of Bubbles. Help?\"",
                    f"They hiked past sleeping triceratops and giant pterodactyls soaring overhead. The volcano bubbled with rainbow soapy bubbles instead of lava! {name} used a giant palm leaf as a fan to blow them aside.",
                    f"There was the shiny red ball! Rex was so happy he wiggled his tiny arms and did a full dinosaur dance. He shared his last cookie with {name} as a heartfelt thank-you.",
                    f"\"You're the best friend a dinosaur could have,\" Rex said warmly. {name} realised that even the most fearsome-looking creatures just want someone to play with."
                ],
                "moral": "Appearances can be deceiving — the most fearsome-looking creatures often just need a good friend!",
                "wrongMorals": ["Dinosaurs belong only in museums and should never be approached.", "Large scary creatures are always dangerous and must be avoided."],
                "quiz": {"q": "What came out of the volcano instead of lava?", "a": "Colourful rainbow bubbles!", "wrong": ["Hot white steam", "Glowing lava rocks", "Bright coloured confetti"]}
            },
            "8": {
                "title": f"{name} and the Littlest Triceratops",
                "pages": [
                    f"While exploring a hidden valley behind the old quarry, {name} and {character} found a baby triceratops stumbling alone through the ferns, calling out in small, worried grunts. Its family was nowhere in sight.",
                    f"{name}'s first plan was to follow the baby's trail of footprints backward, but the prints vanished at a rocky stream where the current had washed them away. {name} stood there unsure, the baby dinosaur nudging anxiously at their leg. Thinking harder, {name} noticed the baby kept turning toward a low rumbling sound in the distance — could that be its herd? Wading carefully across the stream, {name} followed the sound instead, even though it meant heading somewhere unfamiliar.",
                    f"Past a ridge of tall rocks, an entire herd of triceratops looked up sharply as the baby broke into an excited trot toward them. Its mother rumbled low with relief and curled protectively around her baby. Walking home, {name} realised the footprints hadn't been the only clue — sometimes you have to trust a different kind of evidence, and be brave enough to go somewhere new to find the answer."
                ],
                "moral": "When your first plan doesn't work, look for a new kind of clue instead of giving up.",
                "wrongMorals": ["If you can't find footprints, there's no way to track anything.", "Wild animals always find their own way home without any help."],
                "quiz": {"q": f"Why did {name} follow the rumbling sound?", "a": "The footprints had washed away.", "wrong": ["The footprints led in circles", "The dinosaur gave directions", "It heard treasure nearby"]}
            }
        },
        "mystery": {
            "4-5": {
                "title": f"{name}'s Mystery Box",
                "pages": [
                    f"{name} found a little box tied with a golden ribbon. \"What is inside?\" said {name}. {character} shook it gently — rattle, rattle! \"Let's open it right now!\" they said together. Inside was a tiny rolled-up map!",
                    f"The map had a big red X on it. \"That's a treasure map!\" shouted {name}. They ran outside as fast as they could. The X was right under the big apple tree in the garden!",
                    f"Buried under the tree was a jar full of sparkly gold and silver stones. \"Treasure!\" laughed {name}. {character} did a big happy dance. They shared the stones with all their friends. Everyone was so glad!"
                ],
                "moral": "The best treasure is the kind you can share with everyone around you!",
                "wrongMorals": ["Treasure should always be kept secret and never shared.", "Maps are only for grown-ups to understand."],
                "quiz": {"q": "Where was the treasure hidden?", "a": "Under the apple tree!", "wrong": ["In the attic", "Behind the garden shed", "Under the kitchen floor"]}
            },
            "6-7": {
                "title": f"{name} and the Great Mystery Box",
                "pages": [
                    f"{name} found a glowing box that said: \"DO NOT OPEN UNLESS YOU LIKE SILLY THINGS.\" Of course, {name} and {character} opened it. Whoosh! They landed on a cloud of pink cotton candy where a dog in a top hat trotted over. \"Welcome to Sillyville!\"",
                    f"Suddenly a giant flying pancake swooped past and stole the dog's top hat. \"Oh no, my formal wear!\" the dog cried. {name} spotted a marshmallow springboard nearby.",
                    f"{name} bounced high, grabbed the hat, and returned it. The pancake apologised — it just wanted to look smart. {name} suggested it share the hat on alternate days. Everyone agreed.",
                    f"The dog gave {name} a shiny golden jellybean as a reward. \"You saved the day and found a solution for the pancake too!\" The very best adventures really are the wonderfully silly ones."
                ],
                "moral": "Bravery and creative thinking can turn any silly problem into a happy solution for everyone!",
                "wrongMorals": ["Silly problems aren't worth solving properly.", "The fastest solution is always the best solution."],
                "quiz": {"q": "What stole the dog's top hat?", "a": "A giant flying pancake!", "wrong": ["A cheeky monkey", "A runaway balloon", "A mischievous cloud"]}
            },
            "8": {
                "title": f"{name} and the Box with Three Locks",
                "pages": [
                    f"In the dusty attic of their grandmother's house, {name} and {character} found an old wooden box with three strange locks and a note that read: \"Only those who are patient may open me.\" The first lock looked like a simple latch, but {name} tugged too hard and it snapped shut even tighter. Frustration bubbled up — why would anyone make something this confusing?",
                    f"Looking closer, {name} noticed tiny symbols carved beside each lock: a sun, a moon, and a star. Turning the first lock toward the sun symbol clicked it open easily. Encouraged, {name} tried turning the second lock toward the moon — but it wouldn't budge until it was turned the opposite way first. The third lock was the trickiest of all, needing both other locks held open at once while {name} twisted it toward the star.",
                    f"It took four tries and a lot of patient breathing before — click — the lid finally lifted. Inside wasn't treasure at all, but a faded letter from {name}'s great-grandmother, full of kind words for whoever found it. {name} smiled, understanding now why the box had asked for patience instead of strength."
                ],
                "moral": "Some of the best things in life can't be rushed — they ask for patience instead of force.",
                "wrongMorals": ["If something is locked, it's always better to force it open quickly.", "Old things found in attics are never worth the effort to understand."],
                "quiz": {"q": f"Why couldn't {name} open the third lock right away?", "a": "It needed the other two locks held open.", "wrong": ["The box was empty", "The lock was broken", "The key was hidden elsewhere"]}
            }
        },
        "moral": {
            "4-5": {
                "title": f"{name} Tries Again",
                "pages": [
                    f"{name} was trying to build a very tall tower with coloured blocks. But — crash! It fell down! {name} felt like crying. \"Don't give up!\" said {character} kindly. \"Try one more time!\"",
                    f"{name} took a big breath and tried again. Crash! It fell again! But {name} did not stop. This time they put the biggest blocks at the very bottom and the smallest ones at the top.",
                    f"The tower went up and up and up — and it stayed! \"I DID IT!\" shouted {name}, jumping up and down. {character} gave {name} a great big hug. Trying again is always, always worth it!"
                ],
                "moral": "Every time you try again, you get a little bit stronger and a little bit wiser!",
                "wrongMorals": ["If something falls down, it means you should stop and give up.", "Only perfect people get to feel proud."],
                "quiz": {"q": f"What did {name} build with the coloured blocks?", "a": "A tall tower!", "wrong": ["A bridge", "A sandcastle", "A little house"]}
            },
            "6-7": {
                "title": f"Luna Learns to Try Again",
                "pages": [
                    f"{name} and {character} were at the Grand Sparkle Talent Show when they met Luna. She desperately wanted to perform her magic dance but kept falling. \"It's okay to fall,\" {name} said gently. \"The important thing is to get back up and try again.\"",
                    f"{name} offered to practise the dance with Luna, counting the steps aloud. They practised by the stream, under the oak tree, and even when it became difficult. Every time Luna fell, {name} cheered her back up.",
                    f"When the talent show began, Luna stumbled once on stage — but she remembered {name}'s words, stood straight up, and finished with a spectacular magical spin that made the lights flash gold.",
                    f"The crowd roared with applause. Luna gave {name} a huge hug. \"Thank you for believing in me.\" They both learned that the real magic isn't the perfect performance — it's the courage to keep going."
                ],
                "moral": "Mistakes are how we learn — the real magic happens when we get back up and try again!",
                "wrongMorals": ["If something is truly difficult, it probably just isn't meant for you.", "Real talent means never making mistakes in public."],
                "quiz": {"q": "What was Luna trying to perform at the Talent Show?", "a": "A magic dance!", "wrong": ["A song about the stars", "A juggling routine", "A poem she had written"]}
            },
            "8": {
                "title": f"{name} and the Wobbly Wheels",
                "pages": [
                    f"{name} had begged for a bicycle all year, but the first time sitting on it, the wheels wobbled wildly and {name} tumbled into the grass within seconds. Cheeks burning, {name} glanced around to check if anyone had seen.",
                    f"{character} cheered from the sidewalk, \"That was a great first try!\" {name} wasn't so sure — five more attempts ended in five more tumbles, and a small voice inside whispered that maybe biking just wasn't for {name}. On the seventh try, {name} noticed something — looking down at the wobbling front wheel made things worse, but looking straight ahead at the mailbox down the street kept things steadier.",
                    f"By the tenth attempt, {name} wasn't thinking about falling anymore, just pedalling faster and faster, hair streaming back, laughing out loud at how the wind felt rushing past. That evening, {name} realised the falling hadn't been the failure. Quitting after the first tumble would have been."
                ],
                "moral": "Every attempt — even the wobbly, falling-down ones — teaches you something that gets you closer to succeeding.",
                "wrongMorals": ["If you fall down on your first try, it means you're not good at something.", "Only naturally talented people are able to learn new skills."],
                "quiz": {"q": f"What helped {name} finally ride well?", "a": "Looking ahead instead of down.", "wrong": ["Pure luck", "A different, easier bike", "Someone held it steady"]}
            }
        }
    }

    theme_stories = fallbacks.get(theme, fallbacks["forest"])
    fallback_data  = theme_stories.get(age, theme_stories.get("6-7", list(theme_stories.values())[0]))

    return jsonify({
        "story":       fallback_data["pages"],
        "title":       fallback_data["title"],
        "theme":       theme,
        "character":   character,
        "name":        name,
        "age":         age,
        "moral":       fallback_data["moral"],
        "wrongMorals": fallback_data["wrongMorals"],
        "quiz":        fallback_data["quiz"]
    })

# ── API: Google Cloud TTS ───────────────────────────────
@app.route("/api/tts", methods=["POST"])
def generate_tts():
    """Takes text, invokes Google Cloud TTS, returns an MP3."""
    if not HAS_GCP:
        return jsonify({"error": "Google Cloud TTS is not configured."}), 503

    data = request.json or {}
    text = data.get("text", "")
    voice_name = data.get("voice", "en-US-Journey-F")
    
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
            speaking_rate=0.9,
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

# ── API: ElevenLabs TTS ─────────────────────────────────
@app.route("/api/elevenlabs-tts", methods=["POST"])
def elevenlabs_tts():
    if not HAS_ELEVENLABS:
        return jsonify({"error": "ElevenLabs API key not configured."}), 503

    data    = request.json or {}
    text    = data.get("text", "")
    voice_id = data.get("voice_id", "EXAVITQu4vr4xnSDxMaL")  # Bella default

    if not text:
        return jsonify({"error": "No text provided."}), 400

    try:
        import urllib.request as urlreq
        import urllib.error

        payload = json.dumps({
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.80,
                "style": 0.20,
                "use_speaker_boost": True,
                "speed": 0.88
            }
        }).encode("utf-8")

        req = urlreq.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            data=payload,
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
        )
        with urlreq.urlopen(req, timeout=15) as resp:
            audio_bytes = resp.read()

        res = make_response(audio_bytes)
        res.headers.set("Content-Type", "audio/mpeg")
        return res

    except Exception as e:
        print(f"ElevenLabs TTS Error: {e}")
        return jsonify({"error": str(e)}), 500

# ── API: Story Choices ──────────────────────────────────
@app.route("/story-choices", methods=["POST"])
def story_choices():
    data  = request.json or {}
    page  = data.get("page", 0)
    theme = data.get("theme", "land")


    choices_map = {
        "jungle": {2: [{"emoji": "🐒", "text": "Follow the monkeys"}, {"emoji": "🌺", "text": "Search the flowers"}]},
        "ocean": {2: [{"emoji": "🐠", "text": "Ask the rainbow fish"}, {"emoji": "🔮", "text": "Follow the trail of bubbles"}]},
        "dinosaur": {2: [{"emoji": "🦖", "text": "Roar back loudly"}, {"emoji": "🍃", "text": "Offer a giant leaf"}]},
        "kindness": {2: [{"emoji": "🤝", "text": "Help a new friend"}, {"emoji": "🎁", "text": "Give a small gift"}]},
        "mystery": {2: [{"emoji": "🔍", "text": "Look for clues"}, {"emoji": "🚪", "text": "Open the secret door"}]},
    }

    # Generic fallback choices if theme doesn't have specific ones defined for this page
    default_choices = [{"emoji": "🌟", "text": "Try something brave"}, {"emoji": "✨", "text": "Use some magic"}]
    choices = choices_map.get(theme, {}).get(page, default_choices if page == 2 else [])
    return jsonify({"choices": choices})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)