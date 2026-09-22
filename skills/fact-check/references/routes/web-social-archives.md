# Route: web pages, social posts, images and archives

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


Claims about what a page, post, image or video showed — and whether it
still shows it, or ever did. These are the claims where the browser
earns its place: the evidence is a specific rendered page, often behind
a login or a script wall, and fetch cannot see it.

## Was this page like this?

- `python3 "$MYCROFT_DIR/tools/evidence-lookup.py" wayback URL --at YYYYMMDD` returns the
  nearest Internet Archive snapshot. Compare the snapshot with the live
  page for "the company quietly changed…" and "the post has since been
  deleted" claims. archive.today (archive.ph) is the other big archive;
  search it in the browser.
- `evidence-lookup.py wayback-save URL` captures the live page now, so the
  version you checked stays citable after it changes.

## Did this post exist, and what did it say?

- X/Twitter: open the post URL in the browser; a deleted post shows an
  error page, which is itself evidence. Search the exact wording in the
  Wayback Machine and archive.ph — viral posts are usually archived.
- Bluesky, Threads, Mastodon: public, fetch usually works; browser if not.
- Facebook, Instagram, TikTok, LinkedIn: browser, and usually the user's
  own login. Note that the view is theirs.
- Telegram public channels: t.me/s/CHANNEL renders without login.
- Truth Social: trumpstruth.org for Trump; other accounts via browser.
- Screenshots of posts circulating as evidence prove nothing on their
  own; find the post or its archive.

## Images and video

- Reverse image search runs only in a browser: Google Lens
  (lens.google.com), TinEye (tineye.com), Bing Visual Search, Yandex. Use
  two. The goal is the earliest appearance and original context.
- Check the file itself when available: EXIF (`exiftool` if installed),
  visible dates, weather, shadows, signage, licence plates against the
  claimed place and time.
- For video: InVID/WeVerify browser extension if the user has it;
  otherwise keyframe screenshots into reverse image search.

## Has someone already checked this?

- `evidence-lookup.py factcheck "claim"` queries Google's Fact Check Tools API
  (free key); without a key, search toolbox.google.com/factcheck/explorer
  in the browser. It aggregates ClaimReview from IFCN-signatory and other
  fact-checkers worldwide, in many languages.
- A prior fact-check is a strong lead and one source; read its evidence
  and cite the primary record it found, not the fact-check alone.

## Traps

- Wayback timestamps are UTC; convert before saying "before" or "after".
- An archived page can be of a cached or logged-out view; the live page
  the author saw may have differed.
- Search engines' cached copies are gone; the archives are the record.
