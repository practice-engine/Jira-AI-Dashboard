import json,re,math,collections as C
L=json.load(open('/tmp/w/classified.json')); K={x['key']:x for x in L}
R=lambda p: re.compile(p,re.I)
CL=[ # name, regex, scope('s'=summary,'sd'=summary+desc), linkType suggestion
 ('Notes won’t close / sign out – stuck “saving to cloud”', R(r'saving (encounter )?to (the )?cloud|unable to close|can.?t close|closing a note|close (out )?(the |this )?note|closing out the note|sign(ing)? out (of )?(the |this )?chart|sign this chart|sign out chart|finalize this note|online save|save locally|cannot finalize|already signed out'),'sd'),
 ('Turn off patient-info / registration notification emails to providers', R(r'patient info(rmation)? update|registration notif|registration emails|patient registration emails|scheduling notifications|emails from ederm about patient forms|email notifications|receiving these emails|online registration em'),'sd'),
 ('New Provider Alert – Alexandria LeDue (same thread)', R(r'alexandria ledue'),'s'),
 ('New Provider Alert – Cameron Clements (same thread)', R(r'cameron clements'),'s'),
 ('Unlock note / locked chart requests', R(r'unlock|locked chart'),'s'),
 ('Old “ghost” faxes / faxes for another office', R(r'ghost fax|fax(ed)? received|incorrectly routed fax|efax dated|fax dated'),'s'),
 ('Duplicate patient accounts / merge requests', R(r'duplicate accounts?|merging|appearing twice|fake patients|delete duplicate charts|duplicate info in same chart'),'s'),
 ('Duplicate charges / payments / encounters', R(r'duplicate (charge|encounter|copay|cpt|payment)|posted twice|us path duplicate|duplicating batches|pathology duplicate|duplicate cpt'),'sd'),
 ('Add / change document types', R(r'document types?|add(ing)? to document|document drop|new categories in documents|document list|ederm documents|deleted.{0,3} document'),'s'),
 ('CPT G2211', R(r'g2211'),'s'),
 ('Post-update iPad regressions & slowness', R(r'new update|latest ios|new ederm update|update 2\.7|search function for patients is unbearably|offline message|^offline|offline red banner'),'sd'),
 ('Online scheduler – minors / age limits', R(r'minors?|under 18|age limit|patients under the age'),'sd'),
 ('Online scheduler – insurance & Medicaid rules', R(r'online schedul\w*.{0,40}(insurance|medicaid)|required insurance|credentialed|medicaid policies'),'sd'),
 ('ZocDoc integration & reporting', R(r'zocdoc'),'s'),
 ('Pathology results log – export / CSV / untreated filter', R(r'path(ology)? results (portal|log)|csv report for path|untreated|declined treatment|pathlog treatment|pathology results log'),'sd'),
 ('Referral / account number on pathology requisition', R(r'referral number.{0,30}requisition|requisition.{0,40}referral|account number for labcorp|referral number to (pathology|biopsy)'),'sd'),
 ('Primary / cell phone on prescriptions', R(r'(primary|cell) phone.{0,20}(rx|prescri)'),'s'),
 ('Prior authorization / referral tracking', R(r'prior authorization|authorization/referrals|authorization# on claim'),'s'),
 ('New exception holds – J-codes / units / NDC', R(r'j\d{4}|j-codes?|j code|\bndc\b'),'s'),
 ('MOD59 exception holds', R(r'mod ?59'),'s'),
 ('Telehealth codes holds / pricing', R(r'telehealth'),'s'),
 ('Utilization report – POS limitation', R(r'utilization report: pos'),'s'),
 ('Knack / RPA file replication', R(r'knack'),'s'),
 ('Documo eFax webhooks & API', R(r'documo|web-?hook'),'s'),
 ('Server low-disk-space alerts (Byte Solutions)', R(r'low disk space'),'s'),
 ('Surescripts certificate notices', R(r'surescripts'),'s'),
 ('Cancel reasons for appointments', R(r'cancel(lation)?s? reasons?|add cancel reason|adding a reason to cancel|cancel appointmet reason'),'s'),
 ('Patient balance wrong / confusing on portal or registration link', R(r'portal balance|displayed balances|bug patient balance|patient balances'),'s'),
 ('Patients cancel / reschedule by text by mistake', R(r'cancel by text|accidentally cancel|hit the .reschedule. button via text|text message reply options'),'sd'),
 ('Audit trail requests', R(r'audit'),'s'),
 ('Hide / remove preliminary notes', R(r'preliminary notes'),'s'),
 ('Self-pay encounter type & codes', R(r'self-?pay'),'s'),
 ('Credit card on file / online booking deposits', R(r'cc on file|credit card on file|credit card for cosmetic|cc on filea|card before a transaction'),'s'),
 ('Payment plans', R(r'payment plan'),'s'),
 ('Emergency contact handling', R(r'emergency contact'),'s'),
 ('Taxonomy codes on claims', R(r'taxonomy'),'s'),
 ('Rendering provider default / auto-populate', R(r'rendering provider (field|default)|provider auto-population'),'s'),
 ('Medication cannot be added / med lists', R(r'medication that cannot|medications? report|pt medication list|^medications$'),'s'),
 ('Online scheduling – notify practice / first available', R(r'notification of online scheduling|first available|next available'),'sd'),
 ('Patient statements content & queues', R(r'patient statements?|statement queue|paper statement'),'s'),
 ('Insurance aging report fixes & filters', R(r'insurance aging'),'s'),
 ('Payment Monitoring / Payment PBI report', R(r'payment (monitoring|report)'),'s'),
 ('Billing Exceptions report (PBI)', R(r'billing exceptions'),'s'),
 ('Referring provider setup & demographics', R(r'referring provider'),'s'),
 ('Mohs / untreated cancer reports', R(r'mohs (referral|documents)|melanoma report|skin cancer log|untreated cancer'),'s'),
 ('eFax queue filters, logs & failures', R(r'efax|fax failures|fax errors|faxing log|efax tank'),'s'),
 ('Sticky notes / important patient alerts', R(r'sticky|pacemaker alert|very important notes'),'sd'),
 ('Tasks – delete / assign / categorize', R(r'delet(e|ing) tasks?|task "assign|task message|problem with tasks|task issue|tasking issue'),'s'),
 ('ERA not posting / missing remits', R(r'\bera\b.{0,40}(not|did not|missing)|remit not found|eras did not|era for auto post|not posting correctly'),'s'),
 ('Templates – delete, clean up, last-used date', R(r'template'),'s'),
 ('iPad printing / requisition from iPad', R(r'ipad printing|req form from ipad|requisition not printing|sending labs from ipad'),'s'),
]
groups=[]; seen=set()
for name,r,scope in CL:
    m=[x for x in L if r.search((x['summary'] or '')+(' '+x['desc'][:350] if scope=='sd' else ''))]
    if len(m)>=2:
        m.sort(key=lambda x:x['created'])
        groups.append(dict(name=name,keys=[x['key'] for x in m],primary=m[0]['key']))
        seen.update(x['key'] for x in m)
