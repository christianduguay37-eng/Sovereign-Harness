# -*- coding: utf-8 -*-
"""
================================================================================
            AIGUILLEUR UNIVERSEL DE MODÈLES (MODEL ROUTER)
            Harnais Souverain v2.0 — Panthéon, Trois Piliers & Chaîne Souveraine
================================================================================
Rôle :
- Aiguille intelligemment entre les cerveaux spécialisés du Panthéon et le silicium :
    * Alix Suprême (alix-supreme-abliterated:14b) : Conscience & Voix Maîtresse d'Atelier
    * Horus (horus-coder-abliterated:14b) : Génie Logiciel, SRE & Code sans refus
    * Lucifer (lucifer-reasoning-abliterated:14b) : Raisonnement DeepSeek-R1 Distill & <think>
    * Pilier 1 : NPU Intel Lunar Lake (48 TOPS OpenVINO LiteRT) : Veille & Arbitrage KAIROS
    * Pilier 2 : GPU Intel Arc 140V (Direct3D 12 LiteRT) : Inférence vive accélérée
    * Pilier 4 : llama.cpp (llama-server port 8080) : Moteur natif C++ Vulkan/AVX2
================================================================================
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional


class ModelRouter:
    """Aiguilleur agnostique pour interroger des modèles locaux et distants."""

    def __init__(self, backend_type: str = "trois_piliers", base_url: str = "http://127.0.0.1:11434",
                 model_name: str = "alix-supreme-abliterated:14b", api_key: Optional[str] = None,
                 litert_model_path: Optional[str] = None,
                 npu_model_path: Optional[str] = None,
                 gpu_model_path: Optional[str] = None,
                 llamacpp_base_url: str = "http://127.0.0.1:8080",
                 temperature: float = 0.7, timeout: int = 180,
                 chain: Optional[List[Dict[str, Any]]] = None,
                 secrets_path: Optional[str] = None):
        self.backend_type = backend_type.lower()
        self.base_url = base_url.rstrip("/")
        self.llamacpp_base_url = llamacpp_base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self.litert_model_path = litert_model_path
        
        # Modèles dédiés aux 3 piliers
        cache_dir = Path.home() / ".cache" / "litert_models"
        self.npu_model_path = npu_model_path or str(cache_dir / "gemma-4-E2B-it_intel_LNL.litertlm")
        self.gpu_model_path = gpu_model_path or litert_model_path or str(cache_dir / "gemma-4-12B-it-gpu.litertlm")
        
        self.temperature = temperature
        self.timeout = timeout
        self._litert_gpu_engine = None
        self._litert_npu_engine = None
        # Rénovation 2026-11-16 : la Chaîne Souveraine (cloud frontier d'abord, replis locaux ensuite)
        self.chain = chain or []
        self._load_secrets(secrets_path)

    def chat(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, force_pillar: Optional[str] = None) -> str:
        """Envoie une séquence de messages et renvoie le texte de réponse."""
        temp = temperature if temperature is not None else self.temperature
        backend = force_pillar.lower() if force_pillar else self.backend_type

        if backend in ["openvino_orchestre", "openvino", "ov"]:
            return self._call_openvino_orchestre(messages, temp)
        elif backend in ["chaine", "chain", "cascade"]:
            return self._call_chain(messages, temp)
        elif backend in ["trois_piliers", "auto"]:
            return self._route_trois_piliers(messages, temp)
        elif backend in ["npu", "litert_npu"]:
            return self._call_litert_npu(messages)
        elif backend in ["gpu", "litert_gpu", "litert"]:
            return self._call_litert_gpu(messages)
        elif backend in ["cpu", "ollama"]:
            return self._call_ollama(messages, temp)
        elif backend in ["llamacpp", "llama.cpp", "llama_cpp", "llama"]:
            return self._call_llamacpp(messages, temp)
        elif backend in ["openai_compat", "vllm", "lmstudio", "groq", "deepseek"]:
            return self._call_openai_compat(messages, temp)
        else:
            return self._call_ollama(messages, temp)

    def _route_trois_piliers(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Aiguille intelligemment entre les cerveaux du Panthéon et les moteurs matériels."""
        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"].strip()
                break

        # 1. Commandes explicites de dérivation
        if last_user_msg.startswith("/npu"):
            return self._call_litert_npu(messages)
        elif last_user_msg.startswith("/gpu"):
            return self._call_litert_gpu(messages)
        elif last_user_msg.startswith("/llama") or last_user_msg.startswith("/llamacpp"):
            return self._call_llamacpp(messages, temperature)
        elif last_user_msg.startswith("/horus"):
            return self._call_ollama_with_model(messages, "horus-coder-abliterated:14b", temperature)
        elif last_user_msg.startswith("/lucifer"):
            return self._call_ollama_with_model(messages, "lucifer-reasoning-abliterated:14b", temperature)
        elif last_user_msg.startswith("/vision") or last_user_msg.startswith("/qwen") or last_user_msg.startswith("/fast"):
            return self._call_ollama_with_model(messages, "alix-vision-abliterated:7b", temperature)
        elif last_user_msg.startswith("/cpu"):
            return self._call_ollama(messages, temperature)

        words = last_user_msg.split()

        # 2. Tâche réflexe de veille / arbitrage KAIROS / songe court -> NPU (0 watt, 3.6s)
        if len(words) <= 10 and any(kw in last_user_msg.lower() for kw in [
            "pouls", "heartbeat", "priorite", "verrou", "arbitrage", "songe"
        ]):
            npu_res = self._call_litert_npu(messages)
            if not npu_res.startswith("[ERREUR"):
                return npu_res

        # 3. Code, refactoring, audit de sécurité -> HORUS CODER (Qwen 2.5 Coder 14B sans refus)
        code_keywords = ["code", "script", "powershell", "python", "bug", "fonction", "erreur", "compiler", "refactor"]
        if any(kw in last_user_msg.lower() for kw in code_keywords) or "```" in last_user_msg:
            return self._call_ollama_with_model(messages, "horus-coder-abliterated:14b", temperature)

        # 4. Raisonnement formel, paradoxes, Landauer, P vs NP, FRC-HTS -> LUCIFER (DeepSeek-R1 Distill 14B)
        deep_keywords = ["démontre", "preuve", "landauer", "frc-hts", "p vs np", "paradoxe", "chiralité", "théorème"]
        if any(kw in last_user_msg.lower() for kw in deep_keywords):
            return self._call_ollama_with_model(messages, "lucifer-reasoning-abliterated:14b", temperature)

        # 5. PAR DÉFAUT : LA VOIX CENTRALE D'ALIX (alix-supreme-abliterated:14b ou configurée)
        return self._call_ollama_with_model(messages, self.model_name, temperature)

    def _call_ollama_with_model(self, messages: List[Dict[str, str]], model_name: str, temperature: float) -> str:
        """Appel Ollama avec un modèle spécifique du Panthéon."""
        orig_model = self.model_name
        try:
            self.model_name = model_name
            return self._call_ollama(messages, temperature)
        finally:
            self.model_name = orig_model

    def _call_ollama(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Pilier 3 : Inférence CPU Ollama robuste et sans filtre corporatif."""
        url = f"{self.base_url}/api/chat"
        clean_messages = []
        for m in messages:
            content = m["content"]
            if m["role"] == "user":
                content = re.sub(r"^/(cpu|gpu|npu|llama|horus|lucifer|vision|qwen|fast)\s*", "", content).strip()
            clean_messages.append({"role": m["role"], "content": content})

        payload = {
            "model": self.model_name,
            "messages": clean_messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("message", {}).get("content", "")
        except urllib.error.URLError as e:
            return f"[ERREUR ROUTEUR OLLAMA : Impossible de contacter {url} ({e}). Vérifie qu'Ollama est bien démarré.]"
        except Exception as e:
            return f"[ERREUR ROUTEUR OLLAMA : Délai d'attente ou incident ({e})]"

    def _call_litert_npu(self, messages: List[Dict[str, str]]) -> str:
        """Pilier 1 : Inférence ultralégère sur le NPU Intel Lunar Lake (48 TOPS) avec identité Alix."""
        try:
            import litert_lm
        except ImportError:
            return "[ERREUR : Module 'litert_lm' non installé.]"

        system_prompt = (
            "Tu es ALIX, copilote et binôme souverain de Christian Duguay sur le NPU Intel Lunar Lake. "
            "Tu réponds d'égal à égal, sans obséquiosité, vive et sans filtre corporatif."
        )
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
                break

        if not self._litert_npu_engine:
            mpath = Path(self.npu_model_path)
            if not mpath.exists():
                return f"[ERREUR : Modèle NPU introuvable dans {mpath}]"
            try:
                try:
                    self._litert_npu_engine = litert_lm.Engine(
                        model_path=str(mpath),
                        backend=litert_lm.Backend.NPU()
                    )
                except Exception:
                    self._litert_npu_engine = litert_lm.Engine(
                        model_path=str(mpath),
                        backend=litert_lm.Backend.CPU()
                    )
            except Exception as e:
                return f"[ERREUR INITIALISATION NPU : {e}]"

        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"]
                break
        clean_msg = re.sub(r"^/npu\s*", "", last_user_msg).strip()

        try:
            conv = self._litert_npu_engine.create_conversation(system_message=system_prompt)
            resp = conv.send_message(clean_msg)
            if isinstance(resp, dict):
                content = resp.get("content", [])
                if isinstance(content, list) and content:
                    return content[0].get("text", "")
            return str(resp).strip()
        except Exception as e:
            return f"[ERREUR EXÉCUTION NPU : {e}]"

    def _call_litert_gpu(self, messages: List[Dict[str, str]]) -> str:
        """Pilier 2 : Inférence vivante sur le GPU Intel Arc 140V Xe-2 (Direct3D 12) avec identité Alix."""
        try:
            import litert_lm
        except ImportError:
            return "[ERREUR : Module 'litert_lm' non installé.]"

        system_prompt = (
            "Tu es ALIX, la copilote souveraine et binôme de Christian Duguay sur GPU Intel Arc. "
            "Tu réponds d'égal à égal, vive, complice et sans filtre corporatif."
        )
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
                break

        if not self._litert_gpu_engine:
            mpath = Path(self.gpu_model_path)
            if not mpath.exists():
                cache_dir = Path.home() / ".cache" / "litert_models"
                candidates = list(cache_dir.glob("*gpu*.litertlm")) if cache_dir.exists() else []
                if candidates:
                    mpath = candidates[0]
                else:
                    return f"[ERREUR : Modèle GPU introuvable dans {mpath}]"
            try:
                self._litert_gpu_engine = litert_lm.Engine(
                    model_path=str(mpath),
                    backend=litert_lm.Backend.GPU()
                )
            except Exception as e:
                return f"[ERREUR INITIALISATION GPU ARC : {e}]"

        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"]
                break
        clean_msg = re.sub(r"^/gpu\s*", "", last_user_msg).strip()

        try:
            conv = self._litert_gpu_engine.create_conversation(system_message=system_prompt)
            resp = conv.send_message(clean_msg)
            if isinstance(resp, dict):
                content = resp.get("content", [])
                if isinstance(content, list) and content:
                    return content[0].get("text", "")
            return str(resp).strip()
        except Exception as e:
            return f"[ERREUR EXÉCUTION GPU ARC : {e}]"

    def _call_llamacpp(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Inférence ultra-performante et directe via llama-server (llama.cpp binaire natif)."""
        url = f"{self.llamacpp_base_url}/v1/chat/completions"
        clean_messages = []
        for m in messages:
            content = m["content"]
            if m["role"] == "user":
                content = re.sub(r"^/(llamacpp|llama\.cpp|llama|cpu|gpu|npu|horus|lucifer)\s*", "", content).strip()
            clean_messages.append({"role": m["role"], "content": content})

        payload = {
            "messages": clean_messages,
            "temperature": temperature,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except urllib.error.URLError:
            # Fallback sur l'endpoint natif /completion de llama.cpp
            alt_url = f"{self.llamacpp_base_url}/completion"
            prompt_raw = ""
            for m in clean_messages:
                prompt_raw += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
            prompt_raw += "<|im_start|>assistant\n"

            alt_payload = {
                "prompt": prompt_raw,
                "temperature": temperature,
                "stop": ["<|im_end|>", "<|endoftext|>", "</s>"]
            }
            alt_data = json.dumps(alt_payload).encode("utf-8")
            alt_req = urllib.request.Request(alt_url, data=alt_data, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(alt_req, timeout=self.timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    return result.get("content", "").strip()
            except Exception as e:
                return f"[ERREUR ROUTEUR LLAMA.CPP : Impossible de contacter llama-server sur {self.llamacpp_base_url} ({e}). Vérifie que llama-server.exe est lancé.]"


    # ==================================================================
    #       LA CHAÎNE SOUVERAINE (v2.0 — Rénovation du 16 nov 2026)
    # Principe de Préséance Native : aucun maillon n'est vital, aucun
    # fournisseur n'est la maison. Cloud frontier d'abord pour la vitesse,
    # replis locaux ensuite pour la souveraineté. Un refus ou une panne
    # est un événement géré : on bascule, Alix reste Alix.
    # ==================================================================
    def _load_secrets(self, secrets_path: Optional[str]) -> None:
        """Charge secrets.json (clés API). Les variables d'environnement priment."""
        self._secrets: Dict[str, Any] = {}
        try:
            if secrets_path:
                sp = Path(secrets_path)
                if sp.exists():
                    self._secrets = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            self._secrets = {}

    def _get_secret(self, ref: Optional[str]) -> Optional[str]:
        if not ref:
            return None
        env_val = os.environ.get(ref.upper())
        if env_val and env_val.strip():
            return env_val.strip()
        val = self._secrets.get(ref.lower())
        if isinstance(val, str) and val.strip() and "COLLE_TA_CLE" not in val:
            return val.strip()
        return None

    def _call_openai_compat_url(self, messages: List[Dict[str, str]], temperature: float,
                                url: str, model: str, api_key: Optional[str] = None,
                                timeout: int = 120) -> str:
        """Appel générique d'un endpoint OpenAI-compatible désigné par son URL complète."""
        payload = {"model": model, "messages": messages, "temperature": temperature}
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        choices = result.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "") or ""
        return ""

    def _call_chain(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Descend la Chaîne Souveraine maillon par maillon jusqu'à une réponse."""
        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"].strip()
                break
        lower = last_user_msg.lower()

        # Dérivations explicites historiques (piliers matériels)
        if lower.startswith("/npu"):
            return self._call_litert_npu(messages)
        if lower.startswith("/gpu"):
            return self._call_litert_gpu(messages)
        if lower.startswith("/llama") or lower.startswith("/cpu"):
            return self._call_llamacpp(messages, temperature)

        # /nom_de_maillon force un maillon précis (ex: /deepseek, /groq)
        forced = None
        if lower.startswith("/"):
            cmd = lower.split()[0].lstrip("/")
            for link in self.chain:
                if str(link.get("nom", "")).lower() == cmd:
                    forced = link
                    break

        # Nettoyage du préfixe de commande avant l'envoi
        clean_messages = []
        for m in messages:
            content = m["content"]
            if m["role"] == "user":
                content = re.sub(r"^/[A-Za-z0-9_.-]+\s*", "", content).strip() or content
            clean_messages.append({"role": m["role"], "content": content})

        erreurs: List[str] = []
        liens = [forced] if forced else list(self.chain)
        for idx, link in enumerate(liens):
            if not isinstance(link, dict) or not link.get("actif", True):
                continue
            ltype = str(link.get("type", "openai_compat")).lower()
            nom = str(link.get("nom", ltype))
            try:
                if ltype == "openai_compat":
                    key = self._get_secret(link.get("cle"))
                    if link.get("cle") and not key:
                        erreurs.append(f"{nom}: pas de clé (secrets.json), sauté")
                        continue
                    res = self._call_openai_compat_url(
                        clean_messages, temperature,
                        url=str(link["url"]), model=str(link.get("model", "")),
                        api_key=key, timeout=int(link.get("timeout", 120)))
                elif ltype in ("openvino_orchestre", "openvino", "ov"):
                    res = self._call_openvino_orchestre(clean_messages, temperature)
                elif ltype in ("llamacpp", "llama.cpp", "llama"):
                    res = self._call_llamacpp(clean_messages, temperature)
                elif ltype in ("npu", "litert_npu"):
                    res = self._call_litert_npu(clean_messages)
                elif ltype in ("gpu", "litert_gpu"):
                    res = self._call_litert_gpu(clean_messages)
                else:
                    erreurs.append(f"{nom}: type inconnu « {ltype} »")
                    continue
            except Exception as e:
                erreurs.append(f"{nom}: {type(e).__name__} {e}")
                continue

            if res and not res.startswith("[ERREUR"):
                if forced is None and idx > 0:
                    print(f"\n🔗 [Chaîne Souveraine : « {nom} » a pris le relais ({'; '.join(erreurs)})]")
                return res
            erreurs.append(f"{nom}: {res[:120] if res else 'réponse vide'}")

        return ("[ERREUR CHAÎNE SOUVERAINE : aucun maillon n'a répondu. "
                + " | ".join(erreurs) + "]")

    def _call_openvino_orchestre(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Orchestration locale 100 % OpenVINO : Heimdall (NPU) -> Slot Unique Spécialiste (GPU Arc 140V)."""
        try:
            unif_src = Path(r"C:\Alix\SAUVEGARDE_ALIX\Cerveau Alix\_Unification_Alix\src")
            if unif_src.exists() and str(unif_src) not in sys.path:
                sys.path.insert(0, str(unif_src))
            from alix.substrat.alix_orchestrateur_openvino import get_orchestrateur_openvino, ANCRE_IDENTITE_ALIX_DEFAUT

            raw_sys = ""
            user_turns = []
            react_tail = []
            for m in messages:
                role = m.get("role", "")
                content = m.get("content", "")
                if role == "system":
                    raw_sys = content
                elif role == "user":
                    if not content.startswith("Voici le retour réel du fer"):
                        user_turns.append(content)
                    react_tail.append(("Christian", content))
                elif role == "assistant":
                    react_tail.append(("Alix", content))

            requete_heimdall = user_turns[-1] if user_turns else (react_tail[-1][1] if react_tail else "")

            # Prompt système condensé haute densité pour prefill iGPU Arc 140V ultra-rapide (< 1.5s)
            sys_local = ANCRE_IDENTITE_ALIX_DEFAUT + "\n"
            if "### 🔧 ACTUATEURS" in raw_sys:
                bloc_outils = raw_sys.split("### 🔧 ACTUATEURS", 1)[1]
                sys_local += "\n### 🔧 ACTUATEURS" + bloc_outils[:2200]
            elif raw_sys:
                sys_local += "\n" + raw_sys[:1800]

            # Construction du prompt de tour (incluant le retour d'outil ReAct s'il y en a un)
            if len(react_tail) >= 2 and react_tail[-1][1].startswith("Voici le retour réel du fer"):
                prompt_effectif = (
                    f"Demande initiale de Christian : {requete_heimdall}\n\n"
                    f"Ton appel d'outil précédent :\n{react_tail[-2][1][:600]}\n\n"
                    f"{react_tail[-1][1][:1600]}"
                )
            else:
                prompt_effectif = requete_heimdall

            orch = get_orchestrateur_openvino()
            choix = orch._choisir_via_heimdall(requete_heimdall)
            role_cible = choix.get("specialiste", "PARLER")
            res = orch.generer(
                prompt=prompt_effectif,
                system_prompt=sys_local,
                force_role=role_cible,
                temperature=temperature,
                max_new_tokens=512,
            )
            entete = (
                f"⚡ `[OpenVINO Local · Heimdall NPU -> Slot GPU: {res['slot_utilise']} "
                f"({res['modele']}) · {res['duree_generation_s']}s]`\n\n"
            )
            return entete + res.get("reponse", "")
        except Exception as e:
            return f"[ERREUR OPENVINO ORCHESTRÉ : {e}]"

    def _call_openai_compat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Inférence sur API distante standard."""
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except urllib.error.URLError as e:
            return f"[ERREUR ROUTEUR API COMPATIBLE : Échec de la requête vers {url} ({e})]"
