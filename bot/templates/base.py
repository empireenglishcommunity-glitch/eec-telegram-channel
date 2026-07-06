"""
Base HTML template — shared styles across all pillar templates.
Fonts: Cinzel (brand headings), Cairo (Arabic body), Inter (English body).
Colors: Gold (#D4AF37), Dark (#0A0A0F), Light text (#F5F0E8).
"""

BASE_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Cinzel:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  width: 1080px;
  height: 1080px;
  background: #0A0A0F;
  overflow: hidden;
  position: relative;
  direction: rtl;
}

/* Noise texture overlay */
body::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.03;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Gold radial glow */
body::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse at 50% 30%, rgba(212,175,55,0.08) 0%, transparent 60%);
}

.container {
  width: 100%;
  height: 100%;
  padding: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  direction: ltr;
}

.pillar-icon {
  font-size: 48px;
  filter: drop-shadow(0 0 20px rgba(212,175,55,0.5));
}

.pillar-label {
  font-family: 'Cinzel', serif;
  font-weight: 700;
  font-size: 22px;
  color: #D4AF37;
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* Gold accent line */
.gold-line {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #D4AF37, rgba(212,175,55,0.3), transparent);
  margin: 30px 0;
}

/* Main content */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 24px;
}

.title-ar {
  font-family: 'Cairo', sans-serif;
  font-weight: 900;
  font-size: 44px;
  color: #F5F0E8;
  direction: rtl;
  text-align: right;
  line-height: 1.5;
}

.subtitle-ar {
  font-family: 'Cairo', sans-serif;
  font-weight: 600;
  font-size: 32px;
  color: rgba(245,240,232,0.7);
  direction: rtl;
  text-align: right;
  line-height: 1.6;
}

.english-highlight {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 38px;
  color: #D4AF37;
  letter-spacing: 1px;
  direction: ltr;
  text-align: left;
}

.examples {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 20px 0;
}

.example-item {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 30px;
  color: #F5F0E8;
  padding: 12px 24px;
  background: rgba(212,175,55,0.08);
  border-left: 3px solid #D4AF37;
  border-radius: 8px;
  direction: ltr;
  text-align: left;
}

/* Footer */
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid rgba(212,175,55,0.15);
  direction: ltr;
}

.brand {
  font-family: 'Cinzel', serif;
  font-weight: 600;
  font-size: 16px;
  color: rgba(212,175,55,0.6);
  letter-spacing: 2px;
}

.channel-handle {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: rgba(245,240,232,0.4);
}
"""


def wrap_html(inner_content: str, extra_styles: str = "") -> str:
    """Wrap content in the base HTML template."""
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
{BASE_STYLES}
{extra_styles}
</style>
</head>
<body>
<div class="container">
{inner_content}
<div class="footer">
    <span class="brand">EMPIRE ENGLISH</span>
    <span class="channel-handle">@Empire_English_Community</span>
</div>
</div>
</body>
</html>"""
