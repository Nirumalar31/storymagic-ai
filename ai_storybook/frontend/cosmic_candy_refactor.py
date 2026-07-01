import os
import re

frontend_dir = r'c:\Users\USER\OneDrive\Documents\SEM 6\PSM2\ai_storybook\ai_storybook\frontend'

def refactor_html_for_cosmic_candy():
    # 1. Standardize page-wrapper (remove inline padding)
    # 2. Clean up Hero/Console in index.html
    # 3. Ensure no residual inline styles where the CSS class should handle it.

    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(frontend_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove inline padding from page-wrapper
            new_content = re.sub(r'<div class="page-wrapper" style="padding-top: \d+px;.*?>', 
                                 '<div class="page-wrapper">', content)
            
            # Simple wrapper replacement if no other styles
            new_content = re.sub(r'<div class="page-wrapper" style="padding-top: \d+px;">', 
                                 '<div class="page-wrapper">', new_content)

            # Special cleaning for index.html
            if filename == 'index.html':
                # Remove inline padding/styling from Magic Console
                new_content = new_content.replace('<div id="createSection" class="magic-console jelly-hover" style="animation:none;">', 
                                              '<div id="createSection" class="magic-console jelly-hover">')
                
                # Cleanup and neaten the age-grid/theme-grid inline styles
                new_content = re.sub(r'style="grid-template-columns: repeat\(4, 1fr\);"', '', new_content)
                new_content = re.sub(r'style="border-radius:16px;"', '', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Refactored {filename} to Cosmic Candy structure.")

if __name__ == "__main__":
    refactor_html_for_cosmic_candy()
