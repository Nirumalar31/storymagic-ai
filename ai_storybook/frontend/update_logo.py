import os

# Directory containing the HTML files
frontend_dir = r'c:\Users\USER\OneDrive\Documents\SEM 6\PSM2\ai_storybook\ai_storybook\frontend'

def revert_logo_extension():
    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(frontend_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Revert Logo filename to .webp
            new_content = content.replace('Logo.png', 'Logo.webp')

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Reverted {filename}")
            else:
                print(f"No changes needed for {filename}")

if __name__ == "__main__":
    revert_logo_extension()
