# Indicator Lab runtime packs

Indicator Lab installs its local runtimes (Python with SearXNG, Crawl4AI and LiteParse, Playwright's Chromium, and Node.js with the Lab's command-line tools) from one runtime pack per operating system and processor. The app downloads the pack itself and checks it against the SHA-256 in its signed catalog, so nobody needs to download these files by hand.

Each pack is published as a release of this repository, because a pack is too large to keep in git.

| Version | Platform | Download | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| 2026.10.23-1 | macOS, Apple silicon | [runtime-pack-2026.10.23-1-darwin-arm64.tar.gz](https://github.com/buriedsignals/mycroft/releases/download/runtime-pack-2026.10.23-1/runtime-pack-2026.10.23-1-darwin-arm64.tar.gz) | 589,403,416 | `6691b91e74b3388afb08e21bcac513b65c8f425fb0228d2a0f534205b06cad6c` |

Every executable in a macOS pack is signed with Buried Signals' Developer ID and notarized by Apple.

The licences of the software a pack contains are listed in [NOTICE.txt](NOTICE.txt), which each pack also carries as `licenses/NOTICE.txt`. SearXNG is included unmodified under the AGPL-3.0-or-later, and the notice gives the address of its complete source.
