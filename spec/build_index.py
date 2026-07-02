#!/usr/bin/env python3
"""
Une os 100 arquivos de sheet em um índice MESTRE navegável pelos 3 eixos
(role, analogia, estética) — o dado que o site vai consumir depois.
Emite:
  data/characters.json        (10.000 registros enriquecidos)
  data/index_by_role.json     ({role_id: [char_id,...]})
  data/index_by_analogy.json  ({sheet_id: {analogy, aesthetic, family, chars:[...]}})
  data/index_by_aesthetic.json({aesthetic: [sheet_id,...]})
"""
import json
from collections import defaultdict
from pathlib import Path

BASE = Path("/home/grec/Projetos/mad-characters")
D = BASE / "data"

sheets = {s["id"]: s for s in json.load(open(D / "sheets.json"))}
roles = {r["id"]: r for r in json.load(open(D / "roles.json"))}

chars = []
missing = []
for sid in sheets:
    f = D / "characters" / f"{sid}.json"
    if not f.is_file():
        missing.append(sid); continue
    recs = json.load(open(f))
    sh = sheets[sid]
    for rec in recs:
        ro = roles.get(rec["role_id"], {})
        rec2 = dict(rec)
        rec2.update({
            "sheet_analogy": sh["analogy"], "sheet_aesthetic": sh["aesthetic"],
            "sheet_family": sh["family"], "role_category": ro.get("category"),
            "real_mad_role": ro.get("real_mad_role", False),
        })
        chars.append(rec2)

(D / "characters.json").write_text(json.dumps(chars, ensure_ascii=False), "utf-8")

by_role = defaultdict(list)
by_aesthetic = defaultdict(list)
for c in chars:
    by_role[c["role_id"]].append(c["char_id"])
by_analogy = {}
for sid, sh in sheets.items():
    by_analogy[sid] = {"analogy": sh["analogy"], "aesthetic": sh["aesthetic"],
                       "family": sh["family"],
                       "chars": [c["char_id"] for c in chars if c["sheet_id"] == sid]}
    by_aesthetic[sh["aesthetic"]].append(sid)

(D / "index_by_role.json").write_text(json.dumps(by_role, ensure_ascii=False, indent=1), "utf-8")
(D / "index_by_analogy.json").write_text(json.dumps(by_analogy, ensure_ascii=False, indent=1), "utf-8")
(D / "index_by_aesthetic.json").write_text(json.dumps(by_aesthetic, ensure_ascii=False, indent=1), "utf-8")

print(f"personagens: {len(chars)}/10000 | sheets faltando: {missing or 'nenhum'}")
print(f"índices: por role ({len(by_role)}), por analogia ({len(by_analogy)}), por estética ({len(by_aesthetic)})")
