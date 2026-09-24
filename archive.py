#!/usr/bin/env python3
"""Archive blog.codeleak.pl posts as plain Markdown with local images.

Metadata (title, dates, labels, URL) comes from the Blogger JSON feed; the feed
is cut at the jump break, so full content is taken from each post page.
"""
import hashlib
import json
import mimetypes
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString
from markdownify import MarkdownConverter

BLOG = "https://blog.codeleak.pl"
ROOT = Path(__file__).parent
POSTS = ROOT / "posts"
CACHE = ROOT / ".cache"
IMAGE_HOSTS = ("googleusercontent.com", "bp.blogspot.com", "blogger.com",
               "storage.googleapis.com", "drive.google.com")

session = requests.Session()
session.headers["User-Agent"] = "codeleak-blog-archive/1.0"


def get(url, **kw):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == 2:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(2)


def fetch_entries():
    entries, start = [], 1
    while True:
        feed = get(f"{BLOG}/feeds/posts/default",
                   params={"alt": "json", "max-results": 150, "start-index": start}).json()["feed"]
        batch = feed.get("entry", [])
        entries += batch
        if len(batch) < 150:
            return entries
        start += 150


def post_path(url):
    """https://blog.codeleak.pl/2016/03/slug.html -> posts/2016/03/slug"""
    p = urlparse(url).path
    return POSTS / re.sub(r"\.html$", "", p.strip("/"))


# --- HTML clean-up -----------------------------------------------------------

def detect_lang(pre):
    classes = " ".join(pre.get("class", []))
    code = pre.find("code")
    if code:
        classes += " " + " ".join(code.get("class", []))
    for pattern in (r"language-([\w+#-]+)", r"lang-([\w+#-]+)", r"brush:\s*([\w+#-]+)"):
        m = re.search(pattern, classes + " " + pre.get("class", "").__str__())
        if m:
            return m.group(1).lower().rstrip(";")
    m = re.search(r"brush:\s*([\w+#-]+)", str(pre.get("class")))
    return m.group(1).lower() if m else ""


HTML_IN_PRE = {"span", "code", "b", "i", "em", "strong", "br", "a", "font", "u", "div", "p"}


def escape_raw_pre(html):
    """Old posts put unescaped XML inside <pre>; escape non-HTML tags before parsing."""
    def fix(m):
        inner = re.sub(r"<(/?)([\w:.-]+)",
                       lambda t: t.group(0) if t.group(2).lower() in HTML_IN_PRE
                       else f"&lt;{t.group(1)}{t.group(2)}", m.group(2))
        return m.group(1) + inner + m.group(3)
    return re.sub(r"(<pre[^>]*>)(.*?)(</pre>)", fix, html, flags=re.S | re.I)


def normalize_pre(soup):
    for pre in soup.find_all("pre"):
        lang = detect_lang(pre)
        text = pre.get_text()
        pre.clear()
        pre["data-lang"] = lang
        pre.append(NavigableString(text.strip("\n")))


def original_image_url(src):
    host = urlparse(src).netloc
    if "googleusercontent.com" in host or "bp.blogspot.com" in host:
        # /s400/ or /w640-h400/ path segment, or =s400 suffix -> original size
        src = re.sub(r"/(?:s|w|h)\d+[^/]*/(?=[^/]+$)", "/s0/", src)
        src = re.sub(r"=[swh]\d+[^/]*$", "=s0", src)
    return src


def download_image(src, target_dir, used):
    url = original_image_url(src)
    try:
        r = get(url)
    except requests.RequestException:
        r = get(src)  # fall back to the size used in the post
    name = unquote(urlparse(src).path.rstrip("/").split("/")[-1]).split("/")[-1]
    name = re.sub(r"[^\w.-]+", "-", name).strip("-") or "image"
    if "." not in name:
        ext = mimetypes.guess_extension(r.headers.get("content-type", "").split(";")[0]) or ".png"
        name += ext
    if name in used and used[name] != url:
        stem, ext = name.rsplit(".", 1)
        name = f"{stem}-{hashlib.sha1(url.encode()).hexdigest()[:6]}.{ext}"
    used[name] = url
    (target_dir / name).write_bytes(r.content)
    return name


