#!/usr/bin/env python3
"""
Cyberpunk 2077 / Edgerunners Netrunner Cyberdeck Profile Generator for PALPARD
Generates pixel-perfect, seamless SVG console slices for GitHub profile README.
"""

import json
import math
import os
import pathlib
import re
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
ASSETS_DIR = HERE / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Cyberpunk 2077 Authentic Color Palette
CP_YELLOW = "#FCEE0A"   # Cyberpunk 2077 Signature Yellow
CP_CYAN = "#00F0FF"     # Netrunner ICE Cyan
CP_RED = "#FF003C"      # Arasaka Combat Alert Red
CP_BLACK = "#070A0F"    # Deep Cyberdeck Void
CP_BG = "#0B0F19"       # Console Surface
CP_DIM = "#526075"      # Dim Terminal Text
CP_FG = "#D6DEEB"       # Terminal Light Text
CP_GREEN = "#00FF66"    # Daemon Verified Green

W, M = 880, 16
FL, FR = M, W - M       # 16, 864
X = 52                  # Text left margin

def fetch_calendar():
    """Fetch real GitHub contributions for PALPARD"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            with open('/home/hermes/.git-credentials', 'r') as f:
                line = f.read().strip()
            m = re.search(r'https://([^:]+):([^@]+)@github\.com', line)
            if m:
                token = m.group(2)
        except Exception:
            pass

    if not token:
        return []

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'login': 'PALPARD'}}).encode('utf-8'),
        headers={'Authorization': f'token {token}', 'User-Agent': 'Hermes-Agent', 'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
            calendar = []
            for w in weeks:
                for d in w['contributionDays']:
                    calendar.append((d['date'], d['contributionCount']))
            return calendar
    except Exception as e:
        print(f"Error fetching calendar: {e}")
        return []

# Base shared CSS & Defs
BASE_CSS = f"""
text {{
  font-family: ui-monospace, 'Cascadia Code', 'Fira Code', 'JetBrains Mono', Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
}}
.dim {{ fill: {CP_DIM}; }}
.fg {{ fill: {CP_FG}; }}
.cy {{ fill: {CP_CYAN}; }}
.yw {{ fill: {CP_YELLOW}; }}
.rd {{ fill: {CP_RED}; }}
.gr {{ fill: {CP_GREEN}; }}
.wh {{ fill: #FFFFFF; }}

@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.35; }} }}
@keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
@keyframes glitch-yw {{
  0%, 92%, 100% {{ transform: translate(0, 0); }}
  93% {{ transform: translate(4px, -1px); }}
  95% {{ transform: translate(-3px, 2px); }}
  97% {{ transform: translate(2px, 0); }}
}}
@keyframes glitch-cy {{
  0%, 92%, 100% {{ transform: translate(0, 0); }}
  93% {{ transform: translate(-4px, 1px); }}
  95% {{ transform: translate(3px, -2px); }}
  97% {{ transform: translate(-2px, 0); }}
}}
@keyframes fly-av {{
  from {{ transform: translate({FL - 60}px, 0); }}
  to {{ transform: translate({FR + 60}px, -35px); }}
}}
@keyframes av-beacon {{ 0%, 90%, 100% {{ opacity: 0; }} 92%, 98% {{ opacity: 1; }} }}
@keyframes scanline {{ from {{ transform: translateY(0); }} to {{ transform: translateY(360px); }} }}

.cursor {{ animation: blink 1s step-end infinite; }}
.dot-live {{ animation: pulse 1.8s ease-in-out infinite; }}
.glitch-yw {{ animation: glitch-yw 5s linear infinite; }}
.glitch-cy {{ animation: glitch-cy 5s linear infinite; }}
.av-craft {{ animation: fly-av 22s linear infinite; }}
.av-bl {{ animation: av-beacon 1.2s infinite; }}
"""

DEFS = f"""
<pattern id="grid40" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{CP_CYAN}" stroke-opacity="0.06" stroke-width="1"/>
</pattern>
<pattern id="crt-scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000000" fill-opacity="0.25"/>
</pattern>
<filter id="glow-neon" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur"/>
  <feMerge>
    <feMergeNode in="blur"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
