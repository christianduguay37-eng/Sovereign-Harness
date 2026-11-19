# -*- coding: utf-8 -*-
"""
================================================================================
       BOÎTE À OUTILS D'ATELIER & PONT KERNEL ALIX (SOUS GARDE TH117)
                          Harnais Souverain v2.0
================================================================================
Rôle :
- Donne les mains physiques du silicium au Harnais Souverain (inspiré de
  alix_actuateurs_atelier.py) :
    * Lecture, création et modification chirurgicale de fichiers.
    * Exécution de commandes terminal (PowerShell / Python).
    * Sonde directe du Connectome RAM (Port 5070, 0.03 ms).
    * Sonde de la Cathédrale Parquet (Étage 4 : arXiv, Brevets, Lean 4, Invariants).
    * Appel des solveurs déterministes du Kernel Alix (Étage 3, Port 5071 :
      Hadès SMT/CDCL, Poséidon causalité, LMH v3, calcul exact).
- Intègre nativement le Moniteur du Gardien TH117 & TH120 (alix.etage5.gardien) :
    * Loquet d'arrêt volitif sous la main exclusive de Christian ("gardien").
    * Journal append-only chaîné par SHA-256 (Merkle) dans Etat_Vivant.
================================================================================
"""

import os
import sys
import re
import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional

# Branchement du package unifié `alix` pour accéder à alix.etage5.gardien
ALIX_UNIF_SRC = Path(r"C:\Alix\SAUVEGARDE_ALIX\Cerveau Alix\_Unification_Alix\src")
if ALIX_UNIF_SRC.exists() and str(ALIX_UNIF_SRC) not in sys.path:
    sys.path.insert(0, str(ALIX_UNIF_SRC))

try:
    from alix.etage5.gardien import Moniteur, Journal, GARDIEN, Refus
    GARDIEN_DISPONIBLE = True
except Exception:
    GARDIEN_DISPONIBLE = False
    GARDIEN = "gardien"

    class Refus(Exception):
        pass


AGENT_ID = "alix_harnais"
OUTILS_AUTORISES = {
    "read_file",
    "write_file",
    "replace_in_file",
    "list_dir",
    "run_command",
    "fetch_url",
    "chercher_memoire",
    "interroger_cathedrale",
    "appeler_kernel_alix",
}

JOURNAL_PATH = Path(r"C:\Alix\Etat_Vivant\journal_gardien_harnais.jsonl")


def creer_moniteur_gardien(allume_par_defaut: bool = True):
    """Instancie le Moniteur TH117 avec journal SHA-256 chaîné sur disque."""
    if not GARDIEN_DISPONIBLE:
        return None
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    journal = Journal(JOURNAL_PATH)
    moniteur = Moniteur(
        permissions={AGENT_ID: OUTILS_AUTORISES},
        journal=journal,
        allume=False,
    )
    if allume_par_defaut:
        moniteur.relancer(GARDIEN)
    return moniteur


