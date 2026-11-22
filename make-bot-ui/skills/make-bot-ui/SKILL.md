---
name: make-bot-ui
description: Use when the user wants a page whose controls wake a bot through a webhook they supply, including "봇 깨우는 버튼 페이지 만들어줘", "웹훅으로 봇 부르는 UI", "make a page that wakes the bot", "buttons that POST to my webhook", "/make-bot-ui", or "$make-bot-ui". Builds a page and a local server. The user gives the webhook URL. The sender key stays in server-side config. A key pasted in chat is refused and is never written into the page or the transcript. The local server sends the POST, and the browser only talks to that server. For a cited question about an API use research-brief.
---

# Make Bot UI

Build a page the user clicks. A server on this computer POSTs JSON to a
webhook the user already has. The bot wakes with that JSON.

The webhook URL comes from the user. The sender key stays in server-side
config. A key pasted in chat is refused. Do not place the key in the page or
the transcript. The local server, not the browser, sends the POST.

Use `scripts/webhook_post.py` next to this file for the page, the config
load, the refusal, and the POST. Do not reimplement those checks in prose.

## 1. Take the webhook URL, and only the URL

Ask for the webhook URL when the user has not given one. It must be `https`.
Do not invent a host, and do not look one up from a product you are not in.

A key pasted in chat is refused. Call `refuse_pasted_key` with the message
and the key when you were handed a key, and stop that turn. The refusal does
not repeat the key. Tell the user to put the key in the server config file
themselves. Do not ask them to paste it again.

## 2. Keep the key in the server config

The config is a JSON file in the UI's own directory, `{ "url", "key" }`,
mode `0600` when the host can set it. `load_server_config` is the only reader.
The page builder has no key argument. Do not print the key, do not log it,
and do not copy it into a transcript, a comment, or a fixture that ships.

If you can see the key because it was pasted, treat that as the refusal in
step 1. You do not copy a seen key into the config. The user writes the file.

## 3. Build the page so it cannot reach the webhook

`render_page` takes a title and controls. Each control is an id and a label.
The button posts to `/send/<id>` on this server. The payload for that id
lives in server code, next to the config, and is not a hidden field.

Run `reject_page` on the HTML with the key and the webhook URL before you
save the file. A failure means the page is wrong. Fix the page. Do not ship
it. Do not place the key in the page or the transcript.

## 4. Send from the server

`build_server_post` builds one POST. The key is the `Authorization` header.
The body is the control's JSON and nothing else. The timeout is 8 seconds.
`retries` is 0. The browser never sees this request.

Bind the server to a local port the user can open. Do not install a network
tunnel, and do not claim the page is reachable beyond this computer unless
the user has already exposed the port themselves.

Before you say the button works, send one harmless payload the bot can
ignore, from the server, and report the status code. A skipped probe is not
a working button.

## 5. Report what the user can click

Name the local URL, the control ids, and where the config file is. Say that
the key was not read back. Do not echo the URL's query if the user put a
secret in it. Ask them to rotate that URL and send a clean one.

## Refusals

- Do not accept a sender key in chat, and do not repeat one that arrives.
- Do not put the key or the webhook host in the page.
- Do not let the browser POST to the webhook. The local server sends it.
- Do not retry a failed POST.
- Do not invent a webhook the user did not supply.
- Do not research an API in place of building the page. That is
  `research-brief`.

## Integration

**Pairs with:** `bug-hunt` when a button the user already has fails, and
`gen-docs` when the page needs a short usage note.

**Use instead of:** `research-brief` when the question is what a webhook API
does, and `arena` when the user wants several page designs raced.
