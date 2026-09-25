"""Original conceptual SVG artwork. No data is simulated or represented as measured."""
from pathlib import Path
from html import escape
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/articles/your-ai-remembers-you'
OUT.mkdir(parents=True, exist_ok=True)
INK, GREEN, BLUE, PAPER, LINE = '#243c32', '#41644e', '#466678', '#f3f1e9', '#bcc9bb'

def text(x,y,s,size=26,color=INK,font='Arial',extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" {extra}>{escape(s)}</text>'

def svg(name,w,h,body,title,desc):
    (OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><rect width="{w}" height="{h}" fill="{PAPER}"/>{body}</svg>',encoding='utf-8')

body=text(65,63,'Neurasoft / Dispatches',23,GREEN)
body+=text(65,185,'Your AI remembers you.',60,font='Georgia')+text(65,270,'Does that mean',60,font='Georgia')+text(65,348,'anyone is there?',60,font='Georgia')
body+=text(65,550,'Memory. Continuity. The question of experience.',25)
body+='<g fill="none" stroke="#bcc9bb" stroke-width="2">'
for x,y in [(805,110),(847,151),(889,192)]:
    body+=f'<rect x="{x}" y="{y}" width="182" height="250" rx="5" fill="{PAPER}"/>'
    for k in range(4): body+=f'<path d="M{x+24} {y+45+k*33}h112"/>'
body+='</g><path d="M828 343C720 400 778 492 913 438S1050 441 1090 515" fill="none" stroke="#41644e" stroke-width="7" stroke-linecap="round"/><circle cx="1090" cy="515" r="11" fill="#41644e"/>'
body+=text(780,89,'yesterday',22,BLUE)+text(970,571,'tomorrow',22,BLUE)
svg('memory-cover',1200,630,body,'Your AI remembers you. Does that mean anyone is there?','Conceptual artwork: overlapping pages connect to a winding path toward tomorrow.')

body=text(48,67,'What does the memory change?',36,font='Georgia')
body+=text(48,110,'Two paths through the same remembered detail.',22)
body+=f'<path d="M395 246V289H211V336M395 289H595V336" fill="none" stroke="{LINE}" stroke-width="3"/>'
def box(x,y,w,h,label,sub,color=GREEN):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#e4eadd" stroke="{LINE}"/>'+text(x+22,y+43,label,27,color)+text(x+22,y+77,sub,20)
body+=box(220,157,350,95,'Stored history','A note about an earlier choice')
body+=box(46,336,330,104,'Recall','Repeat the relevant detail',BLUE)
body+=box(423,336,330,104,'Use','Interpret the present choice')
body+=f'<path d="M588 440V477M588 581V620" stroke="{GREEN}" stroke-width="3"/>'
body+=box(423,477,330,104,'Decide','Let the history affect action')
body+=box(423,620,330,104,'Learn from the outcome','Carry consequences forward')
body+='<path d="M753 669H774V201H578" stroke="#41644e" fill="none" stroke-width="2" stroke-dasharray="5 5"/><path d="M582 196L572 201L582 206" fill="none" stroke="#41644e" stroke-width="2"/>'
body+=text(48,506,'The sentence is available.',23,BLUE)+text(48,547,'What happens next',23,BLUE)+text(48,580,'may still be unchanged.',23,BLUE)
body+=text(48,783,'Conceptual illustration. No experimental results shown.',20)
svg('memory-path',800,830,body,'Remembering a sentence versus using history','Stored history branches toward recalling a detail or using it to interpret a choice, act, and learn from the outcome.')

body=text(48,70,'Four questions. Four kinds of evidence.',34,font='Georgia')
rows=[('Capability','What can it do?','Look at results on the task.'),('Continuity','What carries forward?','Test the influence of earlier state.'),('Responsibility','How does it handle consequences?','Examine choices, limits, and repair.'),('Experience','Is there a subjective point of view?','An open scientific and philosophical question.')]
for i,(label,q,desc) in enumerate(rows):
    y=126+i*159
    body+=f'<line x1="48" y1="{y}" x2="752" y2="{y}" stroke="{LINE}"/>'
    body+=text(48,y+41,label,22,BLUE)+text(48,y+83,q,31,font='Georgia')+text(48,y+121,desc,21)
body+=text(48,815,'These are lenses, not a ladder or a consciousness score.',21)
svg('four-questions',800,860,body,'Four distinct questions about an AI system','Capability, continuity, responsibility, and subjective experience require different evidence. Progress in one does not automatically establish another.')
print('Wrote 3 original SVG illustrations.')
