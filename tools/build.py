#!/usr/bin/env python3
"""
Cyberpunk 2077 / Edgerunners Netrunner Cyberdeck Profile Generator for PALPARD
Generates pixel-perfect, seamless SVG console slices for GitHub profile README.
"""

import json
import math
import os
import pathlib
import random
import re
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
ASSETS_DIR = HERE / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Cyberpunk 2077 Authentic Color Palette
CP_YELLOW = "#FCEE0A"   # Cyberpunk 2077 Signature Yellow (Pantone 3945 C)
CP_CYAN = "#00F0FF"     # Netrunner ICE Cyan
CP_RED = "#FF003C"      # Arasaka Combat Alert Crimson
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
  from {{ transform: translate({FL - 80}px, 0); }}
  to {{ transform: translate({FR + 80}px, -45px); }}
}}
@keyframes fly-av-back {{
  from {{ transform: translate({FR + 80}px, -10px); }}
  to {{ transform: translate({FL - 80}px, 25px); }}
}}
@keyframes av-beacon {{ 0%, 88%, 100% {{ opacity: 0; }} 90%, 96% {{ opacity: 1; }} }}
@keyframes spotlight {{ 0%, 100% {{ opacity: 0.15; transform: rotate(-8deg); }} 50% {{ opacity: 0.35; transform: rotate(12deg); }} }}

.cursor {{ animation: blink 1s step-end infinite; }}
.dot-live {{ animation: pulse 1.8s ease-in-out infinite; }}
.glitch-yw {{ animation: glitch-yw 5s linear infinite; }}
.glitch-cy {{ animation: glitch-cy 5s linear infinite; }}
.av-craft {{ animation: fly-av 24s linear infinite; }}
.av-craft-back {{ animation: fly-av-back 30s linear infinite; }}
.av-bl {{ animation: av-beacon 1.2s infinite; }}
.spotlight-beam {{ animation: spotlight 8s ease-in-out infinite alternate; transform-origin: 350px 300px; }}
"""

DEFS = f"""
<pattern id="grid40" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{CP_CYAN}" stroke-opacity="0.06" stroke-width="1"/>
</pattern>
<pattern id="crt-scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000000" fill-opacity="0.22"/>
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
<linearGradient id="cyber-fog" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="{CP_CYAN}" stop-opacity="0"/>
  <stop offset="50%" stop-color="{CP_CYAN}" stop-opacity="0.08"/>
  <stop offset="100%" stop-color="{CP_RED}" stop-opacity="0.18"/>
</linearGradient>
<linearGradient id="beam-grad" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0%" stop-color="{CP_CYAN}" stop-opacity="0.35"/>
  <stop offset="100%" stop-color="{CP_CYAN}" stop-opacity="0"/>
</linearGradient>
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
  <path d="{glow_rails}" fill="none" stroke="{CP_CYAN}" stroke-width="4" stroke-opacity="0.4" filter="url(#glow-soft)"/>
  <path d="{rails}" fill="none" stroke="{CP_CYAN}" stroke-width="1.8" stroke-opacity="0.85"/>
  {corners}

  <!-- Body Content -->
  {body_content}