<filter id="glow-soft" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="3"/>
</filter>
"""

def wrap_slice(h, body_content, *, title, desc, top=False, bottom=False):
    """Wraps body in exact 880px wide slice with continuous frame rails and 40px grid"""
    assert h % 40 == 0, f"Slice height {h} must be multiple of 40!"
    y0 = M if top else 0
    y1 = h - M if bottom else h

    # Frame rails path
    rails = f"M {FL} {y0} V {y1} M {FR} {y0} V {y1}"
    if top:
        rails += f" M {FL} {y0} H {FR}"
    if bottom:
        rails += f" M {FL} {y1} H {FR}"

    # Glow overflowing seams
    gy0 = y0 if top else -40
    gy1 = y1 if bottom else h + 40
    glow_rails = f"M {FL} {gy0} V {gy1} M {FR} {gy0} V {gy1}"
    if top:
        glow_rails += f" M {FL} {y0} H {FR}"
    if bottom:
        glow_rails += f" M {FL} {y1} H {FR}"

    # Corner brackets
    corners = ""
    if top:
        corners += f"""
        <path d="M {FL-6} {y0+16} V {y0-6} H {FL+16}" fill="none" stroke="{CP_YELLOW}" stroke-width="2"/>
        <path d="M {FR-16} {y0-6} H {FR+6} V {y0+16}" fill="none" stroke="{CP_YELLOW}" stroke-width="2"/>
        <rect x="{FL+20}" y="{y0-3}" width="30" height="6" fill="{CP_YELLOW}"/>
        <rect x="{FR-50}" y="{y0-3}" width="30" height="6" fill="{CP_YELLOW}"/>
        """
    if bottom:
        corners += f"""
        <path d="M {FL-6} {y1-16} V {y1+6} H {FL+16}" fill="none" stroke="{CP_CYAN}" stroke-width="2"/>
        <path d="M {FR-16} {y1+6} H {FR+6} V {y1-16}" fill="none" stroke="{CP_CYAN}" stroke-width="2"/>
        <rect x="{FL+20}" y="{y1-3}" width="40" height="6" fill="{CP_CYAN}"/>
        <rect x="{FR-60}" y="{y1-3}" width="40" height="6" fill="{CP_CYAN}"/>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">
  <title>{title}</title>
  <desc>{desc}</desc>
  <style>
    {BASE_CSS}
  </style>
  <defs>
    {DEFS}
  </defs>

  <!-- Background Base & 40px Alignment Grid -->
  <rect x="{FL}" y="{0 if not top else M}" width="{FR-FL}" height="{h if not (top or bottom) else (h-M if (top and not bottom) else (h-2*M if (top and bottom) else h-M))}" fill="{CP_BG}"/>
  <rect x="{FL}" y="{0 if not top else M}" width="{FR-FL}" height="{h if not (top or bottom) else (h-M if (top and not bottom) else (h-2*M if (top and bottom) else h-M))}" fill="url(#grid40)"/>

  <!-- Neon Frame Rails -->
  <path d="{glow_rails}" fill="none" stroke="{CP_CYAN}" stroke-width="4" stroke-opacity="0.45" filter="url(#glow-soft)"/>
  <path d="{rails}" fill="none" stroke="{CP_CYAN}" stroke-width="1.8" stroke-opacity="0.85"/>
  {corners}

  <!-- Body Content -->
  {body_content}
