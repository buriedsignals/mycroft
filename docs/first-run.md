# First Run

The installer is designed to leave the user in Goose, ready to choose a first reporting action.
The default Mycroft workspace is `~/Documents/OpenKnowledge/Mycroft`; Spotlight remains a sibling workspace at `~/Documents/OpenKnowledge/Spotlight`.

After setup:

1. If Spotlight is already installed, Mycroft records its workspace and case paths so Goose can launch Spotlight or read cases read-only. Mycroft does not install Spotlight. Install Spotlight separately through Indicator Labs or the signed open-source Engine path documented in Spotlight's README.
2. Goose opens the `start` recipe unless the user already has a morning brief monitoring profile.
3. The Mycroft knowledge project contains `START_HERE.md` with copy-paste starter prompts.

The `start` recipe offers:

- Set up my beat
- Add to my knowledge base
- Help me set up my morning brief
- Investigate a lead
- Set up scouts
- Show me a demo

The "Add to my knowledge base" path is the best default when the wiki is empty and the journalist has links, files, newsletters, pasted notes, PDFs, or folders. Wiki cleanup and audits are later workflows for existing note collections.

## What To Do Next

Start chatting with Mycroft in Goose and pick one first action. If you know your beat, start there. If you already have material, add it to the knowledge base. For a daily brief, say “Help me set up my morning brief.”

Then create a folder for investigations in the Spotlight vault and ask Mycroft to Spotlight it. Spotlight is the active casework space; Mycroft is the durable knowledge and publishing space.

## Morning Brief Setup

Say “Help me set up my morning brief” in Goose. This starts the interactive
`morning-brief-preflight` recipe; it is a prompt, not a desktop button.

Mycroft asks what to cover, which sources it may collect and disclose, when to
start, and whether to save in Goose/wiki only or also email an explicit
recipient through AgentMail. Newsletter subscriptions need their own approval.
The first result and real background execution must verify before recurrence
becomes active. Existing editorial preferences are suggestions for review,
not collection or delivery permission.

See [Schedules](schedules.md) for result locations, sleep/offline behavior,
controls, existing-install handover and platform limitations.
