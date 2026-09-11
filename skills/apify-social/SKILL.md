---
name: apify-social
description: Collect public social-media posts and comments through Apify actors — Instagram, Facebook, TikTok, LinkedIn, and X — via the apify-* recipes or a curl fallback. Use when a journalist needs a bounded, cost-capped pull of posts from a named account or post; every run leaves the device and costs money, and X collection breaks X's terms.
requires: [shell-safety]
---

# Apify Social

Use this skill when the user wants posts, comments, or videos from a specific social
account, post, or keyword and the local acquisition stack (SearXNG/Crawl4AI/Firecrawl)
cannot reach behind the platform's login or rate limits. Apify is a third-party service:
the target URL and the returned content leave the device, and each run is billed.

Do not use this skill for web pages, PDFs, or news sites — that is `web-acquisition`.
Do not use it to build a profile of a private individual without an editorial reason
the user can state.

**Always load `shell-safety` first.** Actor inputs carry user-supplied URLs and keywords;
they go into a JSON file, never into a shell string.

## Before collecting

Record the collection authority in the run note: who asked, why, which account or post,
and how many items. This is the line an editor or lawyer will ask for later.

| Platform | Recipe | Actor | Terms note |
|---|---|---|---|
| Instagram profile posts | `apify-instagram` | `apidojo/instagram-scraper` | Public profiles only. |
| Instagram post comments | `apify-instagram-comments` | `apify/instagram-comment-scraper` | Post or reel URL, not a profile. |
| Facebook page/profile posts | `apify-facebook` | `cleansyntax/facebook-profile-posts-scraper` | Public pages only. |
| TikTok user videos | `apify-tiktok` | `novi/tiktok-user-api` | Public accounts only. |
| LinkedIn post search | `apify-linkedin` | `curious_coder/linkedin-post-search-scraper` | Rate-limited; zero results may mean throttling, retry later. |
| X / Twitter | `apify-x` | apidojo actor `61RPP7dywgiy0JPD0` | X's post-2023 terms prohibit automated collection without X's written consent, public posts included. Running this actor is a terms violation; only do it with a stated editorial justification and the editor's sign-off in the run note. |

Unsure which one fits? `apify-select-actor` maps a plain-language intent (platform +
target) to the recipe and normalizes the URL.

## How to run

From a terminal, by recipe name (Goose resolves it on `GOOSE_RECIPE_PATH`; a `/` in the
name would be read as a file path, which is why these recipes live flat under `recipes/`):

```sh
goose run --recipe apify-instagram --params url="https://www.instagram.com/some.handle/" --params max_items=50
```

Goose Desktop: open the recipe picker and choose the `Apify social — …` entry.

Each recipe caps `max_items` (100 for posts, 500 for comments), writes the raw dataset
to `/tmp/apify-<platform>-<pid>.json`, and returns the count, a top-5 inline sample,
and the file path. Reference the file; do not paste the whole dataset into chat.

## REST fallback

When a recipe cannot run (no Goose CLI, a parameter the recipe does not expose), call the
run-sync endpoint directly. Write the actor input to a file first so user text never
reaches the shell line:

```sh
cat > /tmp/apify-input-$$.json <<'EOF'
{"startUrls": ["https://www.instagram.com/some.handle/"], "maxItems": 50}
EOF

curl -sS -X POST \
  "https://api.apify.com/v2/acts/<actor-id>/run-sync-get-dataset-items?token=${APIFY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @/tmp/apify-input-$$.json \
  -o /tmp/apify-<platform>-$$.json

jq 'length' /tmp/apify-<platform>-$$.json
```

Actor ids and input field names are in the matching `recipes/apify-<platform>.yaml`;
copy them from there rather than from memory. Never `echo` the URL, never run with
`set -x`, and never write the token into a file or a note.

## The token

`APIFY_API_TOKEN` is read from the environment. On an Engine install with Apify
connected (`bsig configure describe mycroft`, "Apify social data"), it comes from the
Engine keychain and is injected at exec time by `bsig run mycroft`; store it with:

```sh
bsig keys set APIFY_API_TOKEN
```

Without the Engine, export it in the shell that launches Goose. If the variable is
unset, stop and say so; do not ask the user to paste the token into chat.

## Output

Normalize every item to the `NormalizedPost` shape the recipes describe (`platform`,
`handle`, `post_url`, `timestamp`, `text`, engagement counts, `media_urls[]`). Treat
the result as leads: verify any quote, figure, or attribution before it enters the
vault, and record the actor, run date, item count, and cost estimate as an evidence
item alongside the collection authority.
