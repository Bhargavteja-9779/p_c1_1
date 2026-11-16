"""Verification of prior-art references found by the prior-art sweep (arXiv / Crossref / DataCite)."""
import json, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
ARX = ["2606.20115", "2608.15500", "2605.05562", "2205.09940", "2205.12940", "2410.02561", "2310.02863",
       "2505.13432", "2510.15780", "2606.00717"]
DOIS = ["10.3390/app16167984", "10.1093/jssam/smae010", "10.1016/j.egyai.2026.100815",
        "10.1080/10920277.2022.2123364", "10.1016/j.enbuild.2022.111846"]
DATACITE = ["10.5281/zenodo.24002627"]
out = []
x = ET.fromstring(urllib.request.urlopen("http://export.arxiv.org/api/query?id_list=" + ",".join(ARX) + "&max_results=50", timeout=60).read())
ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
for e in x.findall("a:entry", ns):
    aid = e.find("a:id", ns).text.split("/abs/")[-1]
    out.append(dict(key=re.sub(r"v\d+$", "", aid), source="arxiv", ok=True, title=" ".join(e.find("a:title", ns).text.split()),
                    authors=[a.find("a:name", ns).text for a in e.findall("a:author", ns)],
                    published=e.find("a:published", ns).text[:10],
                    journal_ref=(e.find("ar:journal_ref", ns).text if e.find("ar:journal_ref", ns) is not None else None),
                    comment=(e.find("ar:comment", ns).text if e.find("ar:comment", ns) is not None else None)))
for d in DOIS:
    try:
        r = json.load(urllib.request.urlopen("https://api.crossref.org/works/" + urllib.parse.quote(d), timeout=60))["message"]
        out.append(dict(key=d, source="crossref", ok=True, title=(r.get("title") or [""])[0],
                        authors=[(a.get("family", "") + ", " + a.get("given", "")).strip(", ") for a in r.get("author", [])],
                        year=(r.get("issued", {}).get("date-parts") or [[None]])[0][0],
                        venue=(r.get("container-title") or [""])[0], volume=r.get("volume"), issue=r.get("issue"),
                        pages=r.get("page") or r.get("article-number")))
    except Exception as ex:
        out.append(dict(key=d, source="crossref", ok=False, error=str(ex)))
    time.sleep(0.3)
for d in DATACITE:
    try:
        r = json.load(urllib.request.urlopen("https://api.datacite.org/dois/" + d, timeout=60))["data"]["attributes"]
        out.append(dict(key=d, source="datacite", ok=True, title=r["titles"][0]["title"],
                        authors=[c.get("name") for c in r["creators"]], year=r.get("publicationYear"),
                        publisher=r.get("publisher"), type=r.get("types", {}).get("resourceTypeGeneral"),
                        published=r.get("published"), version=r.get("version")))
    except Exception as ex:
        out.append(dict(key=d, source="datacite", ok=False, error=str(ex)))
json.dump(out, open("references_verified_new.json", "w"), indent=1)
for o in out:
    print(o["key"], "|", o.get("ok"), "|", o.get("published") or o.get("year"), "|", "; ".join((o.get("authors") or [])[:4])[:70], "|", (o.get("title") or o.get("error", ""))[:90], "|", (o.get("venue") or o.get("journal_ref") or o.get("publisher") or o.get("comment") or "")[:60])
# Additional checks done interactively (2026-11-16): Crossref 10.1109/isap.2015.7325539 (Almeida & Gama, ISAP 2015)
# and 10.1016/j.epsr.2026.113412 (Shi, Shen & Lyu, EPSR 261:113412; abstract not accessible -> cited only for
# what its title states). NeurIPS 2022 proceedings page confirms Lin, Trivedi & Sun (TQA).
