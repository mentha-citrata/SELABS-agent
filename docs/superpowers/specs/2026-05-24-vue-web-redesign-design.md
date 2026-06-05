# Vue Web Redesign Design

Date: 2026-05-24

## Goal

Redesign the current Vue Web client from a lightweight chat demo into a production-ready frontend skeleton for SELABS Agent. The product should act as a centralized entry point for lab management workflows, using conversation as the primary interaction model while supporting structured UI forms, safe Markdown rendering, and a smoother streaming experience.

The design covers both the Vue client and the minimum Agent API adjustments needed to make the experience coherent.

## Current State

The current Vue client is small:

- `web/vue/src/App.vue` renders a centered header and a single `Chat` component.
- `web/vue/src/components/Chat.vue` handles session creation, sending, EventSource streaming, and message rendering in one file.
- Assistant output is rendered with `v-html` directly.
- Streaming currently appends string chunks from `/api/agent/stream`.
- There is no structured message model, no Markdown safety layer, and no A2UI form renderer.

The current Agent API in `src/webserver.py` exposes:

- `POST /api/agent/session`
- `POST /api/agent/send`
- `GET /api/agent/stream`

The backend queue currently pushes `{ data: string }` chunks. `LabAgent.run_stream()` is a prototype that calls `run()` first and then splits the full response into fixed-size character chunks.

## Product Direction

Use the "Precision Lab Console" direction.

The interface should feel like a calm laboratory command console, not a generic SaaS dashboard. The conversation remains the primary workspace, with a right-side context panel acting like an instrumentation rail for login state, API status, recent form activity, and shortcuts.

Visual principles:

- Deep or low-brightness neutral surfaces.
- Thin technical borders.
- Status lights and compact data labels.
- Controlled density.
- Clear typography and strong hierarchy.
- Avoid generic card-heavy admin layouts and purple-gradient AI styling.

## Information Architecture

The main page consists of:

- Top status bar: product name, Agent API state, stream state, environment/status indicators.
- Main conversation workbench: Markdown responses, A2UI forms, user messages, system/error messages.
- Right context panel: login state, current user, recent form submissions, shortcuts, and Agent/backend state.
- Bottom input dock: multiline input, send action, retry/stop affordances, and room for future attachments or quick commands.

The first screen should communicate that this is a lab-management command entrance, not only a chatbot.

## Structured Streaming Protocol

Upgrade the SSE queue from string chunks to structured events.

Initial event types:

```json
{ "type": "message_start", "message_id": "..." }
{ "type": "markdown_delta", "message_id": "...", "content": "..." }
{ "type": "ui_block", "message_id": "...", "block": { "kind": "form" } }
{ "type": "tool_status", "status": "running", "label": "查询可用机位" }
{ "type": "message_done", "message_id": "..." }
{ "type": "error", "message": "..." }
```

Backend rules:

- Keep the existing API paths to avoid broad client churn.
- `POST /api/agent/session` still creates an in-memory session.
- `POST /api/agent/send` still starts Agent processing.
- `GET /api/agent/stream` now emits structured SSE payloads.
- Short term: the backend may still call `LabAgent.run()` and convert the complete result into `markdown_delta` events.
- Medium term: the same protocol can support true LLM streaming without changing frontend contracts.
- Errors must be sent as `error` events when possible instead of only closing the stream.

Frontend rules:

- `markdown_delta` appends to the current assistant message.
- `ui_block` appends a structured block to the current assistant message.
- `message_done` marks the assistant message complete.
- `error` marks the current operation failed and surfaces a retry path.

## A2UI Form Protocol

A2UI forms are structured blocks embedded in assistant messages. The frontend does not infer forms from text.

Initial block shape:

```json
{
  "kind": "form",
  "id": "seat_reservation_001",
  "title": "预约机位",
  "description": "选择房间、时间段和机位后提交。",
  "submitLabel": "提交预约",
  "fields": [
    {
      "name": "roomName",
      "label": "房间",
      "type": "select",
      "required": true,
      "options": ["A101", "B203"]
    },
    {
      "name": "startTime",
      "label": "开始时间",
      "type": "datetime",
      "required": true
    }
  ]
}
```

Initial field types:

- `text`
- `textarea`
- `number`
- `select`
- `datetime`
- `date`
- `checkbox`
- `hidden`

Submission flow:

