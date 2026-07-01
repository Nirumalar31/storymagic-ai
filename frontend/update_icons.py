import os
import glob

dir_path = r'c:/Users/USER/OneDrive/Documents/SEM 6/PSM2/ai_storybook/ai_storybook/frontend'

fa_link = '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>\n</head>'

for filepath in glob.glob(os.path.join(dir_path, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject Font Awesome if not present
    if 'font-awesome' not in content:
        content = content.replace('</head>', fa_link)

    # Replace Emojis with Font Awesome Icons
    content = content.replace('>📱<', '><i class="fa-brands fa-instagram"></i><')
    content = content.replace('>💼<', '><i class="fa-brands fa-linkedin-in"></i><')
    content = content.replace('>▶️<', '><i class="fa-brands fa-youtube"></i><')
    content = content.replace('>🎵<', '><i class="fa-brands fa-tiktok"></i><')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Icons successfully replaced with Font Awesome!")
