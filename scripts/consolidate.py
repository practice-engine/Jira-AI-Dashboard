import json,glob,os,re
d='/sessions/adoring-awesome-davinci/mnt/.claude/projects/session/42d9afa6-9b26-46c9-bc9f-dbe226102b2b/tool-results/'
files=sorted(glob.glob(d+'*searchJira*'),key=os.path.getmtime)[1:]  # skip first compact page
out={}
def txt(x):
    if x is None: return ''
    if isinstance(x,str): return x
    return json.dumps(x)
def clean(s):
    s=re.sub(r'!\[\]\([^)]*\)','',s); s=re.sub(r'\(blob:[^)]*\)','',s)
    s=re.sub(r'https?://\S+','[url]',s); s=re.sub(r'\s+',' ',s)
    return s.strip()
for f in files:
    for n in json.load(open(f))['issues']['nodes']:
        F=n['fields']; cf=F.get('customFields') or {}
        rt=(cf.get('Request Type') or {}).get('value') or {}
        rtn=rt.get('requestType',{}).get('name') if isinstance(rt,dict) else None
        org=(cf.get('Organizations') or {}).get('value') or []
        com=F.get('comment') or {}
        comments=com.get('comments',[]) if isinstance(com,dict) else []
        rep=F.get('reporter') or {}
        out[n['key']]=dict(key=n['key'],summary=F.get('summary'),status=F['status']['name'],
          priority=(F.get('priority') or {}).get('name'),type=F['issuetype']['name'],requestType=rtn,
          created=F['created'][:10],updated=F['updated'][:10],
          reporter=rep.get('displayName'),reporterEmail=rep.get('emailAddress'),reporterType=rep.get('accountType'),
          assignee=(F.get('assignee') or {}).get('displayName'),
          org=[o.get('name') for o in org if isinstance(o,dict)],labels=F.get('labels'),
          links=[(l.get('outwardIssue') or l.get('inwardIssue') or {}).get('key') for l in F.get('issuelinks',[])],
          ncomments=len(comments),
          desc=clean(txt(F.get('description')))[:700],
          lastComment=clean(txt(comments[-1].get('body')))[:300] if comments else '')
json.dump(list(out.values()),open('/tmp/w/tickets.json','w'))
print(len(out))
import collections as C
L=list(out.values())
for k in ['status','priority','type','requestType','reporterType']:
    print(k,C.Counter(x[k] for x in L).most_common(15))
print('orgs',C.Counter(o for x in L for o in x['org']).most_common(15))
print('reporters',C.Counter(x['reporterEmail'] for x in L).most_common(25))
print('dates',min(x['created'] for x in L),max(x['created'] for x in L))
