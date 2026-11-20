---
description: Build a page whose controls wake a bot through a webhook the user supplies.
argument-hint: "[webhook url]"
---

Use the **make-bot-ui** skill.

The webhook URL comes from the user. Use `$ARGUMENTS` when it is a URL.
The sender key stays in server-side config. A key pasted in chat is refused.
Do not place the key in the page or the transcript. The local server, not the
browser, sends the POST.

Build the page with `scripts/webhook_post.py`. The page posts only to
`/send/<id>` on that server. Reject a page that contains the key or the
webhook host.
