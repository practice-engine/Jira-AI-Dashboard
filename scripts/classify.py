import json,re,collections as C
L=json.load(open('/tmp/w/tickets.json'))
R=lambda p: re.compile(p,re.I)
THEMES=[
 ('Provider onboarding & offboarding', R(r'new (mohs )?provider|new partner alert|termed \d|resignation|provider agreement|new providers|updates needed to provider records')),
 ('Notification emails (unwanted)', R(r'patient info(rmation)? update|registration notif|registration emails|scheduling notifications|emails from ederm about patient forms|email notifications|^email error|online registration em')),
 ('Infrastructure / server alerts', R(r'low disk space')),
 ('Note sign-off, closing & unlock', R(r'unlock|locked chart|clos(e|ing)( out)? (the |a |this )?note|sign (out|this chart)|sign.{0,20}chart|saving (encounter )?to (the )?cloud|finaliz|prelim|charts on hold|kicked out of notes|^chart provider change|change the dos|rendering provider switch|save locally|online save')),
 ('Patient record corrections & duplicates', R(r'duplicate (account|encounter|charge|copay|site|info|cpt|batches|chart)|duplicate/|merg|delete duplicate|missing (visit|office) note|lost records|appearing twice|dupilcate|pathology duplicate|showing up twice|posted twice|fake patients|data corruption|patient information update$')),
 ('eRx & medications', R(r'escri|eprescrib|e-?rx|medication|surescripts|pharmac|refill|scripts?\b|days supply|prescri|drug card|patient provided drugs|rx coverage|\brxs?\b')),
 ('Pathology & labs', R(r'\bpath\b|pathology|path report|requisition|biops')),
 ('Reporting & Power BI', R(r'report|pbi|power bi|data ?set|\baging|export|csv|analytics|sql|update table|location table|utilization|evaluating jan|rev rec|payment data|data request|log for garrison|kyriba|835 replication')),
 ('Pathology & labs', R(r'path|biops|requisition|\blabs?\b|lab order|microbiology|labcorp|qdx|specimen|skin cancer log|melanoma|mohs')),
 ('eFax & document management', R(r'fax|documo|document|scan|attachments|hipaa form|appeal letter|upload')),
 ('Online scheduling, self-registration & check-in', R(r'online sched|online book|self.?reg|check.?in link|registration link|online registration|zocdoc|qr code|kiosk|pre-?registration|intake form|scheduler|appointments done online|scheduling online|online medical|registration request|first available|consent by ?pass|check in link')),
 ('Billing rules & exception queue', R(r'exception|rules engine|\bhold\b|holds|mod ?59|j-?codes?|j\d{4}|\bndc\b|coding|cpt|icd|taxonomy|claim|837|denial|global|upcod|down-?coding|bundl|hcpcs|telehealth codes|eligib|unit of measure|\buom\b|hud claims|modifier|zero bills|\$0\.00|billing default|filing indicator|charge codes|validat|medicare|medicaid|abn|bill claims|hospice|rendering provider|payer|insurances|self-pay')),
 ('Payments, posting & statements', R(r'\bera\b|remit|835|posting|\bpost\b|auto ?post|uac|refund|lockbox|payment|copay|credit card|\bcc\b|paymyderm|pay my derm|statement|balance|collection|receipt|sales tax|takeback|recoup|deposit|capitation|\bbill|convenience fee|inventory|batches|cosmetic|ledger')),
 ('Devices, login & access', R(r'ipad|\bmdm\b|log ?in|locked out|mfa|authy|sso|access|overseas|offline|password|legacy|super user|permission|row level|security code|scanner|ios update|corporate user|staff login')),
 ('Integrations & interfaces', R(r'fhir|knack|interface|webhook|integration|hl7|\bema\b|ellkay|relatient|b\.?well|flexpa|\bapi\b|recall health')),
 ('Patient messaging & portal', R(r'text|mass text|\bsms\b|reminder|confirmation|portal|secure messag|recall|opt.?in|survey|marketing|notification|send patients|email')),
 ('Tasks & inbox', R(r'task|sticky|inbox|messaging pools|number bubble')),
 ('Scheduling & appointments', R(r'schedul|appointment|appt|appoit|cancel|block|column|wait ?list|calendar|reschedul|room and times|translator|auto refresh|refresh')),
 ('Demographics & insurance setup', R(r'demographic|insurance|emergency contact|phone|address|referring provider|\bpcp\b|occupation|non bi|full name|name disappears|quick add|dob|family accounts|responsible billing|contact|referral|authorization|ins card|patient card|field')),
 ('Performance & stability', R(r'slow|search|glitch|white screen|update|crash|not loading|freez')),
 ('Clinical documentation & templates', R(r'template|note|descriptor|exam|plan of care|anatomical|eyelid|photo|history|alert|allerg|chart|visit|documentation|laterality|assessment|instructions|dashboard|templetes|face')),
]
NOISE=[
 ('Automated server-monitoring alert', R(r'low disk space')),
 ('Vendor / third-party notice', R(r'surescripts certificate|certificate updates surescripts|payment receipt from drummond|letter from hhs')),
 ('Unsolicited vendor / partner outreach', R(r'fhir access for antaeus|flexpa')),
]
# reply-thread duplicates and misroutes identified by reading descriptions
NOISE_KEYS={
 'ESS-26848':'Reply-all acknowledgement ("Received. Thank you") on existing ticket',
 'ESS-26851':'Reply on existing New Provider Alert thread (dup of ESS-26847)',
 'ESS-26852':'Reply on existing New Provider Alert thread (dup of ESS-26847)',
 'ESS-26860':'Reply on existing New Provider Alert thread (dup of ESS-26856)',
 'ESS-26598':'Forward of same issue already logged as ESS-26601',
 'ESS-26599':'Same issue already logged as ESS-26755 (same MRN)',
 'ESS-26482':'Duplicate of ESS-26722 (CPT G2211)',
}
KEY_THEME={'ESS-26875':'Integrations & interfaces','ESS-20806':'Integrations & interfaces','ESS-21418':'Vendor / external notices','ESS-26448':'Vendor / external notices','ESS-22803':'Vendor / external notices','ESS-22643':'Vendor / external notices','ESS-18649':'Billing rules & exception queue','ESS-18774':'Patient messaging & portal','ESS-16278':'Demographics & insurance setup','ESS-15325':'Note sign-off, closing & unlock','ESS-18357':'Billing rules & exception queue','ESS-26249':'Patient messaging & portal','ESS-21452':'Payments, posting & statements','ESS-24649':'Billing rules & exception queue','ESS-22693':'Demographics & insurance setup','ESS-26888':'Tasks & inbox','ESS-26871':'Clinical documentation & templates','ESS-26651':'Devices, login & access',
 'ESS-26744':'Clinical documentation & templates','ESS-26841':'Performance & stability','ESS-25999':'Performance & stability','ESS-24658':'Clinical documentation & templates',
 'ESS-25194':'Integrations & interfaces','ESS-23245':'Pathology & labs','ESS-26470':'Notification emails (unwanted)','ESS-19323':'Patient messaging & portal',
 'ESS-19270':'Online scheduling, self-registration & check-in','ESS-18122':'Reporting & Power BI','ESS-21919':'Billing rules & exception queue','ESS-26487':'Demographics & insurance setup',
 'ESS-26790':'Patient messaging & portal','ESS-26792':'Devices, login & access','ESS-26669':'Online scheduling, self-registration & check-in','ESS-26638':'Patient messaging & portal',
 'ESS-26630':'Patient messaging & portal','ESS-10250':'Patient messaging & portal','ESS-26720':'Patient record corrections & duplicates','ESS-26582':'Patient record corrections & duplicates',
 'ESS-26723':'Payments, posting & statements','ESS-24442':'Clinical documentation & templates','ESS-17365':'Billing rules & exception queue','ESS-17110':'Billing rules & exception queue',
 'ESS-21104':'Pathology & labs','ESS-13177':'Billing rules & exception queue','ESS-13182':'Billing rules & exception queue','ESS-6792':'Payments, posting & statements',
 'ESS-4995':'Clinical documentation & templates','ESS-26439':'Performance & stability','ESS-25136':'Devices, login & access','ESS-26754':'Performance & stability',
 'ESS-12879':'Pathology & labs','ESS-17111':'Clinical documentation & templates','ESS-13070':'Scheduling & appointments','ESS-26616':'Billing rules & exception queue'}
