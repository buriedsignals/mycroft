# Manual installation with Engine

For guided setup, use [Install with Indicator Lab](https://indicator.media/indicator-lab).
The Mycroft Osaurus installation is for Mac. Engine support for other operating systems does
not imply Mycroft supports those platforms.

Buried Signals Engine (`bsig`) is the installation authority. It installs a
catalogue-pinned public commit, its runtime dependencies, agents and skills.
A clone of this repository is source code, not a configured installation.

## Installation routes

Indicator’s Lab-tier members install through Indicator Lab, using Engine for
setup, repair and updates. Use the member interface to obtain managed software.

You may also use this public repository to experiment with self-managed setup.
It contains Mycroft’s instructions, skills and Analyst dependency pins; it does
not include Engine or the models. The commands below assume you already have
Engine. Private artifact download endpoints are not part of this guide.

## Configure and apply

```sh
bsig catalog sync
bsig --json configure describe mycroft
```

Use the returned descriptor to select supported configuration values; do not
copy old model ids or runtime names from examples. Submit the configuration
JSON on stdin to `bsig configure plan mycroft`. Review the emitted `plan.json`,
then apply the approved plan with `bsig apply <path-to-plan.json>`.

Preflight and `bsig keys list` identify optional provider credential ids.
A trusted local agent may prepare Engine's protected stdin/keychain flow,
but enter each credential only through a private operating-system or terminal
prompt. Never put credentials in chat, argv, shell history or repository files.
There is no Mycroft localhost credential form.

For updates, use `bsig plan update mycroft`, review the resulting plan and apply
it. Indicator Lab manages the same Engine lifecycle through its interface.

## After installation

Open Osaurus to use Mycroft and Spotlight. OpenKnowledge holds your wiki.
The Analyst proposes wiki changes for you to confirm; it also has an
OpenKnowledge agent entry. If it is not enabled there, open OpenKnowledge's
Settings → Agent connections.

Navigator and Scoutpost require their service connections. Cloud research
requires the corresponding provider setup; it is separate from local inference.
The installer preview on the website is a design reference, not a guarantee
that every installed version has the same interface.

## Retired installation paths

Goose is no longer a Mycroft runtime. Old recipe and website-installer
instructions do not apply. [`install.sh`](../install.sh) remains only to make
legacy `curl | bash` commands fail closed; it downloads and installs nothing.
