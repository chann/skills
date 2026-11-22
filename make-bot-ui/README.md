# make-bot-ui

[한국어](README.ko.md) · [← back to main](../README.md)

Build a page whose controls wake a bot through a webhook you supply. The
sender key stays on the server. The browser never calls the webhook.

## Why it is different

A button that holds the sender key will leak it into the page, the logs, and
the chat that built it. This skill refuses that shape.

- The webhook URL comes from you.
- The sender key stays in server-side config. A key pasted in chat is refused.
- The key is not placed in the page or the transcript.
- The local server, not the browser, sends the POST.

`scripts/webhook_post.py` builds the page, rejects a page that contains the
key or the webhook host, and builds the one POST the server sends.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill make-bot-ui
```

Project-local:

```bash
npx skills add chann/skills --skill make-bot-ui
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/make-bot-ui [webhook url]` | `$make-bot-ui [webhook url]` | Build a page whose controls wake a bot through your webhook |

Examples:

```text
/make-bot-ui https://hooks.example.test/wake
$make-bot-ui a page with a ping button for the webhook I will give you
/make-bot-ui 이 웹훅으로 봇을 깨우는 버튼 페이지를 만들어줘
```

You write the sender key into the server config yourself. A question about
what a webhook API does is `research-brief`.

## What it refuses

- A sender key pasted in chat
- A page that contains the key or the webhook host
- A browser request that POSTs to the webhook
- A retry of a failed POST
- A webhook URL you did not supply

## Package layout

```text
make-bot-ui/
├── .claude-plugin/plugin.json
├── commands/make-bot-ui.md
├── skills/make-bot-ui/
│   ├── SKILL.md
│   ├── scripts/webhook_post.py
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Python 3.10+ for `scripts/webhook_post.py` (standard library only)

## License

MIT