1. User fills a form embedded in an assistant message.
2. Frontend validates required fields locally.
3. Frontend renders the submitted form as a read-only summary.
4. Frontend sends the submission back to Agent as a structured user message:

```json
{
  "kind": "a2ui_form_submit",
  "form_id": "seat_reservation_001",
  "values": {
    "roomName": "A101",
    "startTime": "2026-05-24 14:00:00"
  }
}
```

The Agent remains responsible for deciding which tool to call. The frontend does not call lab business APIs directly.

## Frontend Architecture

Split the current `Chat.vue` into focused units:

- `App.vue`: application shell entry.
- `components/WorkbenchShell.vue`: top-level console layout.
- `components/ConversationPanel.vue`: message list, scrolling, empty state, stream state.
- `components/MessageBubble.vue`: user, assistant, system, and error message rendering.
- `components/MarkdownRenderer.vue`: safe Markdown rendering.
- `components/A2UIForm.vue`: form rendering, validation, submit, read-only summary.
- `components/ContextPanel.vue`: login state, session state, shortcuts, recent form activity.
- `services/agentStream.js`: session creation, send, stream consumption, event normalization.
- `utils/a2ui.js`: schema helpers, defaults, validation, submit summary.
- `utils/markdown.js`: Markdown rendering and sanitization.

State stays local for the first production skeleton. Use Vue reactive state/composables rather than introducing Pinia immediately. If session and workflow complexity grows later, extract a store.

## Markdown Rendering

Add a safe Markdown rendering pipeline:

- `markdown-it` for Markdown parsing.
- `dompurify` for HTML sanitization.

Rules:

- Do not render raw assistant output directly with `v-html`.
- Markdown output is parsed and sanitized before insertion.
- A2UI blocks are not parsed from Markdown HTML; they are rendered as Vue components from structured event data.
- Support headings, lists, code blocks, tables, links, and inline formatting in the first version.

## Dependencies

Allowed new frontend dependencies:

- `markdown-it`
- `dompurify`
- `lucide-vue-next`

These are scoped to Markdown safety, rendering quality, and icon clarity. Avoid adding a UI framework in the first pass.

## Error Handling

Frontend should distinguish these states:

- Agent API offline: show in the status rail and disable or warn in the input area.
- SSE disconnected: mark current assistant message interrupted and offer retry.
- Business/auth error: render as assistant/system error message and reflect login need in the context panel.
- A2UI local validation error: show field-level error and do not send to Agent.
- A2UI submit followed by Agent failure: keep the submitted summary and allow retry.

Backend should prefer structured `error` SSE events over silent disconnects.

## Testing And Verification

Minimum verification:

- `npm run build` in `web/vue`.
- Manual dev flow with Agent API and Vite:
  - Start `python3 -m uvicorn src.webserver:app --reload --host 127.0.0.1 --port 8000`.
  - Start `npm run dev` in `web/vue`.
  - Verify session creation, send, stream rendering, and done/error states.
- Markdown examples:
  - headings
  - lists
  - fenced code blocks
  - tables
  - links
- A2UI examples:
  - form rendering
  - required field validation
  - submit summary
  - structured submission payload sent back to Agent

Regression expectations:

- Existing `/api/agent/session`, `/api/agent/send`, and `/api/agent/stream` routes remain present.
- Vite proxy to Agent API on port `8000` continues to work.

## First Implementation Scope

In scope:

- Replace the current Vue UI with the Precision Lab Console layout.
- Add structured event consumption in the frontend.
- Upgrade backend SSE queue payloads to structured events.
- Implement safe Markdown rendering.
- Implement A2UI form rendering and submit-back-to-Agent flow.
- Provide a demo path where backend can emit an A2UI `ui_block`.

Out of scope for the first pass:

- Full rewrite of `LabAgent` internals.
- True LLM-native streaming if it requires broad LangGraph callback work.
- Direct frontend calls to lab business APIs.
- Full form schema registry.
- Persistent conversation history.
- Authentication UI beyond reflecting current session/auth state and supporting future extension.

## Open Decisions Resolved

- Production-grade frontend skeleton, not only a high-fidelity demo.
- A2UI source is embedded structured UI blocks from Agent output.
- A2UI submissions go back to Agent as structured user messages.
- Streaming protocol is structured SSE events.
- Main layout is single conversation workbench plus right context panel.
- Visual direction is Precision Lab Console.
- Small stable dependencies are allowed.