def localize_images(soup, target_dir):
    used = {}
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src.startswith("http") or not any(h in src for h in IMAGE_HOSTS):
            continue
        try:
            name = download_image(src, target_dir, used)
        except requests.RequestException as e:
            print(f"  ! image failed {src}: {e}", file=sys.stderr)
            continue
        img["src"] = name
        for attr in ("width", "height", "border", "style"):
            img.attrs.pop(attr, None)
        # Blogger wraps images in a link to the full-size version: unwrap it
        a = img.find_parent("a")
        if a and any(h in a.get("href", "") for h in IMAGE_HOSTS):
            a.unwrap()


def relativize_links(soup, post_dir):
    for a in soup.find_all("a", href=True):
        u = urlparse(a["href"])
        if u.netloc in ("blog.codeleak.pl", "codeleak.blogspot.com") and u.path.endswith(".html"):
            target = post_path(f"{BLOG}{u.path}")
            rel = Path(*([".."] * len(post_dir.relative_to(POSTS).parts))) / target.relative_to(POSTS)
            a["href"] = f"{rel.as_posix()}/index.md" + (f"#{u.fragment}" if u.fragment else "")
        elif u.fragment == "more" and not a.get_text(strip=True):
            a.decompose()


class Converter(MarkdownConverter):
    def convert_pre(self, el, text, *args, **kwargs):
        code = el.get_text()
        fence = "````" if "```" in code else "```"
        return f"\n\n{fence}{el.get('data-lang', '')}\n{code}\n{fence}\n\n"


def to_markdown(html):
    md = Converter(heading_style="ATX", bullets="-", escape_underscores=False,
                   escape_asterisks=False).convert(html)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


# --- main --------------------------------------------------------------------

def archive(entry, force=False):
    url = next(l["href"] for l in entry["link"] if l["rel"] == "alternate")
    post_dir = post_path(url)
    md_file = post_dir / "index.md"
    if md_file.exists() and not force:
        return url, post_dir, "skip"
    post_dir.mkdir(parents=True, exist_ok=True)

    page = BeautifulSoup(escape_raw_pre(get(url).text), "html.parser")
    body = page.select_one("div.post-body")
    for junk in body.select("script, style, link, meta, head"):
        junk.decompose()
    for wrapper in body.select("html, body"):
        wrapper.unwrap()

    normalize_pre(body)
    localize_images(body, post_dir)
    relativize_links(body, post_dir)

    title = entry["title"]["$t"]
    tags = sorted(c["term"] for c in entry.get("category", []))
    front = "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        f"date: {entry['published']['$t']}",
        f"updated: {entry['updated']['$t']}",
        f"author: {yaml_str(entry['author'][0]['name']['$t'])}",
        f"tags: [{', '.join(yaml_str(t) for t in tags)}]",
        f"original_url: {url}",
        "---",
    ])
    md_file.write_text(f"{front}\n\n# {title}\n\n{to_markdown(str(body))}")
    return url, post_dir, "ok"


def write_index(entries):
    lines = ["# blog.codeleak.pl — archive", "",
             f"{len(entries)} posts archived from <{BLOG}> as Markdown with local images.", ""]
    year = None
    for e in sorted(entries, key=lambda e: e["published"]["$t"], reverse=True):
        url = next(l["href"] for l in e["link"] if l["rel"] == "alternate")
        y = e["published"]["$t"][:4]
        if y != year:
            lines += ["", f"## {y}", ""]
            year = y
        tags = ", ".join(f"`{c['term']}`" for c in e.get("category", []))
        rel = post_path(url).relative_to(ROOT).as_posix()
        lines.append(f"- {e['published']['$t'][:10]} [{e['title']['$t']}]({rel}/index.md) {tags}".rstrip())
    (ROOT / "README.md").write_text("\n".join(lines) + "\n")


def main():
    force = "--force" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    entries = fetch_entries()
    print(f"{len(entries)} posts in feed")
    selected = [e for e in entries if not only or any(o in json.dumps(e["link"]) for o in only)]
    for i, e in enumerate(selected, 1):
        try:
            url, _, status = archive(e, force)
            print(f"[{i}/{len(selected)}] {status} {url}")
        except Exception as ex:
            print(f"[{i}/{len(selected)}] FAILED {e['title']['$t']}: {ex}", file=sys.stderr)
    write_index(entries)


if __name__ == "__main__":
    main()
