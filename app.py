import os, glob, shutil, socket, ipaddress, subprocess, tempfile, threading, time
from urllib.parse import urlparse
import re
from flask import Flask, request, jsonify, send_file, send_from_directory, abort

app = Flask(__name__, static_folder="static", static_url_path="")

MAX_JOBS = threading.BoundedSemaphore(int(os.getenv("MAX_JOBS", "2")))  # free CPUs are small
LIMIT_PER_HOUR = int(os.getenv("LIMIT_PER_HOUR", "10"))
HITS = {}

FORMATS = {
    "regular": "b[height<=480]/bv*[height<=480]+ba/b",
    "hd": "bv*[height<=1080]+ba/b[height<=1080]/b",
    "ai": "bv*[height<=1080]+ba/b[height<=1080]/b",
}

def err(msg, code):
    return jsonify(error=msg), code

def client_ip():
    return (request.headers.get("X-Forwarded-For") or request.remote_addr or "?").split(",")[0].strip()

def rate_ok(ip):
    now = time.time()
    h = [t for t in HITS.get(ip, []) if now - t < 3600]
    ok = len(h) < LIMIT_PER_HOUR
    if ok:
        h.append(now)
    HITS[ip] = h
    return ok

def safe_url(u):
    p = urlparse(u)
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        for info in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except Exception:
        return False
    return True

@app.get("/health")
def health():
    return "ok"

@app.get("/api/download")
def download():
    url = request.args.get("url", "").strip()
    q = request.args.get("q", "hd")
    if q not in FORMATS or len(url) > 500 or not safe_url(url):
        return err("Invalid link or quality.", 400)
    if not rate_ok(client_ip()):
        return err("Too many downloads. Please try again later.", 429)
    if not MAX_JOBS.acquire(blocking=False):
        return err("Server is busy. Try again in a minute.", 503)

    tmp = tempfile.mkdtemp()
    def cleanup():
        shutil.rmtree(tmp, ignore_errors=True)
        MAX_JOBS.release()

    try:
        cmd = ["yt-dlp", "--no-playlist", "--no-warnings", "--socket-timeout", "15",
               "--max-filesize", "200M", "--match-filter", "duration<=300",
               "-f", FORMATS[q], "--merge-output-format", "mp4",
               "-o", f"{tmp}/in.%(ext)s", "--", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        files = glob.glob(f"{tmp}/in.*")
        if r.returncode != 0 or not files:
            cleanup()
            return err("Couldn't fetch that video. It may be private, too long (5 min max) or unsupported.", 422)
        src = files[0]
        if q == "ai":
            out = f"{tmp}/out.mp4"
            vf = "scale=-2:'max(ih,1080)':flags=lanczos,hqdn3d=1.5:1.5:6:6,unsharp=5:5:0.8"
            subprocess.run(["ffmpeg", "-y", "-i", src, "-vf", vf, "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "20", "-c:a", "aac",
                            "-movflags", "+faststart", out],
                           capture_output=True, timeout=170, check=True)
            src = out
        resp = send_file(src, mimetype="video/mp4", as_attachment=True, download_name=f"video-{q}.mp4")
        resp.call_on_close(cleanup)
        return resp
    except Exception:
        cleanup()
        return err("Processing failed or took too long. Try a shorter video or another quality.", 500)

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/<slug>")
def clean_url(slug):
    if re.fullmatch(r"[a-z0-9-]+", slug) and os.path.exists(f"static/{slug}.html"):
        return send_from_directory("static", f"{slug}.html")
    return send_from_directory("static", slug)  # legal.html, sitemap.xml, robots.txt (404 if missing)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
