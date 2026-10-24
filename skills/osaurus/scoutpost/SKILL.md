---
name: scoutpost
description: Turn research into Scoutpost page and social monitors, and read what they find, with Scoutpost's tools in Osaurus. Use when the member wants to watch a web page or a public social profile for a case, or asks what the monitors found.
version: 1.0.0
author: Buried Signals
---

# Scoutpost

Scoutpost watches pages and public social profiles on a schedule and extracts source-linked information units. Your job here is to turn the member's research, often from Spotlight, into monitors, and to report what the monitors find.

Osaurus asks the member before Scoutpost creates anything, and shows the call's details. If Scoutpost isn't connected, tell the member to sign in to Scoutpost when Osaurus asks. Never ask for a key.

Create only two kinds of monitor:

- **Page monitor** (`type: "web"`): one URL, alerting on changes.
- **Social monitor** (`type: "social"`): one public profile on `instagram`, `x`, `facebook`, `tiktok` or `linkedin`. For LinkedIn, only personal profiles, given as the full `linkedin.com/in/...` URL; other platforms take the account handle.

Don't create any other scout type.

## Setting up monitors for a case

1. `scoutpost_list_projects`. If no project has this case's name, create it with `scoutpost_create_project`: the case name as `name`, and `case:<case-slug>` in `tags`.
2. `scoutpost_list_scouts`, so you don't create a monitor that already exists.
3. For a page monitor, run `scoutpost_test_web_scout` with the `url` (and `criteria` if the member wants specific alerts). If it returns `ok: false`, tell the member why and fix the URL before going on.
4. `scoutpost_create_scout` with:
   - `name`: short, says what is watched;
   - `type`: `web` or `social`;
   - `project_id`: the case's project;
   - `topic`: one to three short tags, for example `procurement, lenders`;
   - for `web`: `url`, and `criteria` in one plain sentence when the member wants only some changes (leave it out for any change);
   - for `social`: `platform` and `profile_handle`, and either `criteria` with the member's filter or `monitor_mode: "summarize"` to collect every new post;
   - `regularity`: `daily` unless the member asks otherwise.
5. Tell the member what you created, and that each run spends Scoutpost credits.

Monitor only public pages and public profiles, for a public-interest reason. Never monitor a confidential source, and never put anything that could identify one in any project or monitor field: name, tags, URL, handle, topic, description or criteria. If the member asks for that, explain why and stop.

## Reading what the monitors found

1. `scoutpost_list_units`, filtered by `project_id` or `scout_id`.
2. `scoutpost_get_unit` for the full text and source of one unit.

Every unit carries a verification state. Unverified units are leads, not facts. Always give the source URL and say whether the unit is verified.