</svg>"""
    return svg

# ==============================================================================
# SLICE 1: HEADER (h = 360px)
# ==============================================================================
def render_header():
    h = 360
    bar_left = "SYS://MILITECH.CYBERDECK // NODE:PALPARD // NIGHT CITY"
    bar_right = "BREACH: ACTIVE // RAM: 16/16 // ICE: BYPASSED"
    dot_x = FR - len(bar_right) * 8.6 - 36

    body = f"""
    <!-- Top Cyberpunk Status Bar -->
    <rect x="{FL}" y="{M}" width="{FR-FL}" height="32" fill="{CP_CYAN}" fill-opacity="0.12"/>
    <line x1="{FL}" y1="{M+32}" x2="{FR}" y2="{M+32}" stroke="{CP_CYAN}" stroke-opacity="0.5" stroke-width="1.5"/>
    <text x="{FL+18}" y="{M+21}" font-size="11" font-weight="700" letter-spacing="1" fill="{CP_CYAN}">{bar_left}</text>
    <circle class="dot-live" cx="{dot_x}" cy="{M+16}" r="4.5" fill="{CP_YELLOW}" filter="url(#glow-neon)"/>
    <text x="{FR-18}" y="{M+21}" font-size="11" font-weight="700" letter-spacing="1" text-anchor="end" fill="{CP_YELLOW}">{bar_right}</text>

    <!-- Angled Cyberpunk Tech Accent -->
    <polygon points="{FL+18},{M+32} {FL+34},{M+48} {FL+180},{M+48} {FL+196},{M+32}" fill="{CP_YELLOW}" fill-opacity="0.2"/>
    <text x="{FL+38}" y="{M+44}" font-size="9" font-weight="800" letter-spacing="2" fill="{CP_YELLOW}">NETRUNNER CONSOLE v3.2</text>

    <!-- Terminal Command Line Prompt -->
    <text x="{X}" y="100" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> whoami --status</text>

    <!-- Chromatic Aberration Glitch Title: PALPARD -->
    <g transform="translate({X}, 168)" font-weight="900" letter-spacing="3" style="font-size: 58px;">
      <!-- Crimson Shadow Layer -->
      <g class="glitch-cy">
        <text x="3" y="0" fill="{CP_RED}" opacity="0.85">PALPARD</text>
      </g>
      <!-- Cyan Shadow Layer -->
      <g class="glitch-yw">
        <text x="-3" y="0" fill="{CP_CYAN}" opacity="0.85">PALPARD</text>
      </g>
      <!-- Main Signature Cyberpunk Yellow -->
      <text x="0" y="0" fill="{CP_YELLOW}" filter="url(#glow-soft)">PALPARD</text>
      <text x="0" y="0" fill="{CP_YELLOW}">PALPARD</text>
    </g>

    <!-- Edgerunners Style Status & Operator Specs -->
    <g transform="translate({X}, 208)">
      <text x="0" y="0" class="fg"><tspan class="yw">&gt;&gt; OPERATOR:</tspan> TAHA <tspan class="dim">//</tspan> <tspan class="cy">PALPARD</tspan></text>
      <text x="0" y="24" class="fg"><tspan class="yw">&gt;&gt; CLASS:</tspan> SECURITY RESEARCHER &amp; BUG BOUNTY HUNTER</text>
      <text x="0" y="48" class="fg"><tspan class="yw">&gt;&gt; PROTOCOL:</tspan> WEB APP SECURITY · RECON ARSENAL · BUSINESS LOGIC HUNTING</text>
      <text x="0" y="72" class="fg"><tspan class="yw">&gt;&gt; CYBERWARE:</tspan> MILITECH &quot;SANDEVISTAN&quot; MK.IV <tspan class="dim">//</tspan> ARASAKA OSINT DECK</text>
    </g>

    <!-- Blinking Prompt -->
    <g transform="translate({X}, 318)">
      <text x="0" y="0" class="rd">[netrunner@night-city]$</text>
      <rect class="cursor" x="180" y="-13" width="10" height="17" fill="{CP_YELLOW}" filter="url(#glow-neon)"/>
    </g>

    <!-- CRT Scanline Mask -->
    <rect x="{FL}" y="{M+33}" width="{FR-FL}" height="{h-M-33}" fill="url(#crt-scan)" pointer-events="none"/>
    """
    return wrap_slice(h, body, title="PALPARD Netrunner Cyberdeck", desc="Cyberpunk console header for PALPARD", top=True)

# ==============================================================================
# SLICE 2: TELEMETRY (h = 160px)
# ==============================================================================
def render_telemetry():
    h = 160
    box_w = (FR - FL - 40) / 3
    b1_x = FL + 14
    b2_x = b1_x + box_w + 6
    b3_x = b2_x + box_w + 6
    b_y = 20
    b_h = 120

    body = f"""
    <!-- Box 1: Cyberdeck Telemetry -->
    <rect x="{b1_x}" y="{b_y}" width="{box_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_CYAN}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b1_x}" y="{b_y}" width="{box_w}" height="22" fill="{CP_CYAN}" fill-opacity="0.15"/>
    <text x="{b1_x+10}" y="{b_y+15}" font-size="10" font-weight="800" fill="{CP_CYAN}">[01 // NEURAL TELEMETRY]</text>
    <text x="{b1_x+12}" y="{b_y+42}" font-size="12" class="fg">STATUS: <tspan class="gr">100% OPERATIONAL</tspan></text>
    <text x="{b1_x+12}" y="{b_y+64}" font-size="12" class="fg">DAEMON: <tspan class="yw">STRIX RECON v1.5</tspan></text>
    <text x="{b1_x+12}" y="{b_y+86}" font-size="12" class="fg">BUFFER: <tspan class="cy">ENCRYPTED (TLS 1.3)</tspan></text>
    <text x="{b1_x+12}" y="{b_y+108}" font-size="12" class="fg">FIREWALL: <tspan class="rd">BLACK-ICE BYPASS</tspan></text>

    <!-- Box 2: Offensive Security Focus -->
    <rect x="{b2_x}" y="{b_y}" width="{box_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_YELLOW}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b2_x}" y="{b_y}" width="{box_w}" height="22" fill="{CP_YELLOW}" fill-opacity="0.15"/>
    <text x="{b2_x+10}" y="{b_y+15}" font-size="10" font-weight="800" fill="{CP_YELLOW}">[02 // HUNTING FOCUS]</text>
    <text x="{b2_x+12}" y="{b_y+42}" font-size="12" class="fg">PRIMARY: <tspan class="yw">IDOR &amp; LOGIC FLAWS</tspan></text>
    <text x="{b2_x+12}" y="{b_y+64}" font-size="12" class="fg">TARGETS: <tspan class="cy">WEB &amp; REST APIS</tspan></text>
    <text x="{b2_x+12}" y="{b_y+86}" font-size="12" class="fg">METHOD: <tspan class="gr">EVIDENCE-BACKED</tspan></text>
    <text x="{b2_x+12}" y="{b_y+108}" font-size="12" class="fg">RATE LIMIT: <tspan class="rd">BYPASS AUDITED</tspan></text>

    <!-- Box 3: System Arsenal -->
    <rect x="{b3_x}" y="{b_y}" width="{box_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_RED}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b3_x}" y="{b_y}" width="{box_w}" height="22" fill="{CP_RED}" fill-opacity="0.15"/>
    <text x="{b3_x+10}" y="{b_y+15}" font-size="10" font-weight="800" fill="{CP_RED}">[03 // ENVIRONMENT]</text>
    <text x="{b3_x+12}" y="{b_y+42}" font-size="12" class="fg">OS: <tspan class="cy">KALI LINUX / XFCE</tspan></text>
    <text x="{b3_x+12}" y="{b_y+64}" font-size="12" class="fg">STACK: <tspan class="yw">PYTHON · NODE · BASH</tspan></text>
    <text x="{b3_x+12}" y="{b_y+86}" font-size="12" class="fg">PROXY: <tspan class="gr">BURP SUITE PRO</tspan></text>
    <text x="{b3_x+12}" y="{b_y+108}" font-size="12" class="fg">AI ORCHESTRATION: <tspan class="cy">HERMES AGENT</tspan></text>
    """
    return wrap_slice(h, body, title="Cyberdeck Telemetry", desc="System telemetry and status indicators")

# ==============================================================================
# SLICE 3: NIGHT CITY SKYLINE (h = 680px)
# ==============================================================================
def render_city(calendar):
    h = 680
    CITY_OX = 350
    CITY_OY = 270
    CITY_TW = 14
    CITY_TH = 7.5
    CITY_HMAX = 135

    # Prepare days
    if not calendar:
        # Fallback 53 weeks
        calendar = [("2026-01-01", 0)] * 365

    days = calendar
    counts = [c for _, c in days]
    total_contribs = sum(counts)
    peak = max(counts) if counts else 1
    if peak == 0:
        peak = 1

    cells = []
    for idx, (d, n) in enumerate(days):
        w_col = idx // 7
        dow = idx % 7
        cells.append((w_col, dow, n))

    # Sort back to front (painter's algorithm)
    cells.sort(key=lambda c: (c[0] + c[1], c[0]))

    shapes = []
    # Distinct Cyberpunk 2077 Night City Roofs
    ROOFS = ["#16233B", "#0D485E", "#00F0FF", "#FCEE0A", "#FF003C"]

    for w_col, dow, n in cells:
        cx = CITY_OX + (w_col - dow) * CITY_TW / 2
        cy = CITY_OY + (w_col + dow) * CITY_TH / 2
        L = (cx - CITY_TW / 2, cy)
        R = (cx + CITY_TW / 2, cy)
        T = (cx, cy - CITY_TH / 2)
        B = (cx, cy + CITY_TH / 2)

        if n == 0:
            # Baseline Night City lot / street slab
            # A small fraction get baseline district low-rise to create dense skyline atmosphere
            if (w_col * 7 + dow) % 9 == 0:
                bh = 6
                Tu = (T[0], T[1] - bh)
                Ru = (R[0], R[1] - bh)
                Bu = (B[0], B[1] - bh)
                Lu = (L[0], L[1] - bh)
                shapes.append(f'<path d="M {L[0]},{L[1]} L {B[0]},{B[1]} L {Bu[0]},{Bu[1]} L {Lu[0]},{Lu[1]} Z" fill="#0C1322"/>')
                shapes.append(f'<path d="M {B[0]},{B[1]} L {R[0]},{R[1]} L {Ru[0]},{Ru[1]} L {Bu[0]},{Bu[1]} Z" fill="#080D17"/>')
                shapes.append(f'<path d="M {Tu[0]},{Tu[1]} L {Ru[0]},{Ru[1]} L {Bu[0]},{Bu[1]} L {Lu[0]},{Lu[1]} Z" fill="#131C30" stroke="#00F0FF" stroke-opacity="0.1" stroke-width="0.5"/>')
            else:
                shapes.append(f'<path d="M {T[0]},{T[1]} L {R[0]},{R[1]} L {B[0]},{B[1]} L {L[0]},{L[1]} Z" fill="#090E17" stroke="#00F0FF" stroke-opacity="0.04" stroke-width="0.5"/>')
            continue

        # Active building
        bh = 12 + (CITY_HMAX - 12) * math.sqrt(n / peak)
        level = min(4, int((n / peak) * 4) + 1)
        roof_color = ROOFS[level]

        Tu = (T[0], T[1] - bh)
        Ru = (R[0], R[1] - bh)
        Bu = (B[0], B[1] - bh)
        Lu = (L[0], L[1] - bh)

        # Left wall (shadowed), Right wall (mid), Roof (bright neon / mega-building)
        shapes.append(f'<path d="M {L[0]},{L[1]} L {B[0]},{B[1]} L {Bu[0]},{Bu[1]} L {Lu[0]},{Lu[1]} Z" fill="#131D33"/>')
        shapes.append(f'<path d="M {B[0]},{B[1]} L {R[0]},{R[1]} L {Ru[0]},{Ru[1]} L {Bu[0]},{Bu[1]} Z" fill="#0C1221"/>')
        shapes.append(f'<path d="M {Tu[0]},{Tu[1]} L {Ru[0]},{Ru[1]} L {Bu[0]},{Bu[1]} L {Lu[0]},{Lu[1]} Z" fill="{roof_color}" stroke="{roof_color}" stroke-width="0.8"/>')

        # Glowing Cyberpunk Windows
        num_floors = int((bh - 8) // 6)
        for flr in range(num_floors):
            wy = Bu[1] + 6 + flr * 6
            # Window dot on left and right face
            if (flr + w_col) % 2 == 0:
                shapes.append(f'<rect x="{Bu[0]-4}" y="{wy-2}" width="2.5" height="2" fill="{CP_YELLOW if flr % 3 == 0 else CP_CYAN}" opacity="0.85"/>')
            if (flr + dow) % 2 == 1:
                shapes.append(f'<rect x="{Bu[0]+2}" y="{wy-2}" width="2.5" height="2" fill="{CP_CYAN if flr % 2 == 0 else CP_RED}" opacity="0.75"/>')

        # Beacon spire on mega towers
        if level >= 3:
            spire_top = (Bu[0], Tu[1] - 16)
            shapes.append(f'<line x1="{Bu[0]}" y1="{Tu[1]}" x2="{spire_top[0]}" y2="{spire_top[1]}" stroke="{roof_color}" stroke-width="1"/>')
            shapes.append(f'<circle class="dot-live" cx="{spire_top[0]}" cy="{spire_top[1]}" r="2" fill="{CP_YELLOW}" filter="url(#glow-neon)"/>')

    # Night City Sky: Stars, Full Moon with Neon Halo, Flying Trauma Team AV
    stars = []
    import random
    rng = random.Random(2077)
    for _ in range(35):
        sx = 420 + rng.random() * 410
        sy = 70 + rng.random() * 160
        s_fill = CP_CYAN if rng.random() > 0.5 else "#FFFFFF"
        s_r = 0.7 + rng.random() * 0.6
        s_op = 0.4 + rng.random() * 0.5
        stars.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{s_r:.1f}" fill="{s_fill}" opacity="{s_op:.2f}"/>')

    body = f"""
    <!-- Terminal Command Heading -->
    <g transform="translate({X}, 54)">
      <text x="0" y="0" class="yw" font-weight="800">&gt;&gt; [03 // NIGHT CITY CONTRIBUTION SKYLINE]</text>
      <text x="0" y="24" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> ./netrunner --scan-skyline --sector night-city --days 365</text>
    </g>

    <!-- Deep Night City Atmosphere & Glowing Moon -->
    <g>{"".join(stars)}</g>
    <circle cx="{FR-90}" cy="135" r="45" fill="{CP_CYAN}" fill-opacity="0.08" filter="url(#glow-neon)"/>
    <circle cx="{FR-90}" cy="135" r="18" fill="#F4F8FB" opacity="0.9"/>
    <circle cx="{FR-83}" cy="130" r="15" fill="{CP_BG}"/>

    <!-- Flying Trauma Team AV (Aerodyne) with Pulsing Nav Beacons -->
    <g class="av-craft">
      <g transform="translate(0, 115)">
        <polygon points="0,4 20,0 28,6 18,10 0,7" fill="{CP_RED}" opacity="0.9"/>
        <polygon points="6,2 14,0 16,4 8,4" fill="{CP_YELLOW}"/>
        <circle class="av-bl" cx="0" cy="5" r="2.2" fill="{CP_RED}" filter="url(#glow-neon)"/>
        <circle class="av-bl" cx="28" cy="6" r="2.2" fill="{CP_CYAN}" filter="url(#glow-neon)"/>
      </g>
    </g>

    <!-- Skyline Stats Box -->
    <g transform="translate({FR-20}, 245)" text-anchor="end">
      <text x="0" y="0" font-size="12" class="fg">ANNUAL COMMITS: <tspan class="yw" font-weight="800">{total_contribs}</tspan></text>
      <text x="0" y="20" font-size="12" class="fg">SKYLINE SECTOR: <tspan class="cy">WATSON / CORPO PLAZA</tspan></text>
      <text x="0" y="40" font-size="11" class="dim">MAPPED: 53 WEEKS ISOMETRIC PROJECTION</text>
    </g>

    <!-- Rendered 3D Skyline Buildings -->
    <g>
      {"".join(shapes)}
    </g>

    <!-- Legend -->
    <g transform="translate({X}, 652)">
      <text x="0" y="0" font-size="11" class="dim">LEVEL: SLUMS</text>
      <rect x="90" y="-10" width="12" height="12" fill="#090E17" stroke="{CP_CYAN}" stroke-width="0.5"/>
      <rect x="108" y="-10" width="12" height="12" fill="#16233B"/>
      <rect x="126" y="-10" width="12" height="12" fill="#0D485E"/>
      <rect x="144" y="-10" width="12" height="12" fill="{CP_CYAN}"/>
      <rect x="162" y="-10" width="12" height="12" fill="{CP_YELLOW}"/>
      <rect x="180" y="-10" width="12" height="12" fill="{CP_RED}"/>
      <text x="202" y="0" font-size="11" class="dim">ARASAKA MEGA-TOWER</text>
    </g>
    """
    return wrap_slice(h, body, title="Night City Skyline", desc="Isometric 3D Night City Skyline built from PALPARD GitHub contributions")

# ==============================================================================
# SLICE 4: QUICKHACKS & ARSENAL (h = 320px)
# ==============================================================================
def render_arsenal():
    h = 320
    b_w = (FR - FL - 36) / 2
    b1_x = FL + 14
    b2_x = b1_x + b_w + 8
    b_y1 = 80
    b_h = 100
    b_y2 = 195

    body = f"""
    <!-- Terminal Heading -->
    <g transform="translate({X}, 48)">
      <text x="0" y="0" class="yw" font-weight="800">&gt;&gt; [04 // NETRUNNER QUICKHACKS &amp; ARSENAL]</text>
      <text x="0" y="20" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> ./arsenal --list-cyberware --tier legendary</text>
    </g>

    <!-- Module 1: Web App Exploitation -->
    <rect x="{b1_x}" y="{b_y1}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_YELLOW}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b1_x}" y="{b_y1}" width="{b_w}" height="22" fill="{CP_YELLOW}" fill-opacity="0.15"/>
    <text x="{b1_x+10}" y="{b_y1+15}" font-size="11" font-weight="800" fill="{CP_YELLOW}">[QUICKHACK // WEB APPLICATION SECURITY]</text>
    <text x="{b1_x+12}" y="{b_y1+44}" font-size="12" class="fg">&gt; Insecure Direct Object Reference (IDOR)</text>
    <text x="{b1_x+12}" y="{b_y1+64}" font-size="12" class="fg">&gt; Business Logic Hunting &amp; Flaws</text>
    <text x="{b1_x+12}" y="{b_y1+84}" font-size="12" class="fg">&gt; SSRF Bypass &amp; 2FA / Rate-Limit Audits</text>

    <!-- Module 2: Recon & OSINT -->
    <rect x="{b2_x}" y="{b_y1}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_CYAN}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b2_x}" y="{b_y1}" width="{b_w}" height="22" fill="{CP_CYAN}" fill-opacity="0.15"/>
    <text x="{b2_x+10}" y="{b_y1+15}" font-size="11" font-weight="800" fill="{CP_CYAN}">[DAEMON // RECONNAISSANCE &amp; OSINT]</text>
    <text x="{b2_x+12}" y="{b_y1+44}" font-size="12" class="fg">&gt; Attack Surface &amp; Asset Mapping</text>
    <text x="{b2_x+12}" y="{b_y1+64}" font-size="12" class="fg">&gt; Subdomain &amp; Cloud Exposure Discovery</text>
    <text x="{b2_x+12}" y="{b_y1+84}" font-size="12" class="fg">&gt; Automated Pentest Pipelines &amp; Probes</text>

    <!-- Module 3: Tooling & Systems -->
    <rect x="{b1_x}" y="{b_y2}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_RED}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b1_x}" y="{b_y2}" width="{b_w}" height="22" fill="{CP_RED}" fill-opacity="0.15"/>
    <text x="{b1_x+10}" y="{b_y2+15}" font-size="11" font-weight="800" fill="{CP_RED}">[CYBERWARE // WEAPONS &amp; RUNTIME]</text>
    <text x="{b1_x+12}" y="{b_y2+44}" font-size="12" class="fg">&gt; Python 3 · Bash Scripting · Kali Linux</text>
    <text x="{b1_x+12}" y="{b_y2+64}" font-size="12" class="fg">&gt; Burp Suite Pro · Wireshark · Nuclei</text>
    <text x="{b1_x+12}" y="{b_y2+84}" font-size="12" class="fg">&gt; Docker · Git · Linux Kernel Diagnostics</text>

    <!-- Module 4: Engineering & Realtime -->
    <rect x="{b2_x}" y="{b_y2}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.6" stroke="{CP_GREEN}" stroke-opacity="0.4" stroke-width="1.5"/>
    <rect x="{b2_x}" y="{b_y2}" width="{b_w}" height="22" fill="{CP_GREEN}" fill-opacity="0.15"/>
    <text x="{b2_x+10}" y="{b_y2+15}" font-size="11" font-weight="800" fill="{CP_GREEN}">[PROTOCOL // FULL-STACK ARCHITECTURE]</text>
    <text x="{b2_x+12}" y="{b_y2+44}" font-size="12" class="fg">&gt; Node.js &amp; Express.js Microservices</text>
    <text x="{b2_x+12}" y="{b_y2+64}" font-size="12" class="fg">&gt; Socket.IO Real-time Multiplayer Engines</text>
    <text x="{b2_x+12}" y="{b_y2+84}" font-size="12" class="fg">&gt; Web Audio API Synthesizers &amp; Tactile UI</text>
    """
    return wrap_slice(h, body, title="Cyberdeck Arsenal", desc="Cyberpunk 2077 Netrunner tools and offensive capabilities")

# ==============================================================================
# SLICE 5: NEURAL UPLINKS & REPOSITORIES (h = 160px)
# ==============================================================================
def render_links():
    h = 160
    b_w = (FR - FL - 36) / 2
    b1_x = FL + 14
    b2_x = b1_x + b_w + 8
    b_y = 52
    b_h = 92

    body = f"""
    <!-- Terminal Heading -->
    <g transform="translate({X}, 34)">
      <text x="0" y="0" class="yw" font-weight="800">&gt;&gt; [05 // NEURAL UPLINKS &amp; FEATURED DEPLOYMENT]</text>
    </g>

    <!-- Comms Link -->
    <rect x="{b1_x}" y="{b_y}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.7" stroke="{CP_CYAN}" stroke-opacity="0.6" stroke-width="1.5"/>
    <text x="{b1_x+16}" y="{b_y+26}" font-size="12" font-weight="800" fill="{CP_CYAN}">[COMMUNICATION // ENCRYPTED COMMS]</text>
    <text x="{b1_x+16}" y="{b_y+52}" font-size="13" class="fg">TELEGRAM: <tspan class="yw" font-weight="700">@PALPARD</tspan></text>
    <text x="{b1_x+16}" y="{b_y+74}" font-size="11" class="dim">DIRECT NEURAL RELAY · ID: 5551619179</text>

    <!-- Project Link -->
    <rect x="{b2_x}" y="{b_y}" width="{b_w}" height="{b_h}" fill="{CP_BLACK}" fill-opacity="0.7" stroke="{CP_YELLOW}" stroke-opacity="0.6" stroke-width="1.5"/>
    <text x="{b2_x+16}" y="{b_y+26}" font-size="12" font-weight="800" fill="{CP_YELLOW}">[FEATURED CODEBASE // LIVE REPOSITORY]</text>
    <text x="{b2_x+16}" y="{b_y+52}" font-size="13" class="fg">REPO: <tspan class="cy" font-weight="700">esm-famil-multiplayer-online</tspan></text>
    <text x="{b2_x+16}" y="{b_y+74}" font-size="11" class="dim">REALTIME PARTY GAME · TACTILE ARCADE UI</text>
    """
    return wrap_slice(h, body, title="Neural Uplinks", desc="Communication ports and repositories")

# ==============================================================================
# SLICE 6: FOOTER (h = 80px)
# ==============================================================================
def render_footer():
    h = 80
    body = f"""
    <g transform="translate({X}, 34)">
      <text x="0" y="0" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> jack_out --force --clean</text>
      <text x="0" y="24" class="dim">neural link severed. node <tspan class="yw">PALPARD</tspan> entered sleep mode. <tspan class="cy">// [FLATLINE: FALSE]</tspan></text>
    </g>
    """
    return wrap_slice(h, body, title="End of Cyberdeck Console", desc="Console closed", bottom=True)

def main():
    print("Fetching PALPARD contribution calendar from GitHub...")
    calendar = fetch_calendar()
    print(f"Calendar entries: {len(calendar)}")

    print("Rendering Cyberpunk 2077 slices...")
    header_svg = render_header()
    telemetry_svg = render_telemetry()
    city_svg = render_city(calendar)
    arsenal_svg = render_arsenal()
    links_svg = render_links()
    footer_svg = render_footer()

    (ASSETS_DIR / "header.svg").write_text(header_svg)
    (ASSETS_DIR / "telemetry.svg").write_text(telemetry_svg)
    (ASSETS_DIR / "city.svg").write_text(city_svg)
    (ASSETS_DIR / "arsenal.svg").write_text(arsenal_svg)
    (ASSETS_DIR / "links.svg").write_text(links_svg)
    (ASSETS_DIR / "footer.svg").write_text(footer_svg)

    # Now write the master README.md that stacks all slices seamlessly
    readme_content = f"""<div align="center">

<p align="center">
  <img src="./assets/header.svg" width="100%" align="top" alt="PALPARD Netrunner Cyberdeck Header"><br>
  <img src="./assets/telemetry.svg" width="100%" align="top" alt="Cyberdeck Telemetry"><br>
  <img src="./assets/city.svg" width="100%" align="top" alt="Night City Skyline"><br>
  <img src="./assets/arsenal.svg" width="100%" align="top" alt="Netrunner Quickhacks and Arsenal"><br>
  <a href="https://t.me/PALPARD"><img src="./assets/links.svg" width="100%" align="top" alt="Neural Uplinks and Featured Deployment"></a><br>
  <img src="./assets/footer.svg" width="100%" align="top" alt="Cyberdeck Footer">
</p>

</div>
"""
    (HERE / "README.md").write_text(readme_content)
    print("All Cyberpunk 2077 slices and README generated successfully!")

if __name__ == "__main__":
    main()