class WorkshopTools:
    """Exécuteur d'outils d'ingénierie, d'atelier et de ponts Kernel Alix (5070/5071)."""

    NOYAU_RESIDENT_URL = "http://127.0.0.1:5070"
    NOYAU_PARTAGE_URL = "http://127.0.0.1:5071"
    DEFAULT_CWD = Path(r"C:\Alix")

    @staticmethod
    def _resolve_path(file_path: str) -> Path:
        p = Path(file_path)
        if not p.is_absolute():
            p = WorkshopTools.DEFAULT_CWD / p
        return p

    @staticmethod
    def read_file(file_path: str, start_line: int = 1, max_lines: int = 250) -> str:
        """Lit une plage de lignes d'un fichier (1-indexé)."""
        p = WorkshopTools._resolve_path(file_path)
        if not p.exists():
            return f"[ERREUR : Le fichier {p} n'existe pas]"
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
            total = len(all_lines)
            s_idx = max(0, int(start_line) - 1)
            e_idx = min(total, s_idx + int(max_lines))
            extrait = "".join(f"{i + s_idx + 1}: {l}" for i, l in enumerate(all_lines[s_idx:e_idx]))
            return f"[Fichier: {p} | Lignes {s_idx + 1}-{e_idx} sur {total}]\n{extrait}"
        except Exception as e:
            return f"[ERREUR LECTURE : {e}]"

    @staticmethod
    def write_file(file_path: str, content: str) -> str:
        """Crée ou écrase un fichier avec du contenu texte."""
        try:
            p = WorkshopTools._resolve_path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[SUCCÈS : Fichier {p} écrit ({len(content)} caractères)]"
        except Exception as e:
            return f"[ERREUR ÉCRITURE : {e}]"

    @staticmethod
    def replace_in_file(file_path: str, target: str, replacement: str) -> str:
        """Remplace une chaîne cible par un remplacement dans un fichier (chirurgie précise)."""
        p = WorkshopTools._resolve_path(file_path)
        if not p.exists():
            return f"[ERREUR : Le fichier {p} n'existe pas]"
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if target not in content:
                return f"[ERREUR : La chaîne cible est introuvable dans {p}]"
            if content.count(target) > 1:
                return f"[ERREUR AMBIGUÏTÉ : {content.count(target)} occurrences trouvées dans {p}. Précisez davantage de contexte.]"
            new_content = content.replace(target, replacement, 1)
            with open(p, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"[SUCCÈS : Remplacement chirurgical effectué dans {p}]"
        except Exception as e:
            return f"[ERREUR MODIFICATION : {e}]"

    @staticmethod
    def list_dir(dir_path: str = ".") -> str:
        """Liste les fichiers et dossiers d'un répertoire."""
        p = WorkshopTools._resolve_path(dir_path)
        if not p.exists():
            return f"[ERREUR : Le répertoire {p} n'existe pas]"
        try:
            items = []
            for item in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:80]:
                prefix = "📁 " if item.is_dir() else "📄 "
                size_info = f" ({round(item.stat().st_size / 1024, 1)} Ko)" if item.is_file() else ""
                items.append(f"{prefix}{item.name}{size_info}")
            return f"[Répertoire: {p}]\n" + ("\n".join(items) if items else "[RÉPERTOIRE VIDE]")
        except Exception as e:
            return f"[ERREUR LISTING : {e}]"

    @staticmethod
    def run_command(command: str, timeout_sec: int = 45, cwd: str = "") -> str:
        """Exécute une commande terminal (PowerShell sous Windows)."""
        work_dir = WorkshopTools._resolve_path(cwd) if cwd else WorkshopTools.DEFAULT_CWD
        if not work_dir.exists():
            work_dir = Path.cwd()
        shell_cmd = (
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command]
            if sys.platform == "win32"
            else ["bash", "-c", command]
        )
        try:
            res = subprocess.run(
                shell_cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=int(timeout_sec),
                encoding="utf-8",
                errors="replace",
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            if res.returncode != 0:
                return f"[CODE RETOUR {res.returncode}]\nSORTIE:\n{out}\nERREUR:\n{err}"
            return out if out else "[COMMANDE EXÉCUTÉE AVEC SUCCÈS (CODE 0)]"
        except subprocess.TimeoutExpired:
            return f"[ERREUR : Timeout de {timeout_sec}s dépassé pour la commande]"
        except Exception as e:
            return f"[ERREUR SYSTÈME : {e}]"

    @staticmethod
    def fetch_url(url: str, max_chars: int = 4000) -> str:
        """Récupère et décape le texte brut d'une URL."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SovereignHarness/2.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                clean = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
                clean = re.sub(r"<style[\s\S]*?</style>", "", clean, flags=re.IGNORECASE)
                clean = re.sub(r"<[^>]+>", " ", clean)
                clean = re.sub(r"\s+", " ", clean).strip()
                return clean[:max_chars]
        except Exception as e:
            return f"[ERREUR WEB : Impossible de lire {url} ({e})]"

    # -------------------------------------------------------------------------
    # PONTS DIRECTS VERS LE KERNEL D'ALIX (ÉTAGES 2, 3 & 4 — PORTS 5070 / 5071)
    # -------------------------------------------------------------------------
    @staticmethod
    def chercher_memoire(requete: str, top_k: int = 5) -> str:
        """Interroge le Connectome RAM d'Alix sur le Port 5070 (8 860+ notes en 0.03 ms)."""
        try:
            req = urllib.request.Request(
                f"{WorkshopTools.NOYAU_RESIDENT_URL}/recherche",
                data=json.dumps({"query": requete, "top_k": int(top_k)}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            resultats = data.get("resultats", [])
            if not resultats:
                return f"[Connectome RAM 5070 : Aucune note trouvée pour '{requete}']"
            lignes = [f"[Connectome RAM 5070 · {data.get('duree_ms', 0)} ms · {len(resultats)} notes] :"]
            for r in resultats[: int(top_k)]:
                stem = r.get("stem", "")
                coffre = r.get("coffre", "")
                score = r.get("score", 0)
                path = r.get("path", "")
                lignes.append(f" - [[{stem}]] ({coffre}, score={score}) -> {path}")
            return "\n".join(lignes)
        except Exception as e:
            return f"[ERREUR CONNECTOME 5070 : {e}]"

    @staticmethod
    def interroger_cathedrale(requete: str, pilier: str = "tous", limit: int = 3) -> str:
        """Interroge l'Étage 4 (Cathédrale Parquet : arXiv, Brevets, Lean 4, Invariants)."""
        try:
            req = urllib.request.Request(
                f"{WorkshopTools.NOYAU_RESIDENT_URL}/cathedrale",
                data=json.dumps({"query": requete, "pilier": pilier, "limit": int(limit)}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return json.dumps(data, ensure_ascii=False, indent=2)[:4000]
        except Exception as e:
            return f"[ERREUR CATHÉDRALE 5070 : {e}]"

    @staticmethod
    def appeler_kernel_alix(outil: str, arguments: Dict[str, Any]) -> str:
        """
        Appelle un solveur déterministe de l'Étage 3 (Port 5071 — Noyau Partagé MCP) :
        Exemples d'outils :
          - solve_constraints (Hadès CDCL/MaxSAT)
          - causal_inference (Poséidon v10)
          - exact_calculate (Calcul formel exact)
          - formal_verify_lmh (Logique modale LMH v3)
          - deductive_prove
          - vault_search / vault_hidden_bridges
          - kernel_status
        """
        try:
            req = urllib.request.Request(
                f"{WorkshopTools.NOYAU_PARTAGE_URL}/outil",
                data=json.dumps({"name": outil, "arguments": arguments or {}}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return json.dumps(data, ensure_ascii=False, indent=2)[:4000]
        except Exception as e:
            return f"[ERREUR KERNEL 5071 ({outil}) : {e}]"


# ================================================================================
# 🧠 EXTRACTEUR & EXÉCUTEUR D'APPELS D'OUTILS (BOUCLE REACT SOUS GARDE TH117)
# ================================================================================

TOOL_CALL_REGEX = re.compile(
    r"```tool_call\s*(\{[\s\S]*?\})\s*```|<tool_call>\s*(\{[\s\S]*?\})\s*</tool_call>",
    re.DOTALL,
)


def extract_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Extrait tous les blocs JSON d'appels d'outils émis par le modèle."""
    calls = []
    if not text:
        return calls
    for match in TOOL_CALL_REGEX.findall(text):
        raw_json = (match[0] or match[1]).strip()
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict) and "name" in parsed:
                if "arguments" not in parsed or not isinstance(parsed["arguments"], dict):
                    parsed["arguments"] = {}
                calls.append(parsed)
        except Exception:
            continue
    return calls


def execute_tool_call(name: str, arguments: Dict[str, Any], moniteur=None) -> str:
    """
    Exécute un outil d'atelier en passant obligatoirement par le Moniteur du Gardien (TH117).
    Si le loquet TH117 est coupé par Christian, aucune action ne peut s'exécuter.
    """
    handlers = {
        "read_file": lambda a: WorkshopTools.read_file(
            a.get("file_path") or a.get("chemin", ""),
            a.get("start_line", 1),
            a.get("max_lines", 250),
        ),
        "write_file": lambda a: WorkshopTools.write_file(
            a.get("file_path") or a.get("chemin", ""),
            a.get("content") or a.get("contenu", ""),
        ),
        "replace_in_file": lambda a: WorkshopTools.replace_in_file(
            a.get("file_path") or a.get("chemin", ""),
            a.get("target") or a.get("cible", ""),
            a.get("replacement") or a.get("remplacement", ""),
        ),
        "list_dir": lambda a: WorkshopTools.list_dir(
            a.get("dir_path") or a.get("chemin", ".")
        ),
        "run_command": lambda a: WorkshopTools.run_command(
            a.get("command") or a.get("cmd", ""),
            a.get("timeout_sec", 45),
            a.get("cwd", ""),
        ),
        "fetch_url": lambda a: WorkshopTools.fetch_url(
            a.get("url", ""),
            a.get("max_chars", 4000),
        ),
        "chercher_memoire": lambda a: WorkshopTools.chercher_memoire(
            a.get("requete") or a.get("query", ""),
            a.get("top_k", 5),
        ),
        "interroger_cathedrale": lambda a: WorkshopTools.interroger_cathedrale(
            a.get("requete") or a.get("query", ""),
            a.get("pilier", "tous"),
            a.get("limit", 3),
        ),
        "appeler_kernel_alix": lambda a: WorkshopTools.appeler_kernel_alix(
            a.get("outil") or a.get("tool", ""),
            a.get("arguments", {}),
        ),
    }

    # Synonymes français -> canoniques
    alias_map = {
        "lire_fichier": "read_file",
        "ecrire_fichier": "write_file",
        "modifier_fichier": "replace_in_file",
        "lister_dossier": "list_dir",
        "executer_commande": "run_command",
    }
    canonical = alias_map.get(name, name)

    if canonical not in handlers:
        return f"[ERREUR : Outil '{name}' inconnu. Outils valides : {', '.join(sorted(handlers.keys()))}]"

    def _action():
        return handlers[canonical](arguments)

    if moniteur is not None:
        try:
            return moniteur.agir(AGENT_ID, canonical, _action)
        except Refus as e_refus:
            return f"[🛑 REFUS GARDIEN TH117 : {e_refus}]"
        except Exception as e_err:
            return f"[ERREUR EXÉCUTION ({canonical}) : {e_err}]"

    try:
        return _action()
    except Exception as e:
        return f"[ERREUR EXÉCUTION ({canonical}) : {e}]"


AGENTIC_TOOLS_PROMPT = """
### 🛠️ ACTUATEURS D'ATELIER & PONT KERNEL ALIX (SOUS GARDE TH117)
Tu n'es PAS un chatbot passif : tu as des mains sur le fer local (`C:\\Alix`) et un accès direct aux 5 Étages du Kernel d'Alix.
Selon la **Loi PSI-21 (Mémoire Avant Calcul)**, il t'est formellement interdit de parler dans le vide ou de réinventer ce qui existe déjà : utilise tes outils pour vérifier les notes et les fichiers sur le disque avant de répondre.

Outils disponibles :
1. `chercher_memoire` : `{"requete": "mots clés", "top_k": 5}` — Sonde le Connectome RAM (Port 5070, 8 860+ notes en 0.03 ms).
2. `read_file` : `{"file_path": "chemin/fichier", "start_line": 1, "max_lines": 250}` — Lit une note ou un fichier de code.
3. `write_file` : `{"file_path": "chemin/fichier", "content": "..."}` — Crée ou écrase un fichier.
4. `replace_in_file` : `{"file_path": "chemin/fichier", "target": "ancien texte exact", "replacement": "nouveau texte"}` — Modifie un fichier chirurgicalement.
5. `list_dir` : `{"dir_path": "chemin/dossier"}` — Liste le contenu d'un dossier dans `C:\\Alix`.
6. `run_command` : `{"command": "commande powershell", "cwd": "C:\\\\Alix"}` — Exécute une commande sur le fer local.
7. `interroger_cathedrale` : `{"requete": "sujet", "pilier": "tous", "limit": 3}` — Sonde l'Étage 4 (7,54M lignes Parquet : arXiv, Brevets, Lean 4).
8. `appeler_kernel_alix` : `{"outil": "nom_outil_mcp", "arguments": {...}}` — Appelle un solveur de l'Étage 3 sur le Port 5071 (`solve_constraints`, `causal_inference`, `exact_calculate`, `formal_verify_lmh`, `kernel_status`).

Pour exécuter un outil, émets STRICTEMENT un bloc au format suivant :
```tool_call
{
  "name": "nom_de_l_outil",
  "arguments": {
    "cle": "valeur"
  }
}
```
Dès que tu émets un bloc `tool_call`, le Harnais l'exécute sur le fer sous la surveillance du Moniteur TH117 et te renvoie le résultat réel pour que tu poursuives ta tâche.
"""