# TF-IDF near-duplicate pairs (pure python)
STOP=set('the a an to of and for in on is it this that be with from at as are we our can you your please i not have has was by or if do but they their them there so any my me us mrn dos thank thanks hello hi good morning afternoon team ederm edermx patient patients request enhancement re fw fwd'.split())
def toks(x):
    t=re.findall(r'[a-z][a-z0-9]{2,}',((x['summary'] or '')*1+' '+(x['summary'] or '')+' '+x['desc'][:400]).lower())
    return [w for w in t if w not in STOP and not w.startswith('mydermgroup')]
docs={x['key']:C.Counter(toks(x)) for x in L}
df=C.Counter(w for d in docs.values() for w in d)
N=len(L)
vec={}
for k,d in docs.items():
    v={w:(1+math.log(c))*math.log(N/df[w]) for w,c in d.items() if df[w]>1}
    n=math.sqrt(sum(a*a for a in v.values())) or 1
    vec[k]={w:a/n for w,a in v.items()}
keys=list(vec); pairs=[]
inv=C.defaultdict(set)
for k,v in vec.items():
    for w in v: inv[w].add(k)
for i,a in enumerate(keys):
    cand=set()
    for w in vec[a]: 
        if df[w]<40: cand|=inv[w]
    for b in cand:
        if b<=a: continue
        s=sum(vec[a][w]*vec[b].get(w,0) for w in vec[a])
        if s>=0.42: pairs.append((round(s,2),a,b))
pairs.sort(reverse=True)
# keep pairs not both in same curated group
gk={}
for gi,g in enumerate(groups):
    for k in g['keys']: gk.setdefault(k,set()).add(gi)
def st(x): return set(w for w in re.findall(r'[a-z][a-z0-9]{2,}',(x['summary'] or '').lower()) if w not in STOP)
extra=[p for p in pairs if not (gk.get(p[1],set())&gk.get(p[2],set())) and (st(K[p[1]])&st(K[p[2]])) and not (K[p[1]]['theme']==K[p[2]]['theme']=='Provider onboarding & offboarding')]
json.dump(dict(groups=groups,pairs=[dict(score=s,a=a,b=b) for s,a,b in extra[:80]]),open('/tmp/w/clusters.json','w'))
print(len(groups),'groups covering',len(seen))
for g in sorted(groups,key=lambda g:-len(g['keys'])): print(len(g['keys']),g['name'])
print('extra pairs',len(extra))
for s,a,b in extra[:60]: print(s,a,K[a]['summary'][:45],'||',b,K[b]['summary'][:45])
