import os
import re

frontend_dir = r'c:\Users\USER\OneDrive\Documents\SEM 6\PSM2\ai_storybook\ai_storybook\frontend'

# Clean up any duplicate comments and standardize the nav
def clean_and_normalize_nav():
    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(frontend_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove multiple instances of the comment if they exist
            content = re.sub(r'<!-- Unified Floating Nav -->\s*', '', content)
            content = re.sub(r'<!-- Navigation Header -->\s*', '', content)
            
            # The pattern to find any existing nav and replace it
            nav_pattern = re.compile(r'<nav class="nav-pill">.*?</nav>', re.DOTALL)
            
            new_nav_html = """  <!-- Navigation Header -->
  <nav class="nav-pill">
    <a href="index.html" class="nav-pill-logo">
      <img src="images/Logo.png" alt="StoryMagic Logo" class="nav-logo-img">
    </a>
    <div class="nav-pill-links">
      <a href="index.html">Home</a>
      <a href="characters.html">Characters</a>
      <a href="parent.html">Parents</a>
    </div>
    <div class="nav-pill-auth">
      <!-- Logic in auth.js will fill this -->
    </div>
  </nav>"""

            new_content = nav_pattern.sub(new_nav_html, content)
            
            # Normalize page-wrapper padding
            new_content = re.sub(r'<div class="page-wrapper" style="padding-top: \d+px;">', 
                                 '<div class="page-wrapper" style="padding-top: 130px;">', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Cleaned and Normalized {filename}")

if __name__ == "__main__":
    clean_and_normalize_nav()
