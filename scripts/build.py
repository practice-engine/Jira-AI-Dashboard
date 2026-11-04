import json,datetime,collections as C,html,re
L=json.load(open('/tmp/w/classified.json')); CJ=json.load(open('/tmp/w/clusters.json'))
import sys
PUBLIC='--public' in sys.argv
OUT=sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else '/sessions/adoring-awesome-davinci/mnt/outputs/ESS_open_tickets_dashboard.html'
PHI=re.compile(r'\d{6,}|\bMRN?\b|MR ?#|\bDOB\b|Shannon Green|larry rodney',re.I)
def red(s):
    if not PUBLIC: return s
    return 'Patient-specific ticket (details redacted)' if PHI.search(s or '') else s
for x in L:
    x['summary']=red(x['summary'])
    if PUBLIC: x['desc']=''; x['reporter']=''
K={x['key']:x for x in L}
TODAY=datetime.date(2026,11,4)
memb=C.defaultdict(list)
for g in CJ['groups']:
    for k in g['keys']: memb[k].append(g['name'])
rows=[]
for x in L:
    age=(TODAY-datetime.date.fromisoformat(x['created'])).days
    rows.append(dict(k=x['key'],s=x['summary'] or '',st=x['status'],p=x['priority'],ty=x['type'],c=x['created'],a=age,
      o=(x['org'] or [''])[0],r=x['reporter'] or '',as_=x['assignee'] or 'Unassigned',th=x['theme'],kd=x['kind'],
      n=x['noise'] or '',au=x['automation'] or '',g=memb.get(x['key'],[]),d=re.sub(r'\\?\*{1,2}|\\_|(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])|\\','',x['desc'])[:260],nc=x['ncomments']))
# curated likely-duplicate pairs (reviewed from text-similarity output)
PAIRS=[('ESS-22197','ESS-26830','Same Granville “EHR SSO Physical Exam coding errors” issue – 26830 says “(still)”'),
 ('ESS-12892','ESS-26771','Patient-portal email questions'),('ESS-9198','ESS-16217','Upgrade request / recommendation'),
 ('ESS-13177','ESS-13342','Missing/open claim blocks changing responsibility to insurance'),
 ('ESS-20371','ESS-24066','Aging report for high-dollar CPTs'),('ESS-22856','ESS-23081','MFA dialog changes (email option / remove Authy)'),
 ('ESS-20806','ESS-26875','Third-party FHIR API access requests'),('ESS-20565','ESS-26868','Bluefield rules-engine request vs. bug'),
 ('ESS-19344','ESS-20849','New path-lab interface requests (PathGroup / QDX)'),('ESS-14228','ESS-21089','INSREG exception hold requests'),
 ('ESS-22165','ESS-26640','Inactive patients can still book online'),('ESS-11944','ESS-12807','Online booking preferences / deposits'),
 ('ESS-10048','ESS-24466','Face / head anatomical location options'),('ESS-22316','ESS-22320','Derm of Boca encounter creation & DUP holds'),
 ('ESS-21078','ESS-21093','PBI table updates (location / budget tables)'),('ESS-17684','ESS-19453','ERA vs paper payment data requests'),
 ('ESS-22433','ESS-24931','Net / accrual revenue dataset logic'),('ESS-4145','ESS-25307','Referring provider / PCP on demographics'),
 ('ESS-24159','ESS-26803','Patients can’t access records via portal'),('ESS-6587','ESS-11437','HIPAA form in online registration'),
 ('ESS-25248','ESS-26378','Patient balance / claim-track bugs in portal'),('ESS-26722','ESS-26482','CPT G2211 (same request twice)'),
 ('ESS-26755','ESS-26599','Same MRN 11798686 – can’t sign out of chart'),('ESS-26601','ESS-26598','Same MRN 11805287 – forwarded twice'),
 ('ESS-26847','ESS-26862','Alexandria LeDue new-provider alert + replies (26848, 26851, 26852)'),('ESS-26856','ESS-26860','Cameron Clements alert + reply')]
