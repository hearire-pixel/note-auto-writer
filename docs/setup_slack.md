# Slack Integration Setup

This document explains how to set up the Slack integration for the automatic article generation system.

## Overview

The system works as follows:

1. You type `/note <memo>` in Slack
2. The Slack bot triggers a GitHub Actions workflow via `repository_dispatch`
3. GitHub Actions runs `scripts/generate_posts.py` using Claude API
4. Generated drafts are committed to the `drafts/` directory
5. Slack receives a completion notification via webhook

## Slack App Setup

### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App** > **From scratch**
3. Name the app (e.g., `HIRO Note Writer`) and select your workspace
4. Click **Create App**

### 2. Configure Slash Command

1. In the app settings, go to **Slash Commands**
2. Click **Create New Command**
3. Fill in:
   - Command: `/note`
   - Request URL: `https://<your-server>/slack/events`
   - Short Description: `Generate a note article`
   - Usage Hint: `[memo text] [platforms:note,instagram,x]`
4. Save

### 3. Configure Bot Token Scopes

1. Go to **OAuth & Permissions**
2. Under **Bot Token Scopes**, add:
   - `commands`
3. Click **Install to Workspace**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### 4. Get Signing Secret

1. Go to **Basic Information**
2. Under **App Credentials**, copy the **Signing Secret**

### 5. Configure Incoming Webhook (for notifications)

1. Go to **Incoming Webhooks**
2. Toggle **Activate Incoming Webhooks** to On
3. Click **Add New Webhook to Workspace**
4. Select the channel for notifications
5. Copy the **Webhook URL**

### 6. (Optional) Socket Mode for Local Testing

1. Go to **Socket Mode** and enable it
2. Go to **Basic Information** > **App-Level Tokens**
3. Click **Generate Token and Scopes**
4. Add scope `connections:write`
5. Copy the token (starts with `xapp-`)

## GitHub Secrets

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

| Secret Name | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL for notifications |

## Environment Variables for slack_trigger.py

Set these when running the Slack bot server:

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token (xoxb-...) |
| `SLACK_SIGNING_SECRET` | App Signing Secret |
| `SLACK_APP_TOKEN` | App-Level Token for Socket Mode (xapp-...), optional |
| `GITHUB_TOKEN` | GitHub Personal Access Token with `repo` scope |
| `GITHUB_REPO` | Repository in `owner/repo` format (e.g., `yourname/note-auto-writer`) |
| `PORT` | Port for HTTP mode (default: 3000) |

## Local Testing

### Install dependencies

```bash
pip install slack-bolt requests
```

### Run in Socket Mode (recommended for local testing)

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_SIGNING_SECRET=...
export SLACK_APP_TOKEN=xapp-...
export GITHUB_TOKEN=ghp_...
export GITHUB_REPO=yourname/note-auto-writer

python scripts/slack_trigger.py
```

### Test the slash command

In Slack, type:
```
/note 今日、病院の帰り道に一枚の葉っぱが落ちてきた。
```

Or with platform selection:
```
/note platforms:note,instagram 今日、空がとても綺麗だった。
```

### Test generate_posts.py directly

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export INPUT_MEMO="今日、病院の帰り道に一枚の葉っぱが落ちてきた。"
export INPUT_PLATFORMS="all"

python scripts/generate_posts.py
```

## Manual Trigger via GitHub Actions

You can also trigger the workflow manually from the GitHub Actions UI:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Generate note draft**
4. Click **Run workflow**
5. Fill in the memo and platform fields
6. Click **Run workflow**

## Slash Command Usage

| Command | Description |
|---|---|
| `/note` | Generate posts for all platforms with no memo |
| `/note <memo>` | Generate posts with the given memo |
| `/note platforms:note <memo>` | Generate only note article |
| `/note platforms:instagram,x <memo>` | Generate Instagram and X posts |
