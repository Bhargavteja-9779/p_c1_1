import json,urllib.request,re,sys,urllib.parse
issn=sys.argv[1]; out=[];cur='*'
while True:
    u=f"https://api.crossref.org/journals/{issn}/works?rows=1000&cursor={urllib.parse.quote(cur)}&select=DOI,title,issued,is-referenced-by-count,type"
    d=json.load(urllib.request.urlopen(u,timeout=120))['message']
    out+=d['items']
    if not d['items'] or 'next-cursor' not in d or len(out)>=d['total-results']: break
    cur=d['next-cursor']
json.dump(out,open(f'cr_{issn}.json','w')); print(issn,len(out))