</svg>"""
    return svg

# ==============================================================================
# SLICE 1: HEADER (h = 360px) — 100% COLLISION-PROOF MODULAR CYBERPUNK HUD
# ==============================================================================
def render_header():
    h = 360

    # 3 Separate, Non-Overlapping HUD Pods:
    # Pod 1: Left (x=28..258, w=230)
    # Pod 2: Center (x=345..535, w=190, center at 440) -> 87px gap!
    # Pod 3: Right (x=622..852, w=230) -> 87px gap!
    body = f"""
    <!-- Top Cyberpunk Status Bar Strip -->
    <rect x="{FL}" y="{M}" width="{FR-FL}" height="34" fill="{CP_BLACK}" fill-opacity="0.75"/>
    <line x1="{FL}" y1="{M+34}" x2="{FR}" y2="{M+34}" stroke="{CP_CYAN}" stroke-opacity="0.6" stroke-width="1.5"/>

    <!-- Pod 1 (Left): Terminal Subsystem Node -->
    <g transform="translate({FL+12}, {M+5})">
      <rect x="0" y="0" width="230" height="24" rx="2" fill="{CP_CYAN}" fill-opacity="0.1" stroke="{CP_CYAN}" stroke-opacity="0.4"/>
      <circle class="dot-live" cx="12" cy="12" r="3.5" fill="{CP_GREEN}" filter="url(#glow-neon)"/>
      <text x="24" y="16" font-size="10.5" font-weight="700" letter-spacing="1" fill="{CP_CYAN}">SYS://CYBERDECK · NODE:PALPARD</text>
    </g>

    <!-- Pod 2 (Center): Night City Location Badge -->
    <g transform="translate(440, {M+5})">
      <rect x="-95" y="0" width="190" height="24" rx="2" fill="{CP_YELLOW}" fill-opacity="0.1" stroke="{CP_YELLOW}" stroke-opacity="0.4"/>
      <text x="0" y="16" font-size="10.5" font-weight="800" letter-spacing="2" text-anchor="middle" fill="{CP_YELLOW}">[ NIGHT CITY · SECTOR 04 ]</text>
    </g>

    <!-- Pod 3 (Right): Hardware Telemetry & ICE Status -->
    <g transform="translate({FR-242}, {M+5})">
      <rect x="0" y="0" width="230" height="24" rx="2" fill="{CP_CYAN}" fill-opacity="0.1" stroke="{CP_CYAN}" stroke-opacity="0.4"/>
      <text x="115" y="16" font-size="10.5" font-weight="700" letter-spacing="1" text-anchor="middle" fill="{CP_CYAN}">RAM: 16/16 // ICE: BYPASSED</text>
    </g>

    <!-- Angled Cyberpunk Tech Accent Badge -->
    <polygon points="{FL+18},{M+34} {FL+34},{M+50} {FL+180},{M+50} {FL+196},{M+34}" fill="{CP_YELLOW}" fill-opacity="0.25"/>
    <text x="{FL+38}" y="{M+46}" font-size="9" font-weight="800" letter-spacing="2" fill="{CP_YELLOW}">NETRUNNER CONSOLE v3.2</text>

    <!-- Terminal Command Line Prompt -->
    <text x="{X}" y="104" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> whoami --status</text>

    <!-- Chromatic Aberration Glitch Title: PALPARD -->
    <g transform="translate({X}, 172)" font-weight="900" letter-spacing="4" style="font-size: 56px;">
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

    <!-- Operator Specs HUD Box with Neon Framing -->
    <g transform="translate({X}, 212)">
      <text x="0" y="0" class="fg"><tspan class="yw">&gt;&gt; OPERATOR:</tspan> TAHA <tspan class="dim">//</tspan> <tspan class="cy">PALPARD</tspan></text>
      <text x="0" y="24" class="fg"><tspan class="yw">&gt;&gt; CLASS:</tspan> SECURITY RESEARCHER &amp; BUG BOUNTY SPECIALIST</text>
      <text x="0" y="48" class="fg"><tspan class="yw">&gt;&gt; SPECIALIZATION:</tspan> IDOR · BUSINESS LOGIC · SSRF · RECON AUTOMATION</text>
      <text x="0" y="72" class="fg"><tspan class="yw">&gt;&gt; CYBERWARE:</tspan> MILITECH &quot;SANDEVISTAN&quot; MK.IV <tspan class="dim">//</tspan> ARASAKA OSINT DECK</text>
    </g>

    <!-- Blinking Prompt -->
    <g transform="translate({X}, 320)">
      <text x="0" y="0" class="rd">[netrunner@night-city]$</text>
      <rect class="cursor" x="180" y="-13" width="10" height="17" fill="{CP_YELLOW}" filter="url(#glow-neon)"/>
    </g>

    <!-- CRT Scanline Mask -->
    <rect x="{FL}" y="{M+35}" width="{FR-FL}" height="{h-M-35}" fill="url(#crt-scan)" pointer-events="none"/>
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
    <text x="{b3_x+12}" y="{b_y+108}" font-size="12" class="fg">AI ENGINE: <tspan class="cy">HERMES AGENT</tspan></text>
    """
    return wrap_slice(h, body, title="Cyberdeck Telemetry", desc="System telemetry and status indicators")

# ==============================================================================
# SLICE 3: 10/10 NIGHT CITY 3D SKYLINE (h = 680px)
# Multi-tiered Mega-Towers, Skybridges, Holographic Signs, Dual Flying AVs, Searchlights
# ==============================================================================
def render_city(calendar):
    h = 680
    CITY_OX = 350
    CITY_OY = 265
    CITY_TW = 14
    CITY_TH = 7.5
    CITY_HMAX = 145

    if not calendar:
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

    def pt(p):
        return f"{p[0]:.1f},{p[1]:.1f}"

    def iso_quad(a, b, u0, du, v0, dv):
        """Calculates exact 3D isometric parallelogram for window or hologram on a wall"""
        p1 = (a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0 - v0)
        p2 = (a[0] + (b[0] - a[0]) * (u0 + du), a[1] + (b[1] - a[1]) * (u0 + du) - v0)
        p3 = (a[0] + (b[0] - a[0]) * (u0 + du), a[1] + (b[1] - a[1]) * (u0 + du) - (v0 + dv))
        p4 = (a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0 - (v0 + dv))
        return f"M {pt(p1)} L {pt(p2)} L {pt(p3)} L {pt(p4)} Z"

    shapes = []
    skybridges = []
    holograms = []
    beacons = []

    ROOFS = ["#1A2538", "#0E566E", "#00F0FF", "#FCEE0A", "#FF003C"]
    rng = random.Random(2077)

    # Track tall building roof coordinates to build skybridges
    tall_towers = []

    for w_col, dow, n in cells:
        cx = CITY_OX + (w_col - dow) * CITY_TW / 2
        cy = CITY_OY + (w_col + dow) * CITY_TH / 2
        L = (cx - CITY_TW / 2, cy)
        R = (cx + CITY_TW / 2, cy)
        T = (cx, cy - CITY_TH / 2)
        B = (cx, cy + CITY_TH / 2)

        # Baseline Urban Architecture (Dense metropolis texture)
        if n == 0:
            pattern_hash = (w_col * 17 + dow * 31) % 100
            if pattern_hash < 70:
                bh = 8 + (pattern_hash % 20)
                Tu = (T[0], T[1] - bh)
                Ru = (R[0], R[1] - bh)
                Bu = (B[0], B[1] - bh)
                Lu = (L[0], L[1] - bh)

                wall_l = "#11192A" if pattern_hash % 2 == 0 else "#0E1524"
                wall_r = "#0A0F1B" if pattern_hash % 2 == 0 else "#070C15"
                roof = "#1A2538" if pattern_hash < 50 else "#132D42"

                shapes.append(f'<path d="M {pt(L)} L {pt(B)} L {pt(Bu)} L {pt(Lu)} Z" fill="{wall_l}"/>')
                shapes.append(f'<path d="M {pt(B)} L {pt(R)} L {pt(Ru)} L {pt(Bu)} Z" fill="{wall_r}"/>')
                shapes.append(f'<path d="M {pt(Tu)} L {pt(Ru)} L {pt(Bu)} L {pt(Lu)} Z" fill="{roof}" stroke="{CP_CYAN}" stroke-opacity="0.15" stroke-width="0.5"/>')

                # Windows on baseline blocks
                if bh > 14 and pattern_hash % 2 == 0:
                    win_quad = iso_quad(L, B, 0.25, 0.45, 6, 4)
                    shapes.append(f'<path d="{win_quad}" fill="{CP_CYAN}" opacity="0.65"/>')
            else:
                shapes.append(f'<path d="M {pt(T)} L {pt(R)} L {pt(B)} L {pt(L)} Z" fill="#090E17" stroke="{CP_CYAN}" stroke-opacity="0.08" stroke-width="0.5"/>')
            continue

        # Active Contribution Mega-Tower!
        bh = 45 + (CITY_HMAX - 45) * math.sqrt(n / peak)
        level = min(4, int((n / peak) * 4) + 1)
        roof_color = ROOFS[level]

        Tu = (T[0], T[1] - bh)
        Ru = (R[0], R[1] - bh)
        Bu = (B[0], B[1] - bh)
        Lu = (L[0], L[1] - bh)

        tall_towers.append((Bu[0], Bu[1], bh))

        # Main tower walls
        shapes.append(f'<path d="M {pt(L)} L {pt(B)} L {pt(Bu)} L {pt(Lu)} Z" fill="#141E33"/>')
        shapes.append(f'<path d="M {pt(B)} L {pt(R)} L {pt(Ru)} L {pt(Bu)} Z" fill="#0D1322"/>')
        shapes.append(f'<path d="M {pt(Tu)} L {pt(Ru)} L {pt(Bu)} L {pt(Lu)} Z" fill="{roof_color}" stroke="{roof_color}" stroke-width="0.8"/>')

        # Tiered Rooftop Setback for high-level towers (Arasaka Tower style)
        if level >= 3:
            s_bh = 16
            s_T = (Tu[0], Tu[1] - s_bh)
            s_R = (Ru[0] - 2, Ru[1] - s_bh)
            s_B = (Bu[0], Bu[1] - s_bh - 2)
            s_L = (Lu[0] + 2, Lu[1] - s_bh)
            shapes.append(f'<path d="M {pt(Lu)} L {pt(Bu)} L {pt(s_B)} L {pt(s_L)} Z" fill="#1A2845"/>')
            shapes.append(f'<path d="M {pt(Bu)} L {pt(Ru)} L {pt(s_R)} L {pt(s_B)} Z" fill="#101A2E"/>')
            shapes.append(f'<path d="M {pt(s_T)} L {pt(s_R)} L {pt(s_B)} L {pt(s_L)} Z" fill="{roof_color}" filter="url(#glow-soft)"/>')

        # Windows mapped in 3D isometric quads
        num_floors = int((bh - 10) // 8)
        for flr in range(num_floors):
            v0 = 6 + flr * 8
            # Left face
            for u0, du in [(0.15, 0.3), (0.55, 0.3)]:
                if rng.random() < 0.7:
                    wcolor = CP_YELLOW if rng.random() < 0.45 else CP_CYAN
                    w_quad = iso_quad(L, B, u0, du, v0, 4)
                    shapes.append(f'<path d="{w_quad}" fill="{wcolor}" opacity="0.95"/>')
            # Right face
            for u0, du in [(0.15, 0.3), (0.55, 0.3)]:
                if rng.random() < 0.6:
                    wcolor = CP_CYAN if rng.random() < 0.65 else CP_RED
                    w_quad = iso_quad(B, R, u0, du, v0, 4)
                    shapes.append(f'<path d="{w_quad}" fill="{wcolor}" opacity="0.85"/>')

        # Holographic Vertical Neon Signboards on Mega-Towers
        if bh > 65:
            sign_text = "ARASAKA" if level == 4 else ("PALPARD" if level == 3 else "NETRUNNER")
            sign_color = CP_RED if level == 4 else (CP_YELLOW if level == 3 else CP_CYAN)
            sign_quad = iso_quad(L, B, 0.15, 0.65, bh - 38, 28)
            holograms.append(f'<path d="{sign_quad}" fill="{sign_color}" fill-opacity="0.25" stroke="{sign_color}" stroke-width="1.2" filter="url(#glow-soft)"/>')
            holograms.append(f'<text x="{Bu[0]-6}" y="{Bu[1]-bh+24}" font-size="8.5" font-weight="900" letter-spacing="1" fill="{sign_color}" transform="rotate(-26 {Bu[0]-6} {Bu[1]-bh+24})">{sign_text}</text>')

        # Spire Antenna with Pulsing Warning Beacon
        spire_h = 28 if level >= 3 else 16
        spire_top = (Bu[0], Tu[1] - (16 if level >= 3 else 0) - spire_h)
        beacons.append(f'<line x1="{Bu[0]}" y1="{Tu[1] - (16 if level >= 3 else 0)}" x2="{spire_top[0]}" y2="{spire_top[1]}" stroke="{CP_CYAN}" stroke-width="1.5"/>')
        beacon_color = CP_RED if level == 4 else CP_YELLOW
        beacons.append(f'<circle class="dot-live" cx="{spire_top[0]}" cy="{spire_top[1]}" r="3" fill="{beacon_color}" filter="url(#glow-neon)"/>')

    # Skybridges connecting nearby towers
    if len(tall_towers) >= 2:
        for i in range(len(tall_towers) - 1):
            t1 = tall_towers[i]
            t2 = tall_towers[i+1]
            dist = math.hypot(t1[0] - t2[0], t1[1] - t2[1])
            if dist < 120:
                sb_y = min(t1[1] - t1[2] + 40, t2[1] - t2[2] + 40)
                skybridges.append(f'<line x1="{t1[0]}" y1="{sb_y}" x2="{t2[0]}" y2="{sb_y}" stroke="{CP_CYAN}" stroke-width="4" stroke-opacity="0.8" filter="url(#glow-soft)"/>')
                skybridges.append(f'<line x1="{t1[0]}" y1="{sb_y}" x2="{t2[0]}" y2="{sb_y}" stroke="#FFFFFF" stroke-width="1.5"/>')

    # Night City Sky: Stars, Full Moon with Holographic Target Rings
    stars = []
    sky_rng = random.Random(2077)
    for _ in range(50):
        sx = 380 + sky_rng.random() * 450
        sy = 55 + sky_rng.random() * 190
        s_fill = CP_CYAN if sky_rng.random() > 0.55 else (CP_YELLOW if sky_rng.random() > 0.85 else "#FFFFFF")
        s_r = 0.6 + sky_rng.random() * 0.8
        s_op = 0.35 + sky_rng.random() * 0.6
        stars.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{s_r:.1f}" fill="{s_fill}" opacity="{s_op:.2f}"/>')

    body = f"""
    <!-- Terminal Command Heading -->
    <g transform="translate({X}, 54)">
      <text x="0" y="0" class="yw" font-weight="800">&gt;&gt; [03 // NIGHT CITY 3D CONTRIBUTION SKYLINE]</text>
      <text x="0" y="24" class="dim"><tspan class="rd">[root@cyberdeck ~]#</tspan> ./netrunner --scan-skyline --sector watson --grid 53x7</text>
    </g>

    <!-- Deep Night City Atmosphere & Glowing Moon with Holographic Rings -->
    <g>{"".join(stars)}</g>
    <circle cx="{FR-90}" cy="135" r="54" fill="{CP_CYAN}" fill-opacity="0.08" filter="url(#glow-neon)"/>
    <circle cx="{FR-90}" cy="135" r="28" fill="none" stroke="{CP_YELLOW}" stroke-opacity="0.3" stroke-width="1" stroke-dasharray="4,4"/>
    <circle cx="{FR-90}" cy="135" r="18" fill="#F4F8FB" opacity="0.95"/>
    <circle cx="{FR-82}" cy="129" r="15" fill="{CP_BG}"/>

    <!-- Searchlight beam sweeping from corporate tower into the clouds -->
    <polygon class="spotlight-beam" points="350,300 280,40 330,40" fill="url(#beam-grad)" pointer-events="none"/>

    <!-- Flying Trauma Team AV (High-speed transport left to right) -->
    <g class="av-craft">
      <g transform="translate(0, 110)">
        <polygon points="0,4 22,0 30,6 20,10 0,7" fill="{CP_RED}" opacity="0.95"/>
        <polygon points="8,2 16,0 18,4 10,4" fill="{CP_YELLOW}"/>
        <line x1="30" y1="6" x2="70" y2="12" stroke="{CP_CYAN}" stroke-opacity="0.4" stroke-width="2.5"/>
        <circle class="av-bl" cx="0" cy="5" r="2.8" fill="{CP_RED}" filter="url(#glow-neon)"/>
        <circle class="av-bl" cx="30" cy="6" r="2.8" fill="{CP_CYAN}" filter="url(#glow-neon)"/>
      </g>
    </g>

    <!-- Second Flying Night City Police AV (Cruising right to left) -->
    <g class="av-craft-back">
      <g transform="translate(0, 165)">
        <polygon points="26,4 4,0 0,6 10,10 26,7" fill="{CP_CYAN}" opacity="0.85"/>
        <line x1="0" y1="6" x2="-35" y2="12" stroke="{CP_YELLOW}" stroke-opacity="0.35" stroke-width="2"/>
        <circle class="av-bl" cx="26" cy="5" r="2.2" fill="{CP_CYAN}" filter="url(#glow-neon)"/>
        <circle class="av-bl" cx="0" cy="6" r="2.2" fill="{CP_RED}" filter="url(#glow-neon)"/>
      </g>
    </g>

    <!-- Skyline Telemetry Box (Top Right) -->
    <g transform="translate({FR-20}, 245)" text-anchor="end">
      <rect x="-240" y="-18" width="240" height="74" fill="{CP_BLACK}" fill-opacity="0.75" stroke="{CP_CYAN}" stroke-opacity="0.4" stroke-width="1.2"/>
      <text x="-12" y="4" font-size="11" class="fg">ANNUAL COMMITS: <tspan class="yw" font-weight="800">{total_contribs}</tspan></text>
      <text x="-12" y="24" font-size="11" class="fg">SECTOR: <tspan class="cy">WATSON / CORPO PLAZA</tspan></text>
      <text x="-12" y="44" font-size="10" class="dim">MAPPED: 53 WEEKS ISOMETRIC SKYLINE</text>
    </g>

    <!-- Volumetric Ground Cyber-Fog & Street Reflections -->
    <rect x="{FL}" y="350" width="{FR-FL}" height="290" fill="url(#cyber-fog)" pointer-events="none"/>

    <!-- Rendered 3D Skyline Buildings & Features -->
    <g>
      {"".join(shapes)}
      {"".join(skybridges)}
      {"".join(holograms)}
      {"".join(beacons)}
    </g>

    <!-- Legend -->
    <g transform="translate({X}, 652)">
      <text x="0" y="0" font-size="11" class="dim">DISTRICT: SLUMS</text>
      <rect x="105" y="-10" width="12" height="12" fill="#1A2538"/>
      <rect x="123" y="-10" width="12" height="12" fill="#0E566E"/>
      <rect x="141" y="-10" width="12" height="12" fill="{CP_CYAN}"/>
      <rect x="159" y="-10" width="12" height="12" fill="{CP_YELLOW}"/>
      <rect x="177" y="-10" width="12" height="12" fill="{CP_RED}"/>
      <text x="200" y="0" font-size="11" class="dim">ARASAKA MEGA-TOWER</text>
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

    readme_content = f"""<p align="center">
  <img src="./assets/header.svg?v=3" width="100%" align="top" alt="PALPARD Netrunner Cyberdeck Header">
  <img src="./assets/telemetry.svg?v=3" width="100%" align="top" alt="Cyberdeck Telemetry">
  <img src="./assets/city.svg?v=3" width="100%" align="top" alt="Night City Skyline">
  <img src="./assets/arsenal.svg?v=3" width="100%" align="top" alt="Netrunner Quickhacks and Arsenal">
  <a href="https://t.me/PALPARD"><img src="./assets/links.svg?v=3" width="100%" align="top" alt="Neural Uplinks and Featured Deployment"></a>
  <img src="./assets/footer.svg?v=3" width="100%" align="top" alt="Cyberdeck Footer">
</p>
"""
    (HERE / "README.md").write_text(readme_content)
    print("All Cyberpunk 2077 slices and README generated successfully!")

if __name__ == "__main__":
    main()
