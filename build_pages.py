"""Generates SEO landing pages, sitemap.xml and robots.txt into static/.
Run: SITE=https://yourdomain.com python build_pages.py  (the Dockerfile does this at build time)"""
import os, json, html
SITE = os.getenv("SITE", "https://YOUR-DOMAIN").rstrip("/")
base = open("template/base.html", encoding="utf-8").read()

COMMON_FAQ = [
 ("Is it free?", "Yes. There is no signup and no limit on how many times you can visit, though downloads per hour are capped to keep the service fast for everyone."),
 ("Which quality should I pick?", "Regular is the fastest and smallest. HD gives you up to 1080p when the original is available. AI HD upscales and sharpens the video, so it takes longer but can look better on low-resolution clips."),
]
PAGES = [
 dict(slug="tiktok-video-downloader", name="TikTok",
  intro="Found a TikTok you want to keep for offline viewing? Copy the link from the Share button, paste it into the box above and choose a quality. Short clips usually finish in seconds.",
  tip="In the TikTok app, tap Share, then Copy link. Links that start with vm.tiktok.com or tiktok.com both work.",
  faq=[("Can I download private TikToks?", "No. Only public videos can be fetched. Private or friends-only videos need the owner's permission and will not work here.")]),
 dict(slug="instagram-reels-downloader", name="Instagram Reels",
  intro="Save public Instagram Reels and video posts to your phone or computer. Paste the link of the Reel, pick Regular, HD or AI HD, and your file is ready in a moment.",
  tip="Open the Reel, tap the paper-plane or three-dot menu and choose Copy link.",
  faq=[("Does it work for Stories?", "Stories and private accounts are usually not available. Public Reels and video posts are the best-supported.")]),
 dict(slug="facebook-video-downloader", name="Facebook",
  intro="Download public Facebook videos, including posts from pages and public profiles. Paste the video link above and choose how much quality you need.",
  tip="On a video, tap Share, then Copy link. Links from fb.watch also work.",
  faq=[("Why does my Facebook link fail?", "Videos posted to groups or shared only with friends are private and can't be downloaded. Try a public video.")]),
 dict(slug="twitter-video-downloader", name="Twitter / X",
  intro="Save videos and GIFs from public posts on X (Twitter). Copy the post link, paste it above and download in the quality you want.",
  tip="Tap the share icon under the post and choose Copy link to post.",
  faq=[("Does it save GIFs?", "Posts with a video or animated GIF can be saved as an MP4 file.")]),
 dict(slug="pinterest-video-downloader", name="Pinterest",
  intro="Download video Pins from Pinterest for offline viewing. Paste the Pin link, pick your quality, and save the MP4.",
  tip="Open the Pin, tap the three dots or Share, then Copy link. Short pin.it links work too.",
  faq=[("Can I download image Pins?", "This tool is built for video Pins. Image Pins are not supported.")]),
 dict(slug="reddit-video-downloader", name="Reddit",
  intro="Reddit hosts videos with the audio stored separately, which makes saving them awkward. Paste the post link above and we merge video and sound into one MP4 for you.",
  tip="Tap Share on the post and choose Copy link.",
  faq=[("Why do other tools give me silent Reddit videos?", "Reddit keeps video and audio in separate files. SaveClip merges them so the download has sound.")]),
 dict(slug="vimeo-video-downloader", name="Vimeo",
  intro="Save public Vimeo videos in regular or HD quality. Paste the video page link above and pick a quality.",
  tip="Copy the link from your browser's address bar while watching the video.",
  faq=[("Can I download password-protected Vimeo videos?", "No. Private, password-protected or download-disabled videos are not supported.")]),
]

def page(title, h1, sub, desc, path, content, faqs=None):
    s = base
    s = s.replace("<title>SaveClip – Free Online Video Downloader</title>", f"<title>{html.escape(title)}</title>")
    s = s.replace('content="Paste a public video link and download it in regular, HD or enhanced HD quality. Free, no signup."', f'content="{html.escape(desc, quote=True)}"')
    s = s.replace("<!--HEAD-->", f'<link rel="canonical" href="{SITE}{path}">' + (
        '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}) + '</script>' if faqs else ""))
    s = s.replace("<h1>SaveClip</h1>", f"<h1>{html.escape(h1)}</h1>")
    s = s.replace('<p class="sub">Paste a public video link and pick a quality.</p>', f'<p class="sub">{html.escape(sub)}</p>')
    s = s.replace("<!--CONTENT-->", content)
    links = '<div class="links">' + "".join(f'<a href="/{p["slug"]}">{p["name"]}</a>' for p in PAGES) + "</div>"
    return s.replace("<!--LINKS-->", links)

pages = [("/", page("SaveClip – Free Online Video Downloader", "SaveClip", "Paste a public video link and pick a quality.",
    "Paste a public video link and download it in regular, HD or enhanced HD quality. Free, no signup.", "/", ""))]
for p in PAGES:
    n = p["name"]; faqs = p["faq"] + COMMON_FAQ
    content = (f'<section class="info"><h2>How to download {n} videos</h2><p>{html.escape(p["intro"])}</p>'
      f'<ol><li>Copy the link. {html.escape(p["tip"])}</li><li>Paste it into the box above.</li>'
      f'<li>Tap Regular, HD or AI HD and wait for the download to start.</li></ol>'
      f'<h2>FAQ</h2>' + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs) +
      f'<p>Please only save {n} videos you own or have permission to download.</p></section>')
    pages.append((f"/{p['slug']}", page(f"{n} Video Downloader – Save {n} Videos in HD | SaveClip", f"{n} Video Downloader",
      f"Paste a public {n} link and pick a quality.", f"Free {n} video downloader. Paste a public link and save the video in regular, HD or enhanced HD quality. No signup.",
      f"/{p['slug']}", content, faqs)))

os.makedirs("static", exist_ok=True)
for path, body in pages:
    open("static/" + ("index" if path == "/" else path[1:]) + ".html", "w", encoding="utf-8").write(body)
open("static/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"<url><loc>{SITE}{path if path != '/' else '/'}</loc></url>\n" for path, _ in pages) + "</urlset>\n")
open("static/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print("built", len(pages), "pages for", SITE)
