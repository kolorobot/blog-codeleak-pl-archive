"""Assemble the Blogger template and static previews from src/.

  python3 build.py [data/feed.json]

data/feed.json is a snapshot of https://blog.codeleak.pl/feeds/posts/default?alt=json&max-results=500
(used only for the previews).

Outputs:
  codeleak-the-record.xml   – paste into Blogger → Theme → Edit HTML
  preview/home.html, preview/post.html – static approximations for review
"""
import html
import json
import re
import sys
import xml.dom.minidom
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
css = (SRC / "theme.css").read_text()
js = (SRC / "archive.js").read_text()

assert "]]>" not in css and "]]>" not in js
assert "$(" not in css, "Blogger skin would treat $( as a variable"

tpl = (SRC / "skeleton.xml").read_text()
out = tpl.replace("/*@@CSS@@*/", css).replace("//@@JS@@", js)
(ROOT / "codeleak-the-record.xml").write_text(out)
xml.dom.minidom.parseString(out.encode("utf-8"))  # well-formedness check
print("template OK:", len(out), "bytes")

# ---------------------------------------------------------------- previews
if len(sys.argv) < 2:
    sys.exit(0)

feed = json.load(open(sys.argv[1]))["feed"]["entry"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def alt(e):
    return next(l["href"] for l in e["link"] if l["rel"] == "alternate")


def snippet(e, n=260):
    t = re.sub(r"<[^>]+>", " ", e["content"]["$t"])
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    return html.escape(t[:n])


# archive widget markup
years = OrderedDict()
for e in feed:
    d = e["published"]["$t"]
    years.setdefault(d[:4], OrderedDict()).setdefault(d[5:7], []).append(e)


def archive_html():
    items = []
    for i, (y, months) in enumerate(years.items()):
        mitems = []
        for m, posts in months.items():
            plist = ""
            if i == 0 and m == next(iter(months)):
                plist = "<ul class='posts hierarchy'>" + "".join(
                    f"<li><a href='{alt(p)}'>{html.escape(p['title']['$t'])}</a></li>" for p in posts) + "</ul>"
            mitems.append(
                f"<li class='archivedate'><div class='hierarchy-title'><a class='post-count-link' href='https://blog.codeleak.pl/{y}/{m}/'>"
                f"{MONTHS[int(m) - 1]} <span class='post-count'>{len(posts)}</span></a></div><div class='hierarchy-content'>{plist}</div></li>")
        n = sum(len(v) for v in months.values())
        items.append(
            f"<li class='archivedate'><div class='hierarchy-title'><a class='post-count-link' href='https://blog.codeleak.pl/{y}/'>{y} "
            f"<span class='post-count'>{n}</span></a></div><div class='hierarchy-content'><ul class='hierarchy'>{''.join(mitems)}</ul></div></li>")
    return ("<div class='widget BlogArchive' id='BlogArchive1'><details class='collapsible extendable' open='open'>"
            "<summary><div class='collapsible-title'><h3 class='title'>By year</h3></div></summary>"
            "<div class='widget-content'><div id='ArchiveList'><div id='BlogArchive1_ArchiveList'><div class='first-items'>"
            f"<ul class='hierarchy'>{''.join(items)}</ul></div></div></div></div></details></div>")


labels = {}
for e in feed:
    for c in e.get("category", []):
        labels[c["term"]] = labels.get(c["term"], 0) + 1


def labels_html():
    mx = max(labels.values())
    out = []
    for k in sorted(labels, key=str.lower):
        size = 1 + round(4 * labels[k] / mx)
        out.append(f"<span class='label-size label-size-{size}'><a class='label-name' href='#'>{html.escape(k)}"
                   f"<span class='label-count'>{labels[k]}</span></a></span>")
    return ("<div class='widget Label' id='Label1'><details class='collapsible extendable' open='open'>"
            "<summary><div class='collapsible-title'><h3 class='title'>Subjects</h3></div></summary>"
            f"<div class='widget-content cloud-label-widget-content'>{''.join(out)}</div></details></div>")


SEARCH_ICON = "<svg class='svg-icon-24 search-expand-icon' viewBox='0 0 24 24'><path d='M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'/></svg>"
MENU_ICON = "<button class='svg-icon-24-button hamburger-menu flat-icon-button ripple'><svg class='svg-icon-24' viewBox='0 0 24 24'><path d='M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z'/></svg></button>"
BACK_ICON = "<a class='return_link' href='home.html'><button class='svg-icon-24-button back-button rtl-reversible-icon flat-icon-button ripple'><svg class='svg-icon-24' viewBox='0 0 24 24'><path d='M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z'/></svg></button></a>"
SHARE_ICON = "<svg class='svg-icon-24' viewBox='0 0 24 24'><path d='M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z'/></svg>"


def header(item):
    nav = "" if item else ("<nav><div class='section' id='page_list_top'><div class='widget PageList'><div class='widget-content'>"
                           "<ul class='tabs'><li class='selected'><a href='home.html'>Home</a></li><li><a href='#'>About Me</a></li></ul></div></div></div></nav>")
    return (f"<div class='centered-top-placeholder'></div><header class='centered-top-container' role='banner'><div class='centered-top'>"
            f"{BACK_ICON if item else MENU_ICON}"
            f"<div class='search'><button aria-label='Search' class='search-expand touch-icon-button'><div class='flat-icon-button ripple'>{SEARCH_ICON}</div></button>"
            "<div class='section' id='search_top'><div class='widget BlogSearch'><h3 class='title'>Search This Blog</h3><div class='widget-content' role='search'>"
            "<form action='#'><div class='search-input'><input aria-label='Search the record' autocomplete='off' name='q' placeholder='Search the record…'/></div>"
            "<input class='search-action flat-button' type='submit' value='Search'/></form></div></div></div></div>"
            "<div class='clearboth'></div><div class='blog-name container'><div class='container section' id='header'><div class='widget Header'>"
            "<div class='header-widget'><div><h1><a href='home.html'>blog.codeleak.pl</a></h1></div><p>by Rafał Borowiec</p></div></div></div>"
            f"{nav}</div></div></header>")


def shell(body_cls, main, hero=""):
    t = tpl
    status = re.search(r"(<div class='cl-status'.*?</div>\s*</div>)", t, re.S).group(1)
    colophon = re.search(r"(<div class='cl-colophon'>.*?<p class='cl-colophon-end'>.*?</p>\s*</div>)", t, re.S).group(1)
    railfoot = re.search(r"(<div class='cl-rail-foot'>.*?</div>)", t, re.S).group(1)
    rail = re.search(r"(<div class='cl-rail-head'>.*?</div>)", t, re.S).group(1)
    fix = lambda s: re.sub(r"<(span|div|b|i)([^<>]*?)/>", r"<\1\2></\1>", s).replace("=''", "").replace("&#8211;", "–").replace("&#8212;", "—").replace("&#183;", "·")
    item = "item-view" in body_cls
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{'Validation groups in Spring MVC' if item else 'blog.codeleak.pl'} — preview</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body class="{body_cls} version-1-3-0">
<a class='skip-navigation' href='#main'>Skip to main content</a>
{fix(status)}
<div class='cl-shell'><div class='page'><div class='page_body'><div class='centered'>
{header(item)}
{hero}
<div class='cl-body'><main class='centered-bottom' id='main' role='main'>{main}</main></div>
<div class='cl-foot'>{fix(colophon)}<footer class='footer section' id='footer'><div class='widget Attribution'><div class='widget-content'><div class='blogger'><a href='#'>Powered by Blogger</a></div></div></div></footer></div>
</div></div></div>
<aside class='sidebar-container container sidebar-invisible' role='complementary'>
<div class='navigation'><button class='svg-icon-24-button flat-icon-button ripple sidebar-back'><svg class='svg-icon-24' viewBox='0 0 24 24'><path d='M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z'/></svg></button></div>
{fix(rail)}
<div class='sidebar_bottom section' id='sidebar_bottom'>{archive_html()}{labels_html()}</div>
{fix(railfoot)}
</aside></div>
<script>{js}</script>
<script>
/* preview-only shim for what Blogger's indie script does */
(function(){{var b=document.body,s=document.querySelector('.sidebar-container');
function tog(v){{s.classList.toggle('sidebar-invisible',!v);b.classList.toggle('sidebar-visible',v);}}
var h=document.querySelector('.hamburger-menu');if(h)h.onclick=function(){{tog(true)}};
document.querySelector('.sidebar-back').onclick=function(){{tog(false)}};
var se=document.querySelector('.search-expand');se.onclick=function(){{document.querySelector('.search').classList.add('focused');document.querySelector('.centered-top').classList.add('search-focused');document.querySelector('.search input').focus();}};
}})();
</script></body></html>"""


def share(pos):
    return (f"<div class='post-share-buttons post-share-buttons-{pos}'><div class='byline post-share-buttons goog-inline-block'><div class='sharing'>"
            f"<button aria-label='Share' class='sharing-button touch-icon-button'><div class='flat-icon-button ripple'>{SHARE_ICON}</div></button></div></div></div>")


# home
featured, rest = feed[0], feed[1:9]
fp = (f"<div class='main section' id='page_body'><div class='widget FeaturedPost' id='FeaturedPost1'><div class='widget-content'><div role='feed'><article class='post'>"
      f"<div class='cl-final' data-cl-date='{featured['published']['$t']}'>"
      f"<p class='cl-kicker'><span>Final entry</span> <span class='cl-recid'></span> <time class='cl-date'></time></p>"
      f"<h3 class='post-title'><a href='post.html'>{html.escape(featured['title']['$t'])}</a></h3>"
      f"<div class='post-snippet snippet-container r-snippet-container'><div class='snippet-item r-snippetized'>{snippet(featured, 420)}</div></div>"
      f"<div class='jump-link'><a href='post.html'>Open record</a></div></div></article></div></div></div>")
posts = "".join(
    f"<article class='post-outer-container'><div class='post-outer'><div class='post' data-cl-date='{e['published']['$t']}'>"
    f"<div class='cl-entry'><div class='cl-entry-meta'><span class='cl-recid'></span><time class='cl-date'></time><span class='cl-ago'></span></div>"
    f"<div class='cl-entry-main'><h3 class='post-title entry-title'><a href='post.html'>{html.escape(e['title']['$t'])}</a></h3>"
    f"<div class='container post-body entry-content'><div class='post-snippet snippet-container r-snippet-container'><div class='snippet-item r-snippetized'>{snippet(e)}</div></div></div>"
    f"<div class='jump-link'><a href='post.html'>Open record</a></div></div></div></div></div></article>"
    for e in rest)
blog = (f"<div class='widget Blog' id='Blog1'><div class='blog-posts hfeed container'>{posts}</div>"
        "<div class='blog-pager container' id='blog-pager'><a class='blog-pager-older-link' href='#'>Older entries →</a></div></div></div>")
hero = re.search(r"(<section aria-labelledby='cl-hero-title'.*?</section>)", tpl, re.S).group(1)
hero = hero.replace("=''", "").replace("&#8211;", "–").replace("&#8212;", "—").replace("&#183;", "·").replace("<div id='cl-timeline'/>", "<div id='cl-timeline'></div>")
(ROOT / "preview").mkdir(exist_ok=True)
(ROOT / "preview/home.html").write_text(shell("home-view", fp + blog, hero))

# post
target = next(e for e in feed if e["title"]["$t"].startswith("Validation groups in Spring MVC"))
tags = "".join(f"<a href='#' rel='tag'>{html.escape(c['term'])}</a>" for c in target.get("category", []))
pops = "".join(
    f"<article class='post'><div class='cl-pop' data-cl-date='{e['published']['$t']}'><p class='cl-pop-meta'><span class='cl-recid'></span> · <span class='cl-ago'></span></p>"
    f"<h3 class='post-title'><a href='#'>{html.escape(e['title']['$t'])}</a></h3><div class='item-content float-container'>"
    f"<div class='popular-posts-snippet snippet-container r-snippet-container'><div class='snippet-item r-snippetized'>{snippet(e, 150)}</div></div>"
    f"<div class='jump-link'><a href='#'>Open record</a></div></div></div></article>"
    for e in feed[1:4])
post_tpl = re.search(r"<b:if cond='data:view.isPost'>(.*?)<b:elseif", tpl, re.S).group(1)
record = re.search(r"(<div class='cl-record'>.*?</div>\s*</div>)", post_tpl, re.S).group(1)
record = (record.replace("<time class='cl-date published' expr:datetime='data:post.date.iso8601'><data:post.date/></time>", "<time class='cl-date'></time>")
          .replace("<b data-label=''/>", "<b></b>").replace("&#8212;", "—"))
notice = re.search(r"(<aside class='cl-notice'.*?</aside>)", post_tpl, re.S).group(1).replace("&#8212;", "—")
single = (f"<div class='main section' id='page_body'><div class='widget Blog' id='Blog1'><div class='blog-posts hfeed container'>"
          f"<article class='post-outer-container'><div class='post-outer'><div class='post' data-cl-date='{target['published']['$t']}'>"
          f"{record}<h1 class='post-title entry-title'>{html.escape(target['title']['$t'])}</h1>{share('top')}"
          "<div class='post-header'><div class='post-header-line-1'><span class='byline post-author vcard'><span class='post-author-label'>By </span>"
          "<span class='fn'><a class='g-profile' href='#'><span>Rafał Borowiec</span></a></span></span></div></div>"
          f"{notice}<div class='post-body entry-content float-container'>{target['content']['$t']}</div>"
          "<p class='cl-endmark'><span>End of record <span class='cl-recid'></span></span></p>"
          f"<div class='post-bottom'><div class='post-footer float-container'><div class='post-footer-line post-footer-line-2'><span class='byline post-labels'>{tags}</span></div></div>{share('bottom')}</div>"
          "<nav class='cl-recnav'><a class='cl-newer' href='#'>← Newer record</a><a class='cl-older' href='#'>Older record →</a></nav>"
          "</div></div><section class='comments threaded' data-num-comments='2' id='comments'><h3 class='title cl-comments-title'>Marginalia</h3>"
          "<p class='cl-comments-note'>Reader comments, kept with the record.</p><div class='comments-content'><div id='comment-holder'><div class='comment-thread'><ol>"
          "<li class='comment'><div class='avatar-image-container'><svg viewBox='0 0 24 24' class='avatar-icon'><circle cx='12' cy='8' r='4'/><path d='M4 20c0-4 4-6 8-6s8 2 8 6'/></svg></div>"
          "<div class='comment-block'><div class='comment-header'><cite class='user'><a href='#'>Reader</a></cite><span class='datetime'><a href='#'>August 13, 2014</a></span></div>"
          "<p class='comment-content'>Great write-up — group sequences were exactly what I needed for my wizard form.</p></div></li></ol></div></div></div></section>"
          "</article></div></div>"
          f"<div class='widget PopularPosts' id='PopularPosts1'><h3 class='title'>Most consulted records</h3><div class='widget-content'><div role='feed'>{pops}</div></div></div></div>")
(ROOT / "preview/post.html").write_text(shell("item-view", single))
print("previews OK")
