# -*- coding: utf-8 -*-
"""
================================================================================
           CONNECTEUR DE MÉMOIRE VIVANTE & PONT KERNEL ALIX (5070 / 5071)
                          Harnais Souverain v2.0
================================================================================
Rôle :
- Branchement direct en priorité sur le Noyau Résident d'Alix (Port 5070, 0.03 ms)
  où les 8 860+ notes Obsidian et 67 500+ liens vivent à chaud en RAM.
- Branchement sur le Noyau Partagé du Kernel (Port 5071) et la Cathédrale Parquet.
- Extraction automatique de l'Ancre de Continuité Épisodique (Memoire_Alix_Active.md,
  Derniere_Discussion_Synthese.md, état du Démon Local 70 BPM) pour garantir qu'aucun
  changement de modèle ne brise la ligne de pensée de l'atelier.
- Repli transparent sur lecture disque Markdown si les démons locaux sont éteints.
================================================================================
"""

import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional


class LocalVaultMemory:
    """Connecteur hybride : Noyau Résident RAM (5070) + Kernel (5071) + Repli Disque."""

    def __init__(
        self,
        vault_paths: List[str],
        noyau_resident_url: str = "http://127.0.0.1:5070",
        noyau_partage_url: str = "http://127.0.0.1:5071",
    ):
        self.vault_paths = [Path(p) for p in vault_paths]
        self.noyau_resident_url = noyau_resident_url.rstrip("/")
        self.noyau_partage_url = noyau_partage_url.rstrip("/")
        self.index: Dict[str, Dict[str, Any]] = {}
        self.resident_online = self.ping_resident()
        if not self.resident_online:
            self._build_index()

    # -------------------------------------------------------------------------
    # SONDES NOYAU RÉSIDENT (PORT 5070) & KERNEL PARTAGÉ (PORT 5071)
    # -------------------------------------------------------------------------
    def ping_resident(self) -> bool:
        """Vérifie si le Noyau Résident (Port 5070) est en vie en RAM."""
        try:
            with urllib.request.urlopen(f"{self.noyau_resident_url}/ping", timeout=0.8) as r:
                data = json.loads(r.read().decode("utf-8"))
                return data.get("status") == "pong" or data.get("statut") == "NOYAU_RESIDENT_EN_VIE"
        except Exception:
            return False

    def ping_kernel(self) -> bool:
        """Vérifie si le Noyau Partagé MCP du Kernel (Port 5071) est en vie."""
        try:
            with urllib.request.urlopen(f"{self.noyau_partage_url}/ping", timeout=0.8) as r:
                data = json.loads(r.read().decode("utf-8"))
                return bool(data.get("ok"))
        except Exception:
            return False

    def _post_json(self, url: str, payload: Dict[str, Any], timeout: float = 3.0) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def query_resident_connectome(self, query: str, top_k: int = 4, max_chars: int = 1200) -> str:
        """Interroge le Connectome en RAM sur le port 5070 en sub-milliseconde."""
        res = self._post_json(f"{self.noyau_resident_url}/recherche", {"query": query, "top_k": top_k}, timeout=1.5)
        if not res or not res.get("resultats"):
            return ""

        duree_ms = res.get("duree_ms", 0)
        snippets = []
        for item in res["resultats"][:top_k]:
            stem = item.get("stem", "")
            coffre = item.get("coffre", "Cerveau Alix")
            score = item.get("score", 0)
            note_data = self._post_json(f"{self.noyau_resident_url}/note", {"titre": stem}, timeout=1.0)
            contenu = ""
            if note_data and note_data.get("contenu"):
                contenu = note_data["contenu"]
            elif item.get("path") and Path(item["path"]).exists():
                try:
                    contenu = Path(item["path"]).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    contenu = ""

            if contenu:
                cleaned = re.sub(r"^\ufeff?---[\s\S]*?---", "", contenu).strip()
                snippets.append(f"### [[{stem}]] ({coffre} · score {score})\n{cleaned[:max_chars]}")

        if not snippets:
            return ""

        return (
            f"\n---\n**🧠 CONNECTOME RAM (Port 5070 · {duree_ms} ms) :**\n"
            + "\n\n".join(snippets)
            + "\n---\n"
        )

    def get_active_continuity_anchor(self) -> str:
        """
        Lit directement les ancres de continuité du Cerveau Alix :
        1. Derniere_Discussion_Synthese.md (point d'arrêt de la dernière session)
        2. Jalons récents de Memoire_Alix_Active.md
        3. État du Démon Local Souverain (70 BPM)
        Garantit qu'aucun changement de modèle ne perd le fil de l'atelier.
        """
        cerveau_dir = self.vault_paths[0] if self.vault_paths else Path(r"C:\Alix\SAUVEGARDE_ALIX\Cerveau Alix")
        blocs = []

        # 1. Jalons de Memoire_Alix_Active.md
        mem_active = cerveau_dir / "Memoire_Alix_Active.md"
        if mem_active.exists():
            try:
                jalons = []
                with open(mem_active, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        ls = line.strip()
                        if ls.startswith("- 2026-") and "**" in ls:
                            jalons.append(ls[:220])
                            if len(jalons) >= 4:
                                break
                if jalons:
                    blocs.append("📌 **Derniers Jalons Scellés ([[Memoire_Alix_Active]]) :**\n" + "\n".join(jalons))
            except Exception:
                pass

        # 2. Continuité de Derniere_Discussion_Synthese.md
        synthese_file = cerveau_dir / "Derniere_Discussion_Synthese.md"
        if synthese_file.exists():
            try:
                txt = synthese_file.read_text(encoding="utf-8", errors="ignore")
                cleaned = re.sub(r"^---[\s\S]*?---", "", txt).strip()
                blocs.append("📜 **Continuité Immédiate ([[Derniere_Discussion_Synthese]]) :**\n" + cleaned[:1200])
            except Exception:
                pass

        return "\n\n".join(blocs)

    # -------------------------------------------------------------------------
    # RECHERCHE UNIFIÉE (5070 RAM D'ABORD -> REPLI DISQUE)
    # -------------------------------------------------------------------------
    def search_context(self, query: str, max_notes: int = 3, max_chars_per_note: int = 1200) -> str:
        """
        Interroge en priorité le Connectome RAM (Port 5070).
        Bascule sur l'index disque local uniquement si le démon 5070 ne répond pas.
        """
        ram_res = self.query_resident_connectome(query, top_k=max_notes, max_chars=max_chars_per_note)
        if ram_res:
            self.resident_online = True
            return ram_res

        # Repli disque si le port 5070 n'a rien retourné ou est éteint
        if not self.index:
            self._build_index()
        if not self.index:
            return ""

        words = set(re.findall(r"\b[A-Za-zÀ-ÿ0-9_-]{3,}\b", query.lower()))
        scores: Dict[str, int] = {}

        for key, data in self.index.items():
            score = 0
            for w in words:
                if w in key:
                    score += 5
            if score > 0:
                scores[key] = score

        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:max_notes]
        if not sorted_keys:
            return ""

        snippets = []
        for k in sorted_keys:
            data = self.index[k]
            try:
                with open(data["path"], "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read(max_chars_per_note)
                    cleaned = re.sub(r"^---[\s\S]*?---", "", content).strip()
                    snippets.append(f"### [[{data['stem']}]]\n{cleaned[:max_chars_per_note]}")
            except Exception:
                continue

        if not snippets:
            return ""

        return "\n\n---\n**📚 MÉMOIRE LOCALE EXTRAITE DU COFFRE :**\n" + "\n\n".join(snippets) + "\n---\n"

    def _build_index(self):
        """Indexe les fichiers markdown sur disque (utilisé en repli si port 5070 inactif)."""
        self.index.clear()
        for vpath in self.vault_paths:
            if not vpath.exists():
                continue
            for root, _, files in os.walk(vpath):
                for f in files:
                    if f.endswith(".md"):
                        full_path = Path(root) / f
                        stem = full_path.stem
                        self.index[stem.lower()] = {
                            "stem": stem,
                            "path": full_path,
                            "filename": f,
                        }