def theme_of(x):
    if x['key'] in KEY_THEME: return KEY_THEME[x['key']]
    s=x['summary'] or ''
    for n,r in THEMES:
        if r.search(s): return n
    d=x['desc'][:450]
    for n,r in THEMES:
        if r.search(d): return n
    return 'Other / unclear'
ENH=R(r'enhanc|feature|suggest|improve|would like|would be (helpful|great|nice)|option to|ability to|can we (get|have|add)|is there (a|any) way|request to (add|route|prevent|expand)|please (consider|add) a|new report|create functionality|add(ing)? (a |new )?(field|tab|option|column)|desperately needed|upgrade rec')
BUG=R(r'\bbug\b|error|not working|unable|cannot|can.t|won.t|issue|glitch|not (saving|printing|loading|populating|syncing|showing|appearing|visible|validating|totaling|posting)|missing|wrong|incorrect|fail|slow|stuck|loop|disappear|lost|kicked out|white screen|problem|trouble|corrupt|duplicat|twice|ghost fax|not pushed|did not')
ADMIN=R(r'new (mohs )?provider|new partner|termed|resignation|provider agreement|unlock|turn (these |this )?(off|on)|please (remove|add|change|update|delete|turn|route|disable|enable|unlock|correct)|change the (dos|note)|ipad enable|enable x|add(ing)? .{0,20}(document type|to document|cpt code|to library|to mips)|document types?\b.*(add|new)|new categories|clean templates|delete (a |the )?(task|template)|deleting task|move dr|removing blocks|provider records|payer id library|update table|location table|webhook needed|web-hook needed|disable|have them routed|mass text|rendering provider switch|chart provider change|provider change|remove (photo|duplicate)|need duplicate|merging|fake patients|defaults for|training spreadsheet')
HOWTO=R(r'^(is there|how do|how can|can you tell|question|inquiry|looking for)|\?\s*$|is ederm able|when our system is supposed|is there (a|any) way to (see|generate|locate|do a search)')
def kind_of(x,th):
    s=(x['summary'] or '')+' '; d=x['desc'][:400]
    if th=='Provider onboarding & offboarding' or th=='Notification emails (unwanted)': return 'Manual admin request'
    if ADMIN.search(s) or (x['type'] in('Setup Request',)) : return 'Manual admin request'
    if x['type']=='Bug' or x['requestType']=='Report An Issue': return 'Bug / defect'
    if x['type']=='Enhancement Request' or x['requestType']=='Suggest An Enhancement':
        if BUG.search(s) and not ENH.search(s+d[:150]): return 'Bug / defect'
        return 'Enhancement request'
    if x['type'] in ('General Question','Training Request'): return 'How-to question'
    if ENH.search(s): return 'Enhancement request'
    if BUG.search(s): return 'Bug / defect'
    if ADMIN.search(d[:250]): return 'Manual admin request'
    if HOWTO.search(s) or HOWTO.search(d[:200]): return 'How-to question'
    if BUG.search(d[:300]): return 'Bug / defect'
    if ENH.search(d[:300]): return 'Enhancement request'
    return 'Manual admin request'
