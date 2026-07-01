import os
import re

frontend_dir = r'c:\Users\USER\OneDrive\Documents\SEM 6\PSM2\ai_storybook\ai_storybook\frontend'

def standardize_footer():
    # The new polished footer HTML
    new_footer_html = """<!-- Global Footer -->
<footer class="pro-footer">
  <div class="footer-container">
    <div class="footer-brand">
      <img src="images/Logo.png" alt="StoryMagic Logo" class="footer-logo-img">
      <p>Making learning to read a magical, unforgettable <br> experience through personalized AI stories.</p>
      <div class="footer-socials">
        <a href="https://www.instagram.com/storymagic_ai?igsh=amZ4OW9lZWNyd21r&amp;utm_source=qr" target="_blank" class="footer-social-btn social-instagram" title="Instagram">
          <img src="images/instagram.webp" alt="Instagram" class="social-icon-img"/>
        </a>
        <a href="https://www.tiktok.com/@storymagic_ai?_r=1&amp;_t=ZS-95WrXclgNGr" target="_blank" class="footer-social-btn social-tiktok" title="TikTok">
          <img src="images/tik tok.webp" alt="TikTok" class="social-icon-img"/>
        </a>
        <a href="#" class="footer-social-btn social-youtube" title="YouTube">
          <img src="images/youtube.png" alt="YouTube" class="social-icon-img"/>
        </a>
        <a href="#" class="footer-social-btn social-linkedin" title="LinkedIn">
          <img src="images/linkedin.png" alt="LinkedIn" class="social-icon-img"/>
        </a>
      </div>
    </div>
    <div class="footer-links">
      <div class="footer-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="library.html">Library</a></li>
          <li><a href="characters.html">Characters</a></li>
          <li><a href="parent.html">Parents Dashboard</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Support</h4>
        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="contact.html">Contact Us</a></li>
          <li><a href="#">Privacy Policy</a></li>
          <li><a href="#">Terms of Service</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&copy; 2024 StoryMagic AI. All rights reserved. Created with ❤️ for young explorers.</p>
  </div>
</footer>"""

    footer_pattern = re.compile(r'<!-- Global Footer -->\s*<footer class="pro-footer">.*?</footer>', re.DOTALL)
    # If the comment is missing, we try to match just the footer tag with pro-footer class
    fallback_pattern = re.compile(r'<footer class="pro-footer">.*?</footer>', re.DOTALL)

    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(frontend_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = footer_pattern.sub(new_footer_html, content)
            if new_content == content:
                new_content = fallback_pattern.sub(new_footer_html, content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Standardized Footer for {filename}")

if __name__ == "__main__":
    standardize_footer()
