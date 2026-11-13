#!/usr/bin/env python3
"""
Checks every citation of an app against the registries, independently of whoever wrote it.

For each repo given:
- CITATION.cff: every `references` entry with a DOI is fetched from Crossref (or DataCite for
  DataCite DOIs: Zenodo, DANDI, figshare, arXiv) and compared: title, the full author list in
  order (family names, and given-name initials), year, and journal when the entry has one.
  Entity authors (`name:`) are compared against consortium names. A PMID is looked up in PubMed
  and must point to the same DOI. Entries without a DOI are listed for manual review; their URL
  must resolve.
- README.md: every DOI must resolve and appear in CITATION.cff; every PMID must map to a DOI that
  appears on the same line.

Exit 1 when anything is wrong. Results are cached in $TMPDIR so reruns are fast.

Usage: scripts/verify-citations.py ../spike-sort ../ephys-prep ...
Needs: pyyaml (python3 -m pip install pyyaml).
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

UA = "pennsieve-citation-check/1.0 (mailto:support@pennsieve.io)"
CACHE = Path(os.environ.get("TMPDIR", "/tmp")) / "citation-cache"
CACHE.mkdir(parents=True, exist_ok=True)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>\]]+)", re.I)


def clean_doi(doi: str) -> str:
    """Trim what follows a DOI in prose: trailing punctuation, and a ')' that closes a parenthesis
    opened before the DOI (DOIs may contain balanced parentheses: 10.1016/0006-8993(71)90358-1)."""
    while doi and (doi[-1] in ".,;:*_" or (doi[-1] == ")" and doi.count(")") > doi.count("("))):
        doi = doi[:-1]
    return doi
PMID_RE = re.compile(r"PMID[:\s]*?(\d{6,9})", re.I)


def get(url: str) -> tuple[int, bytes]:
    key = CACHE / hashlib.sha256(url.encode()).hexdigest()
    if key.exists():
        status, body = key.read_bytes().split(b"\n", 1)
        return int(status), body
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                status, body = r.status, r.read()
            break
        except urllib.error.HTTPError as e:
            status, body = e.code, b""
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError):
            status, body = 0, b""
        time.sleep(2 ** attempt)
    if status in (200, 404):
        key.write_bytes(f"{status}\n".encode() + body)
    return status, body


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"<[^>]+>", "", s)  # Crossref titles may carry <i>, <sub>
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def registry(doi: str) -> dict | None:
    """Normalised record: title, authors [(family, given) or (None, name)], year, journal."""
    q = urllib.parse.quote(doi, safe="/")
    status, body = get(f"https://api.crossref.org/works/{q}")
    if status == 200:
        m = json.loads(body)["message"]
        authors = []
        for a in m.get("author", []):
            authors.append((a.get("family"), a.get("given", "")) if a.get("family") else (None, a.get("name", "")))
        parts = (m.get("issued") or m.get("published") or {}).get("date-parts", [[None]])[0]
        return {"source": "crossref", "title": (m.get("title") or [""])[0], "authors": authors,
                "year": parts[0], "journal": (m.get("container-title") or [""])[0]}
    status, body = get(f"https://api.datacite.org/dois/{q}")
    if status == 200:
        a = json.loads(body)["data"]["attributes"]
        authors = []
        for c in a.get("creators", []):
            if c.get("familyName"):
                authors.append((c["familyName"], c.get("givenName", "")))
            else:
                authors.append((None, c.get("name", "")))
        return {"source": "datacite", "title": (a.get("titles") or [{}])[0].get("title", ""),
                "authors": authors, "year": a.get("publicationYear"), "journal": a.get("publisher", "")}
    return None


def pubmed_doi(pmid: str) -> tuple[str | None, str]:
    status, body = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json")
    if status != 200:
        return None, ""
    rec = json.loads(body).get("result", {}).get(pmid, {})
    doi = next((i["value"] for i in rec.get("articleids", []) if i.get("idtype") == "doi"), None)
    return doi, rec.get("title", "")


def pubmed_authors(doi: str) -> list[tuple[str, str]] | None:
    """Author list from PubMed, as (family, initials): a second source when a registry record is incomplete."""
    q = urllib.parse.quote(f"{doi}[doi]")
    status, body = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={q}&retmode=json")
    ids = json.loads(body).get("esearchresult", {}).get("idlist", []) if status == 200 else []
    if len(ids) != 1:
        return None
    status, body = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids[0]}&retmode=json")
    rec = json.loads(body).get("result", {}).get(ids[0], {}) if status == 200 else {}
    out = []
    for a in rec.get("authors", []):
        if a.get("authtype") == "Author":
            fam, _, ini = a["name"].rpartition(" ")
            out.append((fam or ini, ini if fam else ""))
    return out or None


def initials(given: str) -> str:
    return "".join(w[0] for w in re.split(r"[\s.\-]+", norm(given)) if w)


def check_reference(ref: dict) -> list[str]:
    errs: list[str] = []
    title = ref.get("title", "")
    doi = ref.get("doi") or next((i.get("value") for i in ref.get("identifiers", []) if i.get("type") == "doi"), None)
    if not doi:
        url = ref.get("url") or ref.get("repository-code")
        if not url:
            return [f"no DOI and no URL: {title!r} (manual review)"]
        status, _ = get(url)
        return [] if status == 200 else [f"URL does not resolve ({status}): {url}"]
    rec = registry(doi)
    if rec is None:
        return [f"DOI not found on Crossref or DataCite: {doi}"]
    ratio = difflib.SequenceMatcher(None, norm(title), norm(rec["title"])).ratio()
    if ratio < 0.9:
        errs.append(f"title mismatch ({ratio:.2f}): cff {title!r} vs {rec['source']} {rec['title']!r}")
    mine = ref.get("authors", [])
    theirs = rec["authors"]
    if theirs and len(mine) != len(theirs):
        # Some publishers deposit incomplete author lists (Frontiers 2013: one of eleven); PubMed may have them all.
        pm = pubmed_authors(doi)
        if pm and len(pm) == len(mine):
            theirs = pm
            rec = {**rec, "source": "pubmed"}
    if theirs:
        if len(mine) != len(theirs):
            errs.append(f"{len(mine)} authors in cff vs {len(theirs)} on {rec['source']}")
        for i, (a, (fam, giv)) in enumerate(zip(mine, theirs)):
            if fam is None:  # consortium / organisation
                got = a.get("name") or f"{a.get('given-names', '')} {a.get('family-names', '')}"
                if norm(got) != norm(giv) and difflib.SequenceMatcher(None, norm(got), norm(giv)).ratio() < 0.85:
                    errs.append(f"author {i + 1}: cff {got!r} vs {giv!r}")
                continue
            f2 = a.get("family-names", "") or a.get("name", "")
            if a.get("name") and not giv:  # a consortium Crossref stores as a family name
                if difflib.SequenceMatcher(None, norm(f2), norm(fam)).ratio() < 0.85:
                    errs.append(f"author {i + 1}: cff {f2!r} vs {fam!r}")
                continue
            if norm(f2) != norm(fam):
                errs.append(f"author {i + 1}: family {f2!r} vs {fam!r}")
            elif giv and a.get("given-names") and initials(a["given-names"])[:1] != initials(giv)[:1]:
                errs.append(f"author {i + 1} ({fam}): given {a['given-names']!r} vs {giv!r}")
    if ref.get("year") and rec["year"] and int(ref["year"]) != int(rec["year"]):
        # Online-first vs issue year differ by one for many journals; flag only bigger gaps.
        if abs(int(ref["year"]) - int(rec["year"])) > 1:
            errs.append(f"year {ref['year']} vs {rec['year']}")
    journal = (ref.get("journal") or "")
    if journal and rec["journal"] and difflib.SequenceMatcher(None, norm(journal), norm(rec["journal"])).ratio() < 0.6:
        errs.append(f"journal {journal!r} vs {rec['journal']!r}")
    pmid = ref.get("pmid") or next((i.get("value") for i in ref.get("identifiers", []) if i.get("type") == "other" and str(i.get("value", "")).isdigit()), None)
    if pmid:
        pdoi, _ = pubmed_doi(str(pmid))
        if not pdoi or pdoi.lower() != doi.lower():
            errs.append(f"PMID {pmid} maps to DOI {pdoi}, not {doi}")
    return errs


def check_repo(repo: Path) -> int:
    problems = 0
    cff_path = repo / "CITATION.cff"
    if not cff_path.exists():
        print(f"{repo.name}: no CITATION.cff")
        return 1
    cff = yaml.safe_load(cff_path.read_text())
    refs = cff.get("references", [])
    cff_dois = set()
    print(f"== {repo.name}: {len(refs)} references")
    for ref in refs:
        doi = ref.get("doi") or next((i.get("value") for i in ref.get("identifiers", []) if i.get("type") == "doi"), None)
        if doi:
            cff_dois.add(doi.lower())
        errs = check_reference(ref)
        label = f"{(ref.get('authors') or [{}])[0].get('family-names') or (ref.get('authors') or [{}])[0].get('name', '?')} {ref.get('year', '')}: {ref.get('title', '')[:60]}"
        if errs:
            problems += 1
            print(f"  FAIL {label}")
            for e in errs:
                print(f"       - {e}")
        else:
            print(f"  ok   {label}")
    readme = repo / "README.md"
    if readme.exists():
        lines = readme.read_text().splitlines()
        for n, line in enumerate(lines, 1):
            near = " ".join(lines[max(0, n - 4):n + 2])  # citations wrap: the DOI may be a line or two away
            for doi in DOI_RE.findall(line):
                doi = clean_doi(doi)
                if registry(doi) is None:
                    problems += 1
                    print(f"  FAIL README:{n}: DOI does not resolve: {doi}")
                elif doi.lower() not in cff_dois:
                    problems += 1
                    print(f"  FAIL README:{n}: DOI {doi} is cited in the README but not in CITATION.cff")
            for pmid in PMID_RE.findall(line):
                pdoi, _ = pubmed_doi(pmid)
                if not pdoi or pdoi.lower() not in near.lower():
                    problems += 1
                    print(f"  FAIL README:{n}: PMID {pmid} maps to DOI {pdoi}, which is not next to it")
    return problems


def main() -> None:
    repos = [Path(p).resolve() for p in sys.argv[1:]]
    if not repos:
        sys.exit(__doc__)
    total = sum(check_repo(r) for r in repos)
    print(f"\n{total} problem(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
