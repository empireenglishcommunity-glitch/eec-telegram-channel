# Deployment Guide — EEC Channel Bot (Telethon)

> **Server:** Hetzner VPS (77.42.43.250)
> **Location:** /opt/eec-channel-bot/
> **Runtime:** Python 3.11+, Docker optional

---

## Quick Deploy (5 Minutes)

### 1. SSH into server
```bash
ssh root@77.42.43.250
```

### 2. Clone the repo
```bash
cd /opt
git clone https://github.com/empireenglishcommunity-glitch/eec-telegram-channel.git eec-channel-bot
cd eec-channel-bot/bot
```

### 3. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
nano .env
# Fill in:
#   API_ID=your_api_id
#   API_HASH=your_api_hash
#   PHONE_NUMBER=+971XXXXXXXXX
#   GROQ_API_KEY=gsk_xxxxx
#   CLOUDFLARE_ACCOUNT_ID=xxxxx
#   CLOUDFLARE_API_TOKEN=xxxxx
```

### 5. First-time authentication
```bash
python setup_channel.py
# It will ask for your phone number verification code (one-time only)
# Then it creates the channel, sets username, pins welcome message
```

### 6. Run the main bot
```bash
python main.py
# Or for production: use systemd service (see below)
```

---

## Production Setup (systemd)

### Create service file
```bash
cat > /etc/systemd/system/eec-channel-bot.service << 'EOF'
[Unit]
Description=EEC Telegram Channel Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/eec-channel-bot/bot
ExecStart=/opt/eec-channel-bot/bot/.venv/bin/python main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and start
```bash
systemctl daemon-reload
systemctl enable eec-channel-bot
systemctl start eec-channel-bot
systemctl status eec-channel-bot
```

### View logs
```bash
journalctl -u eec-channel-bot -f
```

---

## First Run Flow

1. `python setup_channel.py` → asks for phone code → creates channel → saves session
2. Session is saved as `eec_session.session` — never asks for code again
3. `python main.py` → starts the scheduler → posts daily at 9 AM Dubai

---

## Update Flow

```bash
cd /opt/eec-channel-bot
git pull
systemctl restart eec-channel-bot
```

---

## File Structure (on server)

```
/opt/eec-channel-bot/bot/
├── .env                    ← Your credentials (NEVER commit)
├── eec_session.session     ← Telegram session (NEVER commit)
├── main.py                 ← Main bot (scheduler + posting + reactions)
├── setup_channel.py        ← One-time channel creation
├── config.py               ← Configuration loader
├── content_engine.py       ← Groq AI content generation
├── image_engine.py         ← Cloudflare Workers AI images
├── reaction_engine.py      ← Natural reaction system
├── engagement_engine.py    ← Discussion group seeding
├── requirements.txt        ← Python dependencies
└── data/
    ├── channel.db          ← SQLite (content queue, analytics)
    ├── channel_id.txt      ← Channel ID (auto-created by setup)
    └── bank/               ← Evergreen content bank (JSON)
```

---

## Safety Notes

- The session file (`eec_session.session`) gives FULL access to your Telegram account
- Keep it on the server only — NEVER commit to git
- If compromised: revoke all sessions in Telegram → Settings → Devices → Terminate all
- The bot only operates in YOUR channels/groups — zero spam risk
- Posting 1x/day to your own channel = near-zero ban risk