AUTO=[ # (feature name, test fn)
 ('Self-service provider & user lifecycle (onboard / term / credentialing)', lambda x,t,k: t=='Provider onboarding & offboarding'),
 ('User-level notification preferences (opt-out of registration / patient-update emails)', lambda x,t,k: t=='Notification emails (unwanted)'),
 ('Self-service note unlock / amend / DOS & provider change (with audit trail)', lambda x,t,k: k=='Manual admin request' and re.search(r'unlock|change the dos|provider change|provider switch|locked chart|chart provider',x['summary'] or '',re.I)),
 ('Duplicate patient/encounter/charge detection + merge tool', lambda x,t,k: t=='Patient record corrections & duplicates' or re.search(r'duplicat|dupilcate|merg|twice',x['summary'] or '',re.I)),
 ('Practice-configurable lists (document types, cancel reasons, library codes)', lambda x,t,k: re.search(r'document type|document drop|add(ing)? to document|documents for|new categories|cancel reason|add cancel|to library|adding cpt|add to document|document list|scan(ning)? tab|scan option|drop downs for scanning',(x['summary'] or '')+' '+x['desc'][:200],re.I)),
 ('Practice-configurable billing rules builder (EQ holds, rules engine)', lambda x,t,k: t=='Billing rules & exception queue' and re.search(r'hold|rules engine|exception|route|mod ?59|j-?code',x['summary'] or '',re.I) and k!='Bug / defect'),
 ('Self-service report builder & scheduled exports', lambda x,t,k: t=='Reporting & Power BI' and k!='Bug / defect'),
 ('Device enrollment & account self-service (iPad enable, MFA, lockouts)', lambda x,t,k: re.search(r'ipad enable|enable x|account access|locked out|mfa|authy|super user|permission|ipad account|overseas|security code|staff to ipad',x['summary'] or '',re.I)),
 ('Configurable online-scheduler rules (age, insurance, provider eligibility)', lambda x,t,k: t=='Online scheduling, self-registration & check-in' and k!='Bug / defect'),
 ('Bulk patient messaging / broadcast (closures, recalls)', lambda x,t,k: re.search(r'mass text|patient outreach|recall',(x['summary'] or ''),re.I)),
 ('Fax routing & webhook self-configuration', lambda x,t,k: re.search(r'webhook|web-hook|fax porting|efax.*(filter|log|date range)|faxing (log|suggestion)',(x['summary'] or ''),re.I)),
]
out=[]
for x in L:
    th=theme_of(x); noise=None
    if x['key'] in NOISE_KEYS: noise=NOISE_KEYS[x['key']]
    else:
        for n,r in NOISE:
            if r.search(x['summary'] or ''): noise=n
    k='Noise / no action' if noise else kind_of(x,th)
    if noise and th not in ('Infrastructure / server alerts',): pass
    au=None
    if not noise:
        for n,f in AUTO:
            if f(x,th,k): au=n;break
    x2=dict(x); x2.update(theme=th,kind=k,noise=noise,automation=au)
    out.append(x2)
json.dump(out,open('/tmp/w/classified.json','w'))
print(C.Counter(o['theme'] for o in out).most_common())
print(C.Counter(o['kind'] for o in out).most_common())
print(C.Counter(o['automation'] for o in out).most_common())
print('OTHER:');[print(' ',o['key'],o['summary'][:60],'|',o['desc'][:120]) for o in out if o['theme']=='Other / unclear']
