"""Citation audit: verify every reference against Crossref (DOI) or arXiv (id). Output: references_verified.json"""
import json, time, urllib.request, urllib.parse, re, xml.etree.ElementTree as ET
DOIS = """10.1038/s41597-020-00712-x
10.24432/C58C86
10.1007/b106715
10.1080/01621459.2017.1307116
10.1214/23-AOS2276
10.1080/01621459.2022.2060112
10.1198/016214506000001437
10.1016/j.ijforecast.2015.11.011
10.1016/j.ijforecast.2016.02.001
10.1016/j.adapen.2022.100084
10.1016/j.adapen.2020.100004
10.1016/j.adapen.2023.100142
10.1016/j.adapen.2024.100165
10.1016/j.adapen.2021.100025
10.1016/j.adapen.2023.100123
10.1016/j.adapen.2021.100054
10.1016/j.adapen.2024.100172
10.1016/j.adapen.2022.100120
10.1016/j.enbuild.2018.01.034
10.1016/j.apenergy.2020.114499
10.1080/23744731.2020.1795514
10.1561/2200000101
10.1016/j.apenergy.2018.10.078
10.1016/j.ijforecast.2019.07.001
10.2307/1913643
10.1007/3-540-36755-1_29
10.1080/01621459.1972.10481224
10.1214/aos/1176342360
10.2307/3001968
10.2466/11.IT.3.1
10.1016/j.knosys.2025.114222
10.1016/j.rser.2017.04.095
10.1093/jrsssb/qkaf008""".split()
ARX = ["1905.03222", "2106.00170", "1904.06019", "2306.06342", "2306.09335", "2102.08898", "2307.00142",
       "2202.07282", "2010.09107", "2508.01418", "1912.01703", "2305.12616"]
out = []
for d in DOIS:
    try:
        r = json.load(urllib.request.urlopen("https://api.crossref.org/works/" + urllib.parse.quote(d), timeout=60))["message"]
        out.append(dict(key=d, source="crossref", ok=True, doi=d, title=(r.get("title") or [""])[0],
                        authors=[(a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in r.get("author", [])],
                        year=(r.get("issued", {}).get("date-parts") or [[None]])[0][0],
                        venue=(r.get("container-title") or [r.get("publisher", "")])[0] if r.get("container-title") else r.get("publisher", ""),
                        volume=r.get("volume"), issue=r.get("issue"), pages=r.get("page") or r.get("article-number"), type=r.get("type")))
    except Exception as e:
        out.append(dict(key=d, source="crossref", ok=False, error=str(e)))
    time.sleep(0.3)
ids = ",".join(ARX)
x = ET.fromstring(urllib.request.urlopen("http://export.arxiv.org/api/query?id_list=" + ids + "&max_results=50", timeout=60).read())
ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
for e in x.findall("a:entry", ns):
    aid = e.find("a:id", ns).text.split("/abs/")[-1]
    out.append(dict(key=re.sub(r"v\d+$", "", aid), source="arxiv", ok=True, title=" ".join(e.find("a:title", ns).text.split()),
                    authors=[a.find("a:name", ns).text for a in e.findall("a:author", ns)],
                    year=int(e.find("a:published", ns).text[:4]),
                    journal_ref=(e.find("ar:journal_ref", ns).text if e.find("ar:journal_ref", ns) is not None else None),
                    doi=(e.find("ar:doi", ns).text if e.find("ar:doi", ns) is not None else None)))
json.dump(out, open("references_verified.json", "w"), indent=1)
for o in out:
    print(o["key"], "|", o.get("ok"), "|", o.get("year"), "|", (o.get("authors") or [""])[0][:25], "|", (o.get("title") or o.get("error", ""))[:85], "|", (o.get("venue") or o.get("journal_ref") or "")[:40])
