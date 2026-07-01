import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire hero div using regex
pattern = r'<!-- Main Content Dreamy Hero -->.*?</div>\s*\n\s*\n<!-- Story Creation Console'
new_hero = '''<!-- Main Content Dreamy Hero -->
<div class="dreamy-hero">

  <div class="hero-badge-new">\u2728 AI-Powered Storytelling for Kids</div>

  <h1 class="dreamy-title hero-main-title">
    Discover <span class="hero-gradient-word">Magical Stories</span>
    Created Just for Your Child
  </h1>

  <p class="hero-subtitle-new">Every adventure is unique, safe &amp; made just for your little explorer.<br>Choose a hero, pick a world, and let the magic begin!</p>

  <div class="dreamy-hero-buttons">
    <a href="#createSection" class="btn dreamy-btn-pink jelly-hover hero-cta-btn">\U0001fa84 Start Story</a>
    <a href="signup.html" class="btn hero-ghost-btn jelly-hover">Join Free \u2192</a>
  </div>

  <div class="dreamy-feature-bar">
    <span class="feature-pill fp-green">\u2728 Interactive Adventures</span>
    <span class="feature-pill fp-yellow">\U0001f31f Personalized Learning</span>
    <span class="feature-pill fp-blue">\U0001f6e1\ufe0f Safe &amp; Kid Friendly</span>
  </div>

</div>

<!-- Story Creation Console'''

result = re.sub(pattern, new_hero, content, flags=re.DOTALL)

if result != content:
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(result)
    print('SUCCESS - Hero section replaced')
else:
    print('PATTERN NOT MATCHED')
    # Debug: show line 35-48
    lines = content.splitlines()
    for i, l in enumerate(lines[33:50], 34):
        print(f'{i}: {repr(l)}')
