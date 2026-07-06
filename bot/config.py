"""Configuration loader for EEC Channel Bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

# Channel Settings
CHANNEL_TITLE = os.getenv("CHANNEL_TITLE", "EEC | Announcements")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "EmpireEnglishClub")
CHANNEL_DESCRIPTION = os.getenv("CHANNEL_DESCRIPTION", "").replace("\\n", "\n")
DISCUSSION_GROUP_USERNAME = os.getenv("DISCUSSION_GROUP_USERNAME", "empireenglishcommunity")

# AI Providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")

# Kokoro TTS
KOKORO_URL = os.getenv("KOKORO_URL", "http://localhost:8880")

# Posting Schedule (UTC — Dubai is UTC+4)
POST_HOUR = int(os.getenv("POST_HOUR", "5"))  # 5 UTC = 9 AM Dubai
POST_MINUTE = int(os.getenv("POST_MINUTE", "0"))

# Reaction Settings
REACT_MIN_DELAY = int(os.getenv("REACT_MIN_DELAY", "900"))  # 15 min
REACT_MAX_DELAY = int(os.getenv("REACT_MAX_DELAY", "28800"))  # 8 hours

# Database
DB_PATH = os.getenv("DB_PATH", "data/channel.db")

# Emojis for reactions (weighted)
REACTION_EMOJIS = ["🔥", "🔥", "🔥", "🔥", "❤️", "❤️", "👍", "👍", "😍", "🎯"]

# Days of the week → pillar mapping (0=Monday, 5=Saturday, 6=Sunday)
# Our schedule: Sat(5)=AL, Sun(6)=SP, Mon(0)=MD, Tue(1)=AL, Wed(2)=SR, Thu(3)=BS/IN
PILLAR_SCHEDULE = {
    5: "accent_lesson",      # Saturday
    6: "social_proof",       # Sunday
    0: "myth_destroyer",     # Monday
    1: "accent_lesson",      # Tuesday (Empire Word)
    2: "system_reveal",      # Wednesday
    3: "brand_story",        # Thursday (alternates with invitation)
    # Friday (4) = OFF
}
