"""
Pillar-specific HTML templates.
Each function takes dynamic content and returns full HTML ready for HTML2IMG.
"""
from .base import wrap_html


def accent_lesson(topic: str, examples: list[str] = None) -> str:
    """🎯 Accent Lesson template — sound/pronunciation focus."""
    examples_html = ""
    if examples:
        items = "".join(f'<div class="example-item">{ex}</div>' for ex in examples[:4])
        examples_html = f'<div class="examples">{items}</div>'

    inner = f"""
    <div class="header">
        <span class="pillar-icon">🎯</span>
        <span class="pillar-label">Accent Lesson</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="english-highlight">{topic}</div>
        {examples_html}
    </div>
    """

    extra = """
    .content { justify-content: center; }
    """
    return wrap_html(inner, extra)


def myth_destroyer(myth_text: str) -> str:
    """💣 Myth Destroyer template — bold myth statement crossed out."""
    inner = f"""
    <div class="header">
        <span class="pillar-icon">💣</span>
        <span class="pillar-label">Myth Destroyer</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="myth-text">{myth_text}</div>
        <div class="myth-cross">❌</div>
    </div>
    """

    extra = """
    .content {
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
    }
    .myth-text {
        font-family: 'Cairo', sans-serif;
        font-weight: 900;
        font-size: 42px;
        color: #F5F0E8;
        direction: rtl;
        line-height: 1.6;
        padding: 40px;
        position: relative;
    }
    .myth-text::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 10%;
        width: 80%;
        height: 4px;
        background: #e74c3c;
        transform: rotate(-3deg);
        opacity: 0.8;
    }
    .myth-cross {
        font-size: 80px;
        margin-top: 30px;
        filter: drop-shadow(0 0 30px rgba(231,76,60,0.5));
    }
    """
    return wrap_html(inner, extra)


def system_reveal(title: str, bullets: list[str] = None) -> str:
    """🏛️ System Reveal template — system feature showcase."""
    bullets_html = ""
    if bullets:
        items = "".join(f'<li>{b}</li>' for b in bullets[:5])
        bullets_html = f'<ul class="system-bullets">{items}</ul>'

    inner = f"""
    <div class="header">
        <span class="pillar-icon">🏛️</span>
        <span class="pillar-label">Inside The System</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="title-ar">{title}</div>
        {bullets_html}
    </div>
    """

    extra = """
    .system-bullets {
        list-style: none;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    .system-bullets li {
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        font-size: 28px;
        color: #F5F0E8;
        direction: rtl;
        text-align: right;
        padding: 16px 24px;
        padding-right: 30px;
        border-right: 3px solid #D4AF37;
        background: rgba(212,175,55,0.05);
        border-radius: 8px;
    }
    .system-bullets li::before {
        content: '⚡ ';
    }
    """
    return wrap_html(inner, extra)


def social_proof(stat_number: str, stat_label: str) -> str:
    """🔥 Social Proof template — big number/stat highlight."""
    inner = f"""
    <div class="header">
        <span class="pillar-icon">🔥</span>
        <span class="pillar-label">Empire Numbers</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="big-stat">{stat_number}</div>
        <div class="stat-label">{stat_label}</div>
    </div>
    """

    extra = """
    .content {
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .big-stat {
        font-family: 'Cinzel', serif;
        font-weight: 900;
        font-size: 120px;
        color: #D4AF37;
        text-shadow: 0 0 60px rgba(212,175,55,0.4), 0 0 120px rgba(212,175,55,0.2);
        line-height: 1;
    }
    .stat-label {
        font-family: 'Cairo', sans-serif;
        font-weight: 700;
        font-size: 34px;
        color: rgba(245,240,232,0.8);
        direction: rtl;
        margin-top: 30px;
        line-height: 1.5;
    }
    """
    return wrap_html(inner, extra)


def brand_story(quote: str) -> str:
    """👑 Brand Story template — powerful quote/statement."""
    inner = f"""
    <div class="header">
        <span class="pillar-icon">👑</span>
        <span class="pillar-label">MACAL Empire</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="brand-quote">{quote}</div>
    </div>
    """

    extra = """
    .content {
        justify-content: center;
        align-items: center;
    }
    .brand-quote {
        font-family: 'Cairo', sans-serif;
        font-weight: 900;
        font-size: 46px;
        color: #F5F0E8;
        direction: rtl;
        text-align: center;
        line-height: 1.7;
        padding: 20px 40px;
        border-top: 2px solid rgba(212,175,55,0.3);
        border-bottom: 2px solid rgba(212,175,55,0.3);
    }
    .brand-quote::before {
        content: '"';
        display: block;
        font-family: 'Cinzel', serif;
        font-size: 80px;
        color: #D4AF37;
        opacity: 0.4;
        line-height: 0.5;
        margin-bottom: 20px;
    }
    """
    return wrap_html(inner, extra)


def invitation(cta_text: str, subtitle: str = "") -> str:
    """📢 Invitation template — CTA/action post."""
    subtitle_html = f'<div class="inv-subtitle">{subtitle}</div>' if subtitle else ""

    inner = f"""
    <div class="header">
        <span class="pillar-icon">📢</span>
        <span class="pillar-label">Join Empire</span>
    </div>
    <div class="gold-line"></div>
    <div class="content">
        <div class="inv-cta">{cta_text}</div>
        {subtitle_html}
        <div class="inv-arrow">→</div>
    </div>
    """

    extra = """
    .content {
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .inv-cta {
        font-family: 'Cairo', sans-serif;
        font-weight: 900;
        font-size: 44px;
        color: #F5F0E8;
        direction: rtl;
        line-height: 1.6;
    }
    .inv-subtitle {
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        font-size: 28px;
        color: rgba(245,240,232,0.6);
        direction: rtl;
        margin-top: 20px;
    }
    .inv-arrow {
        font-size: 64px;
        color: #D4AF37;
        margin-top: 40px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: translateX(0); }
        50% { opacity: 0.6; transform: translateX(10px); }
    }
    """
    return wrap_html(inner, extra)
