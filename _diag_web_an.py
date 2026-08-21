import json, re, collections
d = json.load(open("_diag_web_enum.json",encoding="utf-8"))
LAYOUT = ['top','left','right','bottom','width','height','margin','padding','font-size','line-height','border-width','flex-basis','gap','max-height','min-height','max-width','min-width','border-radius','box-shadow','filter','background','background-color','color','border-color']
HEAVY = ['top','left','right','bottom','width','height','margin','padding','font-size','line-height','max-height','min-height','max-width','min-width','gap','flex-basis','border-width']

print("="*70); print("TRANSICIONES POR PAGINA (unicas)")
seen=set()
durs=collections.Counter()
for pg,r in d.items():
    if 'error' in r: continue
    for t in r['transitions']:
        key=(t['sel'],t['value'])
        if key in seen: continue
        seen.add(key)
        props=t['value']
        heavy=[h for h in HEAVY if re.search(r'(^|[\s,])'+re.escape(h)+r'($|[\s,])',props)]
        flag=' <<< LAYOUT' if heavy else ''
        allp = 'all' in props.split()
        if allp: flag += ' <<< ALL'
        print(f"[{pg}] {t['sel']}\n     {props}{flag}")
        for m in re.findall(r'([\d.]+)m?s', props):
            v=float(m)
            if v>=20: v=v/1000.0
            durs[v]+=1
print()
print("="*70); print("HISTOGRAMA DURACIONES (s -> n reglas)")
for k in sorted(durs): print(f"  {k}s : {durs[k]}")
print()
print("="*70); print("ANIMACIONES")
for pg,r in d.items():
    if 'error' in r: continue
    for a in r.get('animations',[]):
        print(f"[{pg}] {a['sel']}  ->  {a['value']}   {a['ctx']}")
print()
print("="*70); print("KEYFRAMES")
kfseen=set()
for pg,r in d.items():
    if 'error' in r: continue
    for k in r.get('keyframes',[]):
        if k['name'] in kfseen: continue
        kfseen.add(k['name'])
        print(f"[{pg}] @keyframes {k['name']}: {' '.join(k['frames'])[:300]}")
print()
print("="*70); print("ELEMENTOS CON ANIMACION INFINITA (en DOM al cargar)")
for pg,r in d.items():
    if 'error' in r: continue
    n=len(r.get('infiniteEls',[]))
    print(f"[{pg}] total={n}")
    agg=collections.Counter()
    for e in r.get('infiniteEls',[]):
        agg[(e['anim'],e['cls'][:60],e['dur'])]+=1
    for k,v in agg.items(): print(f"     {v}x anim={k[0]} dur={k[2]} class='{k[1]}'")
print()
print("="*70); print("REDUCED MOTION")
for pg,r in d.items():
    if 'error' in r: continue
    if not r.get('reducedMotion'): print(f"[{pg}] SIN @media prefers-reduced-motion")
    else:
        for rm in r['reducedMotion']: print(f"[{pg}] {rm['body'][:400]}")
