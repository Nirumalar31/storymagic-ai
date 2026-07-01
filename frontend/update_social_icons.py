import os
import glob
import re

dir_path = r'c:/Users/USER/OneDrive/Documents/SEM 6/PSM2/ai_storybook/ai_storybook/frontend'

FA_LINK = '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>\n</head>'

# New footer-socials block — proper brand icons with individual links
SOCIAL_BLOCK_OLD_INDEX = '''        <a href="https://www.instagram.com/storymagic_ai?igsh=amZ4OW9lZWNyd21r&amp;utm_source=qr" target="_blank" class="footer-social-btn">📱</a> <!-- Instagram -->
        <a href="#" class="footer-social-btn">💼</a> <!-- LinkedIn Placeholder -->
        <a href="#" class="footer-social-btn">▶️</a> <!-- YouTube Placeholder -->
        <a href="https://www.tiktok.com/@storymagic_ai?_r=1&amp;_t=ZS-95WrXclgNGr" target="_blank" class="footer-social-btn">🎵</a> <!-- TikTok -->'''

SOCIAL_BLOCK_NEW = '''        <a href="https://www.instagram.com/storymagic_ai?igsh=amZ4OW9lZWNyd21r&amp;utm_source=qr" target="_blank" class="footer-social-btn social-instagram" title="Instagram">
          <i class="fa-brands fa-instagram"></i>
        </a>
        <a href="https://www.tiktok.com/@storymagic_ai?_r=1&amp;_t=ZS-95WrXclgNGr" target="_blank" class="footer-social-btn social-tiktok" title="TikTok">
          <i class="fa-brands fa-tiktok"></i>
        </a>
        <a href="#" class="footer-social-btn social-youtube" title="YouTube">
          <i class="fa-brands fa-youtube"></i>
        </a>
        <a href="#" class="footer-social-btn social-linkedin" title="LinkedIn">
          <i class="fa-brands fa-linkedin-in"></i>
        </a>'''

for filepath in glob.glob(os.path.join(dir_path, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Inject Font Awesome if not already there
    if 'font-awesome' not in content:
        content = content.replace('</head>', FA_LINK)
        changed = True

    # For index.html which already has real links but old icons
    if SOCIAL_BLOCK_OLD_INDEX in content:
        content = content.replace(SOCIAL_BLOCK_OLD_INDEX, SOCIAL_BLOCK_NEW)
        changed = True
    else:
        # For other pages that still have emoji icons — do a regex replace on the entire footer-socials block
        pattern = r'<div class="footer-socials">.*?</div>'
        replacement = '''<div class="footer-socials">
        <a href="https://www.instagram.com/storymagic_ai?igsh=amZ4OW9lZWNyd21r&amp;utm_source=qr" target="_blank" class="footer-social-btn social-instagram" title="Instagram">
          <i class="fa-brands fa-instagram"></i>
        </a>
        <a href="https://www.tiktok.com/@storymagic_ai?_r=1&amp;_t=ZS-95WrXclgNGr" target="_blank" class="footer-social-btn social-tiktok" title="TikTok">
          <i class="fa-brands fa-tiktok"></i>
        </a>
        <a href="#" class="footer-social-btn social-youtube" title="YouTube">
          <i class="fa-brands fa-youtube"></i>
        </a>
        <a href="#" class="footer-social-btn social-linkedin" title="LinkedIn">
          <i class="fa-brands fa-linkedin-in"></i>
        </a>
      </div>'''
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {os.path.basename(filepath)}')
    else:
        print(f'SKIP: {os.path.basename(filepath)}')

print('\nDone!')
