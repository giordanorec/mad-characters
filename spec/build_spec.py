#!/usr/bin/env python3
"""
Fonte da verdade da spec de personagens do mad.
Define os 100 SHEETS (analogia × estética) e os 100 ROLES, e emite:
  - data/sheets.json      (navegável por analogia e por estética)
  - data/roles.json       (navegável por role e categoria)
  - data/manifest.json    (parâmetros do pipeline + grade)
  - SHEETS.md / ROLES.md  (versões legíveis)
10.000 personagens = 100 sheets × 100 roles. Cada personagem terá id
determinístico  s{NN}-r{NN}  para indexação/navegação no site depois.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
DATA.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 100 SHEETS — (familia, slug, analogia, estetica, vibe)
# Inclui cultura de internet/meme/pop (Funko, South Park, Simpsons, Wojak,
# Muppet, bobblehead) sem passar de 100 combinações.
# ---------------------------------------------------------------------------
SHEETS = [
 # A. Reino Animal
 ("Animal","floresta-plush","Animais da floresta","Pelúcia (plush)","fofo de bicho de pelúcia"),
 ("Animal","caes-foto","Raças de cachorro","Foto realista","retrato de estúdio"),
 ("Animal","gatos-amigurumi","Raças de gato","Amigurumi (crochê)","lãzinha"),
 ("Animal","aves-aquarela","Aves exóticas","Aquarela","leve e translúcido"),
 ("Animal","marinho-lowpoly","Criaturas do fundo do mar","Low-poly 3D","facetado"),
 ("Animal","insetos-entomologia","Insetos","Prancha entomológica vintage","museu"),
 ("Animal","dinos-chibi","Dinossauros","Chibi cartoon","cabeçudo e fofo"),
 ("Animal","miticos-vitral","Animais míticos (dragão, grifo)","Vitral gótico","chumbo e cor"),
 ("Animal","repteis-pixel","Répteis e anfíbios","Pixel art 8-bit","arcade"),
 ("Animal","borboletas-papercraft","Borboletas e mariposas","Papercraft","camadas de papel"),
 # B. Heróis & Fantasia
 ("Heróis","herois-comics","Super-heróis","Quadrinhos (halftone)","action comic"),
 ("Heróis","viloes-popart","Vilões carismáticos","Pop art (Warhol)","serigrafia"),
 ("Heróis","rpg-pixel16","Classes de RPG (mago, guerreiro)","Pixel art 16-bit","SNES"),
 ("Heróis","fantasia-oleo","Raças de fantasia (elfo, anão, orc)","Óleo renascentista","retrato clássico"),
 ("Heróis","cavaleiros-vitral","Cavaleiros medievais","Vitral","catedral"),
 ("Heróis","magos-nouveau","Magos e bruxas","Art nouveau","Mucha"),
 ("Heróis","piratas-xilo","Piratas","Xilogravura antiga","gravura em madeira"),
 ("Heróis","ninjas-ukiyoe","Ninjas e samurais","Ukiyo-e","woodblock japonês"),
 ("Heróis","robos-tintoy","Robôs retrô","Tin toy (lata vintage)","brinquedo de lata"),
 ("Heróis","mechas-anime","Mechas gigantes","Anime mecha","painel de anime"),
 # C. Divindades & Mito
 ("Mito","olimpo-marmore","Deuses do Olimpo","Escultura de mármore","estátua branca"),
 ("Mito","nordicos-madeira","Deuses nórdicos","Madeira entalhada","runas"),
 ("Mito","egipcios-mural","Deuses egípcios","Arte mural/hieróglifo","perfil dourado"),
 ("Mito","hindus-devocional","Deuses hindus","Arte devocional","cores saturadas"),
 ("Mito","yokai-sumie","Yokai japoneses","Sumi-e (tinta)","pincel monocromático"),
 ("Mito","santos-bizantino","Santos e ícones","Ícone bizantino dourado","folha de ouro"),
 ("Mito","anjos-barroco","Anjos e demônios","Barroco claro-escuro","Caravaggio"),
 ("Mito","espiritos-aquarela","Espíritos da natureza","Aquarela etérea","fantasmagórico"),
 ("Mito","bobblehead-caricatura","Arquétipos (caricatura)","Bobblehead cabeçudo","boneco de painel"),
 ("Mito","zodiaco-neon","Signos do zodíaco","Constelação neon","linhas de estrela"),
 # D. Gente & Profissões
 ("Gente","profissoes-foto","Profissões clássicas","Foto de estúdio realista","crachá corporativo"),
 ("Gente","personas-flat","Personas de usuário","Flat design (icon)","vetor limpo"),
 ("Gente","chefs-gouache","Chefs e cozinheiros","Gouache de receita","guache quente"),
 ("Gente","cientistas-riso","Cientistas (estilizados)","Risograph","duas tintas"),
 ("Gente","musicos-vinil","Músicos por gênero","Capa de disco vinil","art direction retrô"),
 ("Gente","atletas-cartaz","Atletas por esporte","Cartaz esportivo vintage","litografia"),
 ("Gente","artistas-impressionista","Artistas (pintor, escultor)","Autorretrato impressionista","pincelada"),
 ("Gente","exploradores-diario","Exploradores/aventureiros","Diário de expedição","ilustração de viagem"),
 ("Gente","detetives-noir","Detetives e espiões","Film noir","p&b dramático"),
 ("Gente","circo-cartaz","Circo (malabarista, mágico)","Cartaz de circo vintage","tipografia festiva"),
 # E. Objetos & Utensílios
 ("Objetos","cozinha-produto","Utensílios de cozinha","Foto de produto minimalista","fundo neutro"),
 ("Objetos","ferramentas-blueprint","Ferramentas","Blueprint técnico","linhas em azul"),
 ("Objetos","escritorio-iso","Material de escritório","3D isométrico","render limpo"),
 ("Objetos","eletro-kawaii","Eletrodomésticos com rosto","Cartoon kawaii","carinha fofa"),
 ("Objetos","gadgets-render","Gadgets e câmeras","Render de produto premium","vidro e metal"),
 ("Objetos","instrumentos-lineart","Instrumentos musicais","Line art dourado","contorno fino"),
 ("Objetos","moveis-bauhaus","Móveis icônicos do design","Bauhaus geométrico","primárias"),
 ("Objetos","loucas-azulejo","Louças e cerâmicas","Azulejo/mosaico português","cobalto"),
 ("Objetos","funko-pop","Colecionáveis","Funko Pop style","vinil cabeçudo"),
 ("Objetos","coqueteis-deco","Bebidas e coquetéis","Menu art deco","dourado 1920s"),
 # F. Marcas & Cultura
 ("Marcas","logos-flat","Logomarcas famosas (paródia)","Flat vector","marca minimal"),
 ("Marcas","empresas-mascote90","Empresas como mascotes","Mascote corporativo anos 90","retrô ad"),
 ("Marcas","emojis-3d","Emojis 3D","Estilo Apple/Fluent 3D","gomoso brilhante"),
 ("Marcas","stickers-diecut","Adesivos die-cut","Sticker brilhante","contorno branco"),
 ("Marcas","pins-esmalte","Enamel pins","Pin de esmalte metálico","borda dourada"),
 ("Marcas","baralho-naipe","Cartas de baralho","Naipe ornamentado","figura de baralho"),
 ("Marcas","taro-riderwaite","Tarô","Arte Rider-Waite","carta mística"),
 ("Marcas","xadrez-marmore","Xadrez (peças)","Mármore preto e branco","escultura de jogo"),
 ("Marcas","southpark-recorte","Países/tribos","South Park (recorte de papel)","cutout construtivo"),
 ("Marcas","simpsons-groening","Personagens amarelos","Estilo Simpsons (Groening)","amarelo cartunesco"),
 # G. Natureza & Ciência
 ("Natureza","plantas-botanica","Plantas e flores","Botânica científica","prancha"),
 ("Natureza","arvores-woodcut","Árvores","Woodcut","traço grosso"),
 ("Natureza","cogumelos-aquarela","Cogumelos","Aquarela micológica","delicado"),
 ("Natureza","frutas-foto","Frutas e vegetais","Foto de produto vibrante","fresco"),
 ("Natureza","micro-cartoon","Micróbios/bactérias fofos","Cartoon científico","fofo educativo"),
 ("Natureza","cristais-iri","Cristais e gemas","Render 3D iridescente","facetas de luz"),
 ("Natureza","astros-scifi50","Planetas e astros","Sci-fi anos 50","pulp espacial"),
 ("Natureza","clima-simpsons","Fenômenos do tempo","Flat design suave","nuvem/raio geométrico"),
 ("Natureza","quimica-popsci","Elementos químicos como heróis","Pop-science cartoon","mascote de tabela"),
 ("Natureza","constelacoes-celeste","Constelações","Mapa celeste dourado antigo","carta estelar"),
 # H. Comida & Aconchego
 ("Comida","kawaii-chibi","Comidas kawaii","Chibi pastel","carinha fofa"),
 ("Comida","doces-clay","Doces e sobremesas","Claymation (massinha)","stop-motion"),
 ("Comida","sushi-anime","Sushi e comida japonesa","Anime food art","brilho de anime"),
 ("Comida","cafe-cozy","Café e padaria","Ilustração aconchegante","cozy"),
 ("Comida","fastfood-popart","Fast food com rosto","Pop art vibrante","saturado"),
 ("Comida","especiarias-rotulo","Temperos e especiarias","Rótulo vintage","apotecário"),
 ("Comida","queijos-gourmet","Queijos do mundo","Foto gourmet","tábua"),
 ("Comida","tropicais-vaporwave","Frutas tropicais","Vaporwave neon","rosa/ciano"),
 ("Comida","chas-nanquim","Chás e infusões","Nanquim oriental","sereno"),
 ("Comida","quentes-croche","Bebidas quentes aconchegantes","Crochê/feltro","quentinho"),
 # I. Materiais Puros (mascote genérico, estética radical)
 ("Materiais","lego","Mascote genérico","LEGO / blocos","minifigura"),
 ("Materiais","origami","Mascote genérico","Origami / dobradura","papel dobrado"),
 ("Materiais","voxel","Mascote genérico","Voxel / Minecraft","cubos"),
 ("Materiais","muppet-feltro","Mascote genérico","Muppet (feltro costurado)","boneco simpático"),
 ("Materiais","neon-sign","Mascote genérico","Neon sign","letreiro luminoso"),
 ("Materiais","wojak-mspaint","Mascote genérico","Wojak / feels (MS Paint)","meme cru"),
 ("Materiais","graffiti","Mascote genérico","Graffiti / street art","spray e tag"),
 ("Materiais","balao-mylar","Mascote genérico","Balão inflável / mylar","brilhante e bojudo"),
 ("Materiais","holografico","Mascote genérico","Holográfico iridescente","foil arco-íris"),
 ("Materiais","bronze","Mascote genérico","Escultura de bronze","pátina"),
 # J. Épocas & Movimentos de Arte
 ("Épocas","synthwave","Retrô anos 80","Synthwave","grade e pôr do sol neon"),
 ("Épocas","steampunk","Steampunk","Engrenagens sépia","latão e vapor"),
 ("Épocas","cyberpunk","Cyberpunk","Neon chuvoso","alta tecnologia suja"),
 ("Épocas","artdeco","Art déco","Dourado geométrico 1920s","Gatsby"),
 ("Épocas","hokusai","Onda japonesa","Ukiyo-e clássico (Hokusai)","gravura clássica"),
 ("Épocas","arcade8bit","Arcade retrô","Pixel 8-bit","fliperama"),
 ("Épocas","cubismo","Cubismo","Picasso facetado","planos e ângulos"),
 ("Épocas","surrealismo","Surrealismo","Dalí onírico","derretido e estranho"),
 ("Épocas","suico","Minimalismo suíço","Tipográfico geométrico","grid rígido"),
 ("Épocas","impressionismo","Impressionismo","Pincelada Monet","luz e cor"),
]

# ---------------------------------------------------------------------------
# 100 ROLES — (categoria, slug, nome, é_papel_real_do_mad?)
# ---------------------------------------------------------------------------
REAL = {"arquiteto","pipeline-dev","frontend-dev","dba","devops-installer",
        "security-auditor","qa-tester","docs-writer","llm-prompt","mobile-dev",
        "asset-designer"}
ROLES = [
 # Liderança & Produto
 ("Liderança","arquiteto","Arquiteto de Solução"),
 ("Liderança","tech-lead","Tech Lead"),
 ("Liderança","staff-engineer","Staff Engineer"),
 ("Liderança","principal-engineer","Principal Engineer"),
 ("Liderança","eng-manager","Engineering Manager"),
 ("Liderança","product-manager","Product Manager"),
 ("Liderança","product-owner","Product Owner"),
 ("Liderança","program-manager","Program Manager"),
 ("Liderança","project-manager","Project Manager"),
 ("Liderança","scrum-master","Scrum Master"),
 # Backend & Dados
 ("Backend","backend-dev","Backend Developer"),
 ("Backend","api-designer","API Designer"),
 ("Backend","microservices-eng","Microservices Engineer"),
 ("Backend","pipeline-dev","Pipeline Developer"),
 ("Backend","data-engineer","Data Engineer"),
 ("Backend","dba","Database Administrator"),
 ("Backend","sql-specialist","SQL Specialist"),
 ("Backend","caching-engineer","Caching Engineer"),
 ("Backend","queue-engineer","Message Queue Engineer"),
 ("Backend","search-engineer","Search Engineer"),
 # Frontend & Mobile
 ("Frontend","frontend-dev","Frontend Developer"),
 ("Frontend","ui-engineer","UI Engineer"),
 ("Frontend","ux-designer","UX Designer"),
 ("Frontend","design-systems-eng","Design Systems Engineer"),
 ("Frontend","a11y-specialist","Accessibility Specialist"),
 ("Frontend","web-perf-engineer","Web Performance Engineer"),
 ("Frontend","css-specialist","CSS Specialist"),
 ("Frontend","animation-engineer","Animation Engineer"),
 ("Frontend","mobile-dev","Mobile Developer"),
 ("Frontend","ios-dev","iOS Developer"),
 ("Frontend","android-dev","Android Developer"),
 ("Frontend","react-native-dev","React Native Developer"),
 ("Frontend","flutter-dev","Flutter Developer"),
 # Dados, ML & IA
 ("Dados/IA","data-scientist","Data Scientist"),
 ("Dados/IA","ml-engineer","ML Engineer"),
 ("Dados/IA","mlops-engineer","MLOps Engineer"),
 ("Dados/IA","ai-researcher","AI Researcher"),
 ("Dados/IA","llm-prompt","Prompt Engineer"),
 ("Dados/IA","nlp-engineer","NLP Engineer"),
 ("Dados/IA","cv-engineer","Computer Vision Engineer"),
 ("Dados/IA","data-analyst","Data Analyst"),
 ("Dados/IA","bi-analyst","BI Analyst"),
 ("Dados/IA","analytics-engineer","Analytics Engineer"),
 ("Dados/IA","dataviz-specialist","Data Viz Specialist"),
 # Infra & Ops
 ("Infra","devops-installer","DevOps Engineer"),
 ("Infra","sre","Site Reliability Engineer"),
 ("Infra","platform-engineer","Platform Engineer"),
 ("Infra","cloud-architect","Cloud Architect"),
 ("Infra","k8s-admin","Kubernetes Admin"),
 ("Infra","network-engineer","Network Engineer"),
 ("Infra","sysadmin","Systems Administrator"),
 ("Infra","release-engineer","Release Engineer"),
 ("Infra","build-engineer","Build Engineer"),
 ("Infra","cicd-engineer","CI/CD Engineer"),
 # Segurança
 ("Segurança","security-auditor","Security Engineer"),
 ("Segurança","pentester","Penetration Tester"),
 ("Segurança","appsec-engineer","AppSec Engineer"),
 ("Segurança","cryptographer","Cryptographer"),
 ("Segurança","compliance-officer","Compliance Officer"),
 ("Segurança","privacy-engineer","Privacy Engineer"),
 ("Segurança","incident-responder","Incident Responder"),
 ("Segurança","threat-modeler","Threat Modeler"),
 # Qualidade
 ("Qualidade","qa-tester","QA Engineer"),
 ("Qualidade","sdet","SDET (Automação)"),
 ("Qualidade","perf-tester","Performance Tester"),
 ("Qualidade","manual-tester","Manual Tester"),
 ("Qualidade","a11y-tester","Accessibility Tester"),
 # Conteúdo & Docs
 ("Conteúdo","docs-writer","Technical Writer"),
 ("Conteúdo","dev-advocate","Developer Advocate"),
 ("Conteúdo","content-strategist","Content Strategist"),
 ("Conteúdo","i18n-engineer","Localization Engineer"),
 # Design & Criação
 ("Design","product-designer","Product Designer"),
 ("Design","visual-designer","Visual Designer"),
 ("Design","interaction-designer","Interaction Designer"),
 ("Design","motion-designer","Motion Designer"),
 ("Design","illustrator","Illustrator"),
 ("Design","asset-designer","Asset Designer"),
 ("Design","brand-designer","Brand Designer"),
 ("Design","sound-designer","Sound Designer"),
 ("Design","3d-artist","3D Artist"),
 ("Design","game-designer","Game Designer"),
 ("Design","level-designer","Level Designer"),
 ("Design","narrative-designer","Narrative Designer"),
 # Dev Especializado
 ("Especializado","game-dev","Game Developer"),
 ("Especializado","graphics-engineer","Graphics/Shader Engineer"),
 ("Especializado","embedded-engineer","Embedded Engineer"),
 ("Especializado","firmware-engineer","Firmware Engineer"),
 ("Especializado","iot-engineer","IoT Engineer"),
 ("Especializado","blockchain-dev","Blockchain Developer"),
 ("Especializado","smartcontract-auditor","Smart Contract Auditor"),
 ("Especializado","arvr-engineer","AR/VR Engineer"),
 ("Especializado","robotics-engineer","Robotics Engineer"),
 # Negócio & Suporte
 ("Negócio","growth-engineer","Growth Engineer"),
 ("Negócio","seo-specialist","SEO Specialist"),
 ("Negócio","marketing-tech","Marketing Technologist"),
 ("Negócio","solutions-engineer","Solutions Engineer"),
 ("Negócio","support-engineer","Support Engineer"),
 ("Negócio","sales-engineer","Sales Engineer"),
 ("Negócio","finops","FinOps Analyst"),
 ("Negócio","legal-counsel","Legal Counsel"),
]

assert len(SHEETS) == 100, f"sheets={len(SHEETS)}"
assert len(ROLES) == 100, f"roles={len(ROLES)}"
assert len({s[1] for s in SHEETS}) == 100, "slug de sheet duplicado"
assert len({r[1] for r in ROLES}) == 100, "slug de role duplicado"

sheets = [{"n": i+1, "id": f"s{i+1:03d}", "family": f, "slug": sl,
           "analogy": an, "aesthetic": ae, "vibe": vb}
          for i,(f,sl,an,ae,vb) in enumerate(SHEETS)]
roles = [{"n": i+1, "id": f"r{i+1:03d}", "category": c, "slug": sl, "name": nm,
          "real_mad_role": sl in REAL}
         for i,(c,sl,nm) in enumerate(ROLES)]

# parâmetros do pipeline / grade
manifest = {
 "totals": {"sheets": 100, "roles": 100, "characters": 10000,
            "grid_cols": 5, "grid_rows": 5, "chars_per_grid": 25,
            "grids": 400},
 "character_id_scheme": "s{sheet:03d}-r{role:03d}",
 "grid": {"cell_px": 512, "gutter_px": 24, "margin_px": 24,
          "final_px": 512*5 + 24*4 + 24*2,  # 2704
          "background": "chromakey #00b140 (verde uniforme)",
          "note": "Nano Banana não entrega alpha real confiável; geramos em "
                  "chromakey verde e recortamos/removemos o fundo depois."},
 "navigation_axes": ["role", "analogy", "aesthetic", "family", "category"],
}

(DATA/"sheets.json").write_text(json.dumps(sheets, ensure_ascii=False, indent=1), "utf-8")
(DATA/"roles.json").write_text(json.dumps(roles, ensure_ascii=False, indent=1), "utf-8")
(DATA/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")

# ROLES.md legível
lines = ["# mad — 100 Roles\n"]
cat = None
for r in roles:
    if r["category"] != cat:
        cat = r["category"]; lines.append(f"\n## {cat}")
    star = " ⭐(role real do mad)" if r["real_mad_role"] else ""
    lines.append(f"{r['n']}. **{r['name']}** `{r['slug']}`{star}")
(HERE/"ROLES.md").write_text("\n".join(lines)+"\n", "utf-8")

print(f"OK — {len(sheets)} sheets, {len(roles)} roles")
print(f"grade: {manifest['grid']['final_px']}px, célula {manifest['grid']['cell_px']}px, "
      f"{manifest['totals']['grids']} grids de {manifest['totals']['chars_per_grid']}")
print(f"reais do mad entre os 100 roles: {sum(1 for r in roles if r['real_mad_role'])}")
