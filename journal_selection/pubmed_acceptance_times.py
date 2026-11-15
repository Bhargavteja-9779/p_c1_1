import sys, json, time, urllib.request, urllib.parse, statistics, xml.etree.ElementTree as ET
E="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
def get(u):
    for i in range(5):
        try: return urllib.request.urlopen(u,timeout=60).read()
        except Exception as e: time.sleep(2+i*2)
    raise
def run(jname, n=400):
    q=f'"{jname}"[jour] AND ("2025/01/01"[dp] : "2026/10/31"[dp]) AND journal article[pt]'
    r=json.loads(get(E+"esearch.fcgi?"+urllib.parse.urlencode(dict(db="pubmed",term=q,retmax=n,retmode="json",sort="pub_date"))))
    ids=r["esearchresult"]["idlist"]; total=r["esearchresult"]["count"]
    d=[];
    for i in range(0,len(ids),200):
        x=ET.fromstring(get(E+"efetch.fcgi?"+urllib.parse.urlencode(dict(db="pubmed",id=",".join(ids[i:i+200]),retmode="xml"))))
        for a in x.findall(".//PubmedArticle"):
            h={}
            for p in a.findall(".//History/PubMedPubDate"):
                try:
                    import datetime
                    h[p.get("PubStatus")]=datetime.date(int(p.findtext("Year")),int(p.findtext("Month")),int(p.findtext("Day")))
                except: pass
            if "received" in h and "accepted" in h:
                dd=(h["accepted"]-h["received"]).days
                if dd>0: d.append(dd)
        time.sleep(0.4)
    if not d: return jname,total,0,None,None,None
    d.sort(); q=lambda p:d[int(p*(len(d)-1))]
    return jname,total,len(d),statistics.median(d),q(.25),q(.75)
for j in sys.argv[1:]:
    print(*run(j),sep="\t",flush=True)
