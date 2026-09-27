"""Draw original conceptual editorial figures for the 2026-09-27 article.

These are explanatory illustrations, not plots of measured neural or clinical data.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/articles/where-does-your-body-end"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#203b34"
SAGE = "#54775f"
TEAL = "#537c86"
CLAY = "#bc8167"
PAPER = "#f5f2e9"
MIST = "#e3e9df"
LINE = "#b8c9ba"


def svg(name: str, width: int, height: int, title: str, description: str, body: str) -> None:
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f8f5eb"/><stop offset="1" stop-color="#eaf0e7"/></linearGradient>
  <radialGradient id="aura"><stop stop-color="#bed6c3" stop-opacity=".74"/><stop offset="1" stop-color="#bed6c3" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#769b81" opacity=".26"/></pattern>
  <style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK}}}.serif{{font-family:Georgia,serif}}.eyebrow{{font-size:19px;letter-spacing:4px;fill:{SAGE}}}.small{{font-size:18px}}.label{{font-size:21px;font-weight:700}}.muted{{fill:#597268}}</style>
</defs><rect width="{width}" height="{height}" fill="url(#paper)"/>{body}</svg>'''
    (OUT / f"{name}.svg").write_text(document, encoding="utf-8")


cover = f'''
<rect x="604" y="0" width="596" height="630" fill="url(#dots)" opacity=".55"/>
<circle cx="860" cy="303" r="246" fill="url(#aura)"/>
<path d="M622 491 C707 528 808 522 875 450" fill="none" stroke="{LINE}" stroke-width="2"/>
<path d="M708 467 C787 409 827 361 857 316" fill="none" stroke="{SAGE}" stroke-width="43" stroke-linecap="round"/>
<path d="M707 467 C789 410 827 362 856 316" fill="none" stroke="#d8e3d6" stroke-width="31" stroke-linecap="round"/>
<path d="M846 334 Q822 302 840 280 Q856 263 872 279 L895 298" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>
<path d="M858 349 Q842 326 858 311 Q877 295 894 313" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>
<path d="M863 278 L1081 145" fill="none" stroke="{CLAY}" stroke-width="13" stroke-linecap="round"/>
<path d="M1077 122 L1095 160 M1058 136 L1076 174 M1095 112 L1113 149" fill="none" stroke="{CLAY}" stroke-width="8" stroke-linecap="round"/>
<path d="M894 370 C1035 359 1159 298 1134 162" fill="none" stroke="{TEAL}" stroke-width="3" stroke-dasharray="6 13" stroke-linecap="round"/>
<path d="M865 389 C970 418 1089 446 1167 422" fill="none" stroke="{LINE}" stroke-width="2"/>
<circle cx="866" cy="318" r="123" fill="none" stroke="{SAGE}" stroke-opacity=".38" stroke-width="2"/>
<circle cx="1090" cy="145" r="11" fill="{CLAY}"/><circle cx="1090" cy="145" r="24" fill="none" stroke="{CLAY}" stroke-opacity=".42"/>
<text x="719" y="565" font-size="19" letter-spacing="2" fill="{SAGE}">SKIN</text>
<text x="1030" y="519" font-size="19" letter-spacing="2" fill="{TEAL}">REACH</text>
<text class="eyebrow" x="68" y="82">NEURASOFT / FIELD NOTES</text>
<text class="serif" x="68" y="208" font-size="68">Where does</text>
<text class="serif" x="68" y="298" font-size="68">your body end?</text>
<path d="M69 332 H528" stroke="{CLAY}" stroke-width="5"/>
<text x="69" y="386" font-size="25" fill="{SAGE}">The borders we use are not all skin.</text>
<text x="69" y="576" font-size="20">Neurasoft editorial · 27 September 2026</text>
'''
svg("body-border-cover", 1200, 630, "Where does your body end?", "A hand and a rake sit inside three different conceptual boundaries: skin, nearby sensory space, and tool-enabled reach.", cover)


borders = f'''
<text class="eyebrow" x="48" y="52">NEURASOFT / EXPLAINER 01</text>
<text class="serif" x="48" y="110" font-size="43">One reach. Three different borders.</text>
<text class="muted" x="49" y="147" font-size="20">A single action can be described three ways.</text>
<rect x="36" y="187" width="728" height="424" rx="22" fill="#edf2ea" stroke="{LINE}"/>
<circle cx="292" cy="395" r="171" fill="url(#aura)"/>
<circle cx="283" cy="393" r="133" fill="none" stroke="{TEAL}" stroke-width="3" opacity=".65"/>
<path d="M38 501 C139 515 202 477 271 410" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/>
<path d="M46 501 C149 507 207 463 275 405" fill="none" stroke="#c1d2bb" stroke-width="30" stroke-linecap="round"/>
<path d="M273 407 Q252 376 271 350 Q291 332 315 357 L331 372" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>
<path d="M282 417 Q274 399 289 383 Q308 370 326 389" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>
<path d="M301 355 L615 278" stroke="{CLAY}" stroke-width="13" stroke-linecap="round"/>
<path d="M604 251 L619 313 M623 246 L637 306 M645 243 L659 304" stroke="{CLAY}" stroke-width="8" stroke-linecap="round"/>
<path d="M319 426 C453 474 620 435 686 293" fill="none" stroke="{SAGE}" stroke-width="3" stroke-dasharray="8 10"/>
<circle cx="650" cy="275" r="19" fill="{CLAY}" opacity=".28"/><circle cx="650" cy="275" r="8" fill="{CLAY}"/>
<circle cx="271" cy="407" r="18" fill="none" stroke="{INK}" stroke-width="3"/>
<circle cx="411" cy="330" r="9" fill="{TEAL}"/><circle cx="242" cy="272" r="8" fill="{TEAL}"/>
<path d="M275 407 L118 224" stroke="{INK}" stroke-width="2"/>
<rect x="62" y="191" width="216" height="64" rx="11" fill="#f7f6ef" stroke="{LINE}"/>
<text class="label" x="77" y="217">1 · Skin</text><text class="small muted" x="77" y="240">Physical body surface</text>
<path d="M411 330 L461 220" stroke="{TEAL}" stroke-width="2"/>
<rect x="472" y="189" width="271" height="68" rx="11" fill="#f7f6ef" stroke="{LINE}"/>
<text class="label" x="489" y="217">2 · Nearby space</text><text class="small muted" x="489" y="241">Senses meet around the hand</text>
<path d="M608 430 L601 504" stroke="{SAGE}" stroke-width="2"/>
<rect x="432" y="510" width="308" height="75" rx="11" fill="#f7f6ef" stroke="{LINE}"/>
<text class="label" x="448" y="538">3 · Tool-linked reach</text><text class="small muted" x="448" y="562">What the action makes accessible</text>
<text class="muted" x="48" y="658" font-size="19">Ownership and agency are separate questions again.</text>
<text x="48" y="705" font-size="18" fill="{SAGE}">CONCEPTUAL MODEL · Curves are not measured neural borders.</text>
'''
svg("three-useful-borders", 800, 748, "One reach, three different borders", "A single hand-and-rake action is shown with separate visual cues for the physical skin, multisensory nearby space, and tool-linked reachable space. These are conceptual distinctions, not measured boundaries.", borders)


conversation = f'''
<text class="eyebrow" x="48" y="52">NEURASOFT / EXPLAINER 02</text>
<text class="serif" x="48" y="111" font-size="44">A prosthesis is a conversation.</text>
<text class="muted" x="49" y="148" font-size="20">Control and returning information form a loop.</text>
<rect x="42" y="196" width="300" height="110" rx="19" fill="#e1eade" stroke="{LINE}"/>
<text class="label" x="68" y="239">PERSON</text><text x="68" y="272" font-size="23">Intended movement</text>
<rect x="456" y="196" width="300" height="110" rx="19" fill="#e4ecee" stroke="{LINE}"/>
<text class="label" x="482" y="239">DEVICE</text><text x="482" y="272" font-size="23">Movement and contact</text>
<rect x="231" y="402" width="336" height="114" rx="19" fill="#f0e5dc" stroke="#d7b9a7"/>
<text class="label" x="260" y="447">RETURNING SIGNAL</text><text x="260" y="480" font-size="22">Sight, sound, or touch</text>
<path d="M344 252 H443" stroke="{SAGE}" stroke-width="5" stroke-linecap="round"/>
<path d="M431 240 L449 252 L431 264" fill="none" stroke="{SAGE}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="362" y="231" font-size="17" fill="{SAGE}">CONTROL</text>
<path d="M604 310 V351 Q604 370 580 370 H425 V389" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M413 379 L425 396 L437 379" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M230 458 H153 Q126 458 126 430 V336 Q126 310 153 310 H193" fill="none" stroke="{TEAL}" stroke-width="5" stroke-linecap="round"/>
<path d="M180 298 L198 310 L180 322" fill="none" stroke="{TEAL}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="45" y="395" font-size="18" fill="{TEAL}">NEXT</text><text x="45" y="419" font-size="18" fill="{TEAL}">ADJUSTMENT</text>
<rect x="43" y="562" width="713" height="125" rx="18" fill="#f8f7f0" stroke="{LINE}"/>
<circle cx="84" cy="610" r="18" fill="{SAGE}" opacity=".18"/><circle cx="84" cy="610" r="7" fill="{SAGE}"/>
<text class="label" x="118" y="602">Felt ownership?</text>
<text class="small muted" x="118" y="632">A possible experience to ask about, not an automatic output</text>
<text class="small muted" x="118" y="659">of movement or feedback.</text>
<text x="48" y="735" font-size="18" fill="{SAGE}">CONCEPTUAL DESIGN LOOP · Not a clinical result.</text>
'''
svg("prosthesis-conversation", 800, 778, "A prosthesis is a conversation", "Conceptual loop: a person's intended movement drives a device that moves and contacts the world; available sight, sound, or touch returns to inform the next adjustment. Felt ownership is a separate possible experience, not an automatic output.", conversation)

print("Wrote three original conceptual SVG figures.")
