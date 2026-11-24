# SaveClip

Flask + yt-dlp + ffmpeg. One service serves the site and the API.

## Deploy on Hugging Face Spaces (free)
1. Create a Space, SDK = Docker.
2. Add this line at the very top of README.md: a YAML block with `sdk: docker` and `app_port: 7860` between `---` lines.
3. Upload all files in this folder. It builds and runs automatically.

## Deploy on Render (free)
New Web Service -> connect your GitHub repo with these files -> Runtime: Docker -> Free plan. Free services sleep after inactivity.

## Before launch
- Replace YOUR-EMAIL@example.com in static/legal.html.
- Paste your ad script in static/index.html (marked comments). Keep ads beside the buttons, never on them.
- Tune with env vars: MAX_JOBS (default 2), LIMIT_PER_HOUR (default 10).
- Update yt-dlp regularly (rebuild the image) since platforms change often.

## SEO pages
- `build_pages.py` generates a landing page per platform (TikTok, Instagram, Facebook, X, Pinterest, Reddit, Vimeo) plus sitemap.xml and robots.txt.
- Set your real domain in the `ENV SITE=` line of the Dockerfile (it rebuilds the pages on every deploy).
- After launch, add the site to Google Search Console and submit /sitemap.xml.
- To add a platform, add an entry to PAGES in build_pages.py.
