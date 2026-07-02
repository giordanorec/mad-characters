#!/usr/bin/env python3
"""
Empacota os 10.000 personagens em grades 4x4 (16 por grade), agrupadas por SHEET
(estética uniforme por grade). 100/16 = 7 grades por sheet (a última com 4).
Prompt SEM nomes/legenda e com fundo chromakey verde forte (asset recortável).

Saída:
  grids/<NNN>_<sheet_id>_p<k>.txt   (numerado 001..)
  grids/INDEX.json
"""
import json
from pathlib import Path

BASE = Path("/home/grec/Projetos/mad-characters")
D = BASE / "data"; G = BASE / "grids"
# limpa grades antigas (eram 5x5)
if G.exists():
    for f in G.glob("*.txt"): f.unlink()
G.mkdir(exist_ok=True)

sheets = {s["id"]: s for s in json.load(open(D / "sheets.json"))}
PER = 16; COLS = 4; ROWS = 4

def grid_prompt(sh, block):
    head = [
        f"Generate ONE single image: a {COLS}x{ROWS} grid of {len(block)} distinct "
        f"characters, evenly spaced, each isolated in its own cell, all in a "
        f"consistent \"{sh['aesthetic']}\" art style (theme: {sh['analogy']}).",
        f"Solid uniform chroma-key green background (#00b140) behind every character, "
        f"filling the entire image. ABSOLUTELY NO text, no words, no captions, no "
        f"labels, no names, no letters or numbers anywhere in the image — characters "
        f"only. {COLS} columns by {ROWS} rows, consistent scale and framing, centered "
        f"characters, high detail.",
        "The characters, left-to-right then top-to-bottom (do NOT write these names, "
        "they are only to guide you):",
    ]
    for i, c in enumerate(block, 1):
        head.append(f"{i}) {c['character_desc']}")
    return "\n".join(head)

index = []; n = 0
for sid in sorted(sheets):
    f = D / "characters" / f"{sid}.json"
    if not f.is_file(): continue
    recs = json.load(open(f)); sh = sheets[sid]
    for k in range(0, len(recs), PER):
        block = recs[k:k+PER]
        n += 1
        part = k // PER + 1
        fname = f"{n:03d}_{sid}_p{part}.txt"
        (G / fname).write_text(grid_prompt(sh, block) + "\n", "utf-8")
        index.append({"grid": n, "file": fname, "sheet_id": sid,
                      "analogy": sh["analogy"], "aesthetic": sh["aesthetic"],
                      "family": sh["family"], "n_chars": len(block),
                      "char_ids": [c["char_id"] for c in block]})

(G / "INDEX.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), "utf-8")
print(f"grades: {n} (16 por grade, 4x4) | personagens: {sum(x['n_chars'] for x in index)}")
