/* codeleak — The Record: archive enhancements (no dependencies). */
(function () {
  'use strict';

  var CFG = {
    since: 2011,
    until: 2023, // the record closes here; anything published later is an epilogue (no archival note, not counted)
    // Used only if the Archive widget is missing from the page.
    fallbackYears: { 2011: 9, 2012: 3, 2013: 16, 2014: 35, 2015: 25, 2016: 12, 2017: 13, 2018: 0, 2019: 8, 2020: 14, 2021: 3, 2022: 0, 2023: 5 },
    hljs: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/'
  };

  var doc = document;
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  function $$(sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function el(tag, cls, html) { var e = doc.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function setText(root, sel, text) { $$(sel, root).forEach(function (n) { n.textContent = text; }); }

  function parseISO(s) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || '');
    return m ? { y: +m[1], m: +m[2], d: +m[3] } : null;
  }
  function yearsAgo(p) {
    var now = new Date(), a = now.getFullYear() - p.y, nm = now.getMonth() + 1;
    if (nm < p.m || (nm === p.m && now.getDate() < p.d)) a--;
    return Math.max(0, a);
  }
  function ageText(n) { return n < 1 ? 'under a year' : n === 1 ? '1 year' : n + ' years'; }
  function agoText(n) { return n < 1 ? 'this year' : n === 1 ? '1 yr ago' : n + ' yrs ago'; }
  function recId(p) { return 'CL-' + p.y + '-' + pad(p.m) + pad(p.d); }
  function niceDate(p) { return p.d + ' ' + MONTHS[p.m - 1].slice(0, 3) + ' ' + p.y; }

  function tier(n) {
    if (n >= 10) return { key: 'vintage', name: 'Vintage record',
      text: 'It documents how things were done at the time. Expect deprecated APIs and long-gone tooling \u2014 valuable as history, risky as a recipe.' };
    if (n >= 5) return { key: 'historical', name: 'Historical record',
      text: 'Versions, APIs and defaults have most likely changed since. Read it as context and verify against current docs before you copy anything.' };
    return { key: 'recent', name: 'Archived record',
      text: 'It is no longer maintained, so parts of it may already be out of date \u2014 check current docs for versions, APIs and defaults before relying on it.' };
  }

  /* ---------- Years: read the Archive widget (falls back to frozen data) ---------- */
  function readYears() {
    var years = {}, links = {};
    $$('.BlogArchive li.archivedate').forEach(function (li) {
      if (li.parentNode && li.parentNode.closest && li.parentNode.closest('li.archivedate')) return; // months
      var a = li.querySelector('.hierarchy-title a, a.post-count-link');
      var m = a && /(\d{4})/.exec(a.textContent);
      if (!m) return;
      li.classList.add('cl-y');
      if (+m[1] > CFG.until) return;
      var c = li.querySelector('.post-count');
      years[+m[1]] = c ? parseInt(c.textContent.replace(/\D/g, ''), 10) || 0 : 0;
      links[+m[1]] = a.href;
    });
    if (!Object.keys(years).length) years = CFG.fallbackYears;
    var ys = Object.keys(years).map(Number);
    var from = Math.min.apply(null, ys.concat(CFG.since)), to = CFG.until;
    var list = [], total = 0, max = 0;
    for (var y = from; y <= to; y++) {
      var n = years[y] || 0;
      total += n; max = Math.max(max, n);
      list.push({ y: y, n: n, href: links[y] || ('/' + y + '/') });
    }
    return { list: list, total: total, max: max, from: from, to: to };
  }

  function renderTimeline(data) {
    var host = doc.getElementById('cl-timeline');
    if (!host) return;
    var ol = el('ol', 'cl-tl');
    data.list.forEach(function (it, i) {
      var li = el('li', it.n ? '' : 'is-empty');
      if (i === data.list.length - 1) li.classList.add('is-last');
      li.style.setProperty('--h', it.n ? Math.max(0.04, it.n / data.max).toFixed(3) : 0);
      var inner = '<span class="cl-tl-n">' + (it.n || '—') + '</span><span class="cl-tl-bar"></span>' +
        '<span class="cl-tl-lbl">’' + String(it.y).slice(2) + '</span>';
      if (it.n) {
        var a = el('a', null, inner);
        a.href = it.href;
        a.title = it.y + ' · ' + it.n + (it.n === 1 ? ' entry' : ' entries');
        li.appendChild(a);
      } else {
        var s = el('span', 'cl-tl-cell', inner);
        s.title = it.y + ' · no entries';
        li.appendChild(s);
      }
      ol.appendChild(li);
    });
    host.innerHTML = '';
    host.appendChild(ol);
    host.appendChild(el('div', 'cl-tl-lbls-gap'));
  }

  function enhanceArchiveRail(data) {
    var max = data.max || 1;
    var path = location.pathname;
    $$('.BlogArchive li.cl-y').forEach(function (li) {
      var title = li.querySelector('.hierarchy-title');
      var c = li.querySelector('.post-count');
      if (!title || title.querySelector('.cl-bar')) return;
      var n = c ? parseInt(c.textContent.replace(/\D/g, ''), 10) || 0 : 0;
      var bar = el('span', 'cl-bar');
      bar.style.setProperty('--w', (n / max).toFixed(3));
      var content = li.querySelector('.hierarchy-content');
      if (content && content.children.length) {
        var btn = el('button', 'cl-y-toggle', '›');
        btn.type = 'button';
        btn.setAttribute('aria-expanded', 'false');
        btn.setAttribute('aria-label', 'Show months');
        btn.addEventListener('click', function () {
          var open = li.classList.toggle('cl-open');
          btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        title.appendChild(btn);
        var y = /(\d{4})/.exec(title.textContent);
        if (y && path.indexOf('/' + y[1] + '/') === 0) { li.classList.add('cl-open'); btn.setAttribute('aria-expanded', 'true'); }
      }
      title.appendChild(bar);
    });
  }

  /* ---------- Posts: record IDs, age, tier, span ---------- */
  function decoratePosts(data) {
    $$('[data-cl-date]').forEach(function (post) {
      var p = parseISO(post.getAttribute('data-cl-date'));
      if (!p) return;
      var age = yearsAgo(p), t = tier(age);
      var epilogue = p.y > CFG.until;
      if (epilogue) {
        post.classList.add('cl-epilogue');
        $$('.cl-notice', post).forEach(function (n) { n.parentNode.removeChild(n); });
      }
      setText(post, '.cl-recid', recId(p));
      setText(post, '.cl-age', ageText(age));
      setText(post, '.cl-ago', agoText(age));
      setText(post, '.cl-month', MONTHS[p.m - 1] + ' ' + p.y);
      setText(post, '.cl-year', String(p.y));
      setText(post, '.cl-tier-name', t.name);
      setText(post, '.cl-tier-text', t.text);
      $$('.cl-date', post).forEach(function (d) { d.textContent = niceDate(p); });
      post.classList.add('cl-tier-' + t.key, 'cl-ready');

      var span = post.querySelector('.cl-span');
      if (span) {
        var from = data.from, to = data.to + 1;
        var pos = epilogue ? 1 : Math.min(1, Math.max(0, (p.y + (p.m - 1) / 12 + (p.d - 1) / 365 - from) / (to - from)));
        span.style.setProperty('--pos', pos.toFixed(4));
        setText(span, '.cl-span-from', String(data.from));
        setText(span, '.cl-span-to', String(data.to));
        var dot = span.querySelector('b');
        if (dot) dot.setAttribute('data-label', epilogue ? 'Epilogue ' + p.y : String(p.y));
      }
      if (!epilogue && doc.body.classList.contains('item-view') && post.closest('.Blog')) {
        doc.body.style.setProperty('--age', Math.min(1, age / 15).toFixed(3));
        var card = post.closest('.post-outer-container');
        if (card) card.style.setProperty('--age', Math.min(1, age / 15).toFixed(3));
      }
    });
  }

  /* ---------- Ledger: year dividers between entries ---------- */
  function yearMarks() {
    if (doc.body.classList.contains('item-view')) return;
    var last = null;
    $$('.Blog .blog-posts > .post-outer-container').forEach(function (art) {
      var d = art.querySelector('[data-cl-date]');
      var p = d && parseISO(d.getAttribute('data-cl-date'));
      if (!p || p.y === last) return;
      last = p.y;
      var mark = el('div', 'cl-yearmark', '<b>' + p.y + '</b>');
      mark.setAttribute('role', 'separator');
      art.parentNode.insertBefore(mark, art);
    });
  }

  /* ---------- Totals ---------- */
  function totals(data) {
    $$('[data-cl-total]').forEach(function (n) { n.textContent = String(data.total); });
    $$('[data-cl-range]').forEach(function (n) { n.textContent = data.from + '–' + data.to; });
  }

  /* ---------- Code blocks: caption, copy, highlight ---------- */
  var LANG_ALIASES = { html: 'xml', xhtml: 'xml', js: 'javascript', ts: 'typescript', sh: 'bash', shell: 'bash', yml: 'yaml', kt: 'kotlin' };

  function langOf(pre) {
    var code = pre.querySelector('code');
    var cls = ((code && code.className) || '') + ' ' + (pre.className || '');
    var m = /language-([\w+-]+)/.exec(cls) || /brush:\s*([\w+-]+)/.exec(cls) || /\blang-([\w+-]+)/.exec(cls);
    return m ? m[1].toLowerCase() : '';
  }

  function decorateCode() {
    var post = doc.querySelector('.item-view .Blog [data-cl-date]');
    var p = post && parseISO(post.getAttribute('data-cl-date'));
    var pres = $$('.item-view .post-body pre');
    pres.forEach(function (pre) {
      if (pre.parentNode.classList && pre.parentNode.classList.contains('cl-code')) return;
      var lang = langOf(pre);
      pre.setAttribute('data-cl-lang', lang);
      var fig = el('figure', 'cl-code');
      var cap = el('figcaption', null,
        '<span class="cl-code-lang">' + (lang || 'code') + '</span>' +
        (p ? '<span class="cl-code-asof">as of ' + p.y + '</span>' : '') +
        '<button type="button" class="cl-code-copy">Copy</button>');
      pre.parentNode.insertBefore(fig, pre);
      fig.appendChild(cap);
      fig.appendChild(pre);
      cap.querySelector('button').addEventListener('click', function () {
        var btn = this, text = pre.innerText.replace(/\n$/, '');
        var done = function () {
          btn.textContent = 'Copied'; btn.classList.add('is-done');
          setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('is-done'); }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
        else {
          var ta = el('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
          doc.body.appendChild(ta); ta.select();
          try { doc.execCommand('copy'); done(); } catch (e) {}
          doc.body.removeChild(ta);
        }
      });
    });
    if (pres.length) loadHighlighter(pres);
  }

  function loadScript(src, cb) {
    var s = doc.createElement('script');
    s.src = src; s.async = true; s.onload = cb; s.onerror = function () {};
    doc.head.appendChild(s);
  }

  function loadHighlighter(pres) {
    if (!CFG.hljs) return;
    loadScript(CFG.hljs + 'highlight.min.js', function () {
      loadScript(CFG.hljs + 'languages/groovy.min.js', function () {
        var hljs = window.hljs;
        if (!hljs) return;
        hljs.configure({ ignoreUnescapedHTML: true });
        pres.forEach(function (pre) {
          var target = pre.querySelector('code') || pre;
          var lang = LANG_ALIASES[pre.getAttribute('data-cl-lang')] || pre.getAttribute('data-cl-lang');
          // Unlabelled blocks: Java is by far the most common language here, so recognise it first.
          if (!lang && /^\s*(package|import)\s+[\w.]+(\.\*)?;|\b(public|private|protected)\s+(static\s+)?(final\s+)?(class|interface|void|enum)\b/m.test(target.textContent)) {
            lang = 'java';
            pre.setAttribute('data-cl-lang', 'java');
            var cl = pre.parentNode.querySelector('.cl-code-lang');
            if (cl) cl.textContent = 'java';
          }
          try {
            if (lang && hljs.getLanguage(lang)) {
              target.innerHTML = hljs.highlight(target.textContent, { language: lang, ignoreIllegals: true }).value;
            } else {
              var r = hljs.highlightAuto(target.textContent, ['java', 'xml', 'javascript', 'typescript', 'bash', 'json', 'yaml', 'groovy', 'properties', 'sql']);
              if (r.relevance >= 6) {
                target.innerHTML = r.value;
                if (!pre.getAttribute('data-cl-lang')) {
                  var l = pre.parentNode.querySelector('.cl-code-lang');
                  if (l) l.textContent = r.language;
                }
              }
            }
            target.classList.add('hljs');
          } catch (e) {}
        });
      });
    });
  }

  /* ---------- Reading progress ---------- */
  function progress() {
    var art = doc.querySelector('.item-view .Blog .post-body');
    if (!art) return;
    var bar = el('div', 'cl-progress', '<span></span>');
    bar.setAttribute('aria-hidden', 'true');
    doc.body.appendChild(bar);
    var ticking = false;
    function update() {
      ticking = false;
      var r = art.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var v = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
      bar.style.setProperty('--p', v.toFixed(4));
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  function init() {
    var data = readYears();
    totals(data);
    renderTimeline(data);
    enhanceArchiveRail(data);
    decoratePosts(data);
    yearMarks();
    decorateCode();
    progress();
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init);
  else init();
})();