pairs=[dict(a=a,b=b,why=(re.sub(r'MRN \d+','patient',w) if PUBLIC else w),sa=K[a]['summary'],sb=K[b]['summary']) for a,b,w in PAIRS if a in K and b in K]
AUTO_INFO={
 'Self-service provider & user lifecycle (onboard / term / credentialing)':'Every new provider and every termination arrives as an email that an agent re-keys (NPI, credentialing, iPad, templates). Replies on the same thread spawn new tickets. A structured onboarding/offboarding form with auto-provisioning removes the ticket entirely.',
 'User-level notification preferences (opt-out of registration / patient-update emails)':'Providers are flooded with “Patient information update” / registration emails and ask support to turn them off one by one. A per-user notification settings page (or default OFF for providers) eliminates this whole category.',
 'Self-service note unlock / amend / DOS & provider change (with audit trail)':'Agents are unlocking notes, changing DOS and rendering/billing provider on request. Role-based self-service with an audit trail lets practice managers do it themselves.',
 'Duplicate patient/encounter/charge detection + merge tool':'Duplicate accounts, encounters, copays and CPTs are fixed manually by agents/Tier2. Duplicate detection at registration + a practice-level merge tool would prevent and self-resolve these.',
 'Practice-configurable lists (document types, cancel reasons, library codes)':'Adding a document type, cancel reason or library code is pure configuration, yet every request is a ticket. Expose these lists in practice admin settings.',
 'Practice-configurable billing rules builder (EQ holds, rules engine)':'A steady stream of “new exception hold” / rules-engine requests (J-codes, MOD59, INSREG, telehealth). A rules builder with templates for RCM admins would remove dev/agent effort.',
 'Self-service report builder & scheduled exports':'Most reporting tickets are “add a column / filter / date range / export” to existing reports. Column pickers, saved filters, CSV export and scheduled subscriptions cover most of them.',
 'Device enrollment & account self-service (iPad enable, MFA, lockouts)':'iPad enablement, lockouts, MFA and overseas-access requests are routine admin work. Self-service password reset, MFA options and an admin “enable iPad” toggle remove them.',
 'Configurable online-scheduler rules (age, insurance, provider eligibility)':'Practices want to control who can book online (minors, Medicaid, inactive patients, insurance required, translator needed, first-available). These should be scheduler settings, not tickets.',
 'Bulk patient messaging / broadcast (closures, recalls)':'Offices ask support to send mass texts (e.g., power-outage closure) or run outreach. A self-service broadcast tool for a day’s schedule handles this instantly.',
 'Fax routing & webhook self-configuration':'Documo webhooks, fax porting and fax-queue filters require agent setup. A fax settings page with webhook config and routing rules reduces these.'}
au=C.Counter(r['au'] for r in rows if r['au'])
OPP=json.load(open('/tmp/w/opp.json'))
auto=[]
for k,v in au.most_common():
    m=OPP[k]; ks=sorted([r for r in rows if r['au']==k],key=lambda r:r['c'],reverse=True)
    auto.append(dict(name=k,count=v,keys=[r['k'] for r in ks],ex=[dict(k=r['k'],s=r['s'],c=r['c']) for r in ks[:3]],**m))
groups=sorted(CJ['groups'],key=lambda g:-len(g['keys']))
for g in groups: g['items']=[dict(k=k,s=K[k]['summary'],c=K[k]['created'],st=K[k]['status']) for k in g['keys']]
DATA=dict(rows=rows,groups=groups,pairs=pairs,auto=auto,today=str(TODAY))
js=json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')
tpl=open(sys.argv[sys.argv.index('--tpl')+1] if '--tpl' in sys.argv else 'template.html').read()
open(OUT,'w').write(tpl.replace('/*__DATA__*/',js).replace('/*__LOGO__*/',open('/tmp/w/logo.b64').read()).replace('/*__LOGOW__*/',open('/tmp/w/logow.b64').read()))
print('ok',len(rows),len(groups),len(pairs),len(auto))
# stats for findings
k=C.Counter(r['kd'] for r in rows); print(k)
print(sum(1 for r in rows if r['au']), 'automation-tagged')
print(sum(len(g['keys']) for g in groups), len(set(x for g in groups for x in g['keys'])))
