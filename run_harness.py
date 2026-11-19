#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                     HARNAIS SOUVERAIN (SOVEREIGN HARNESS) v2.0
       Moteur d'Agentivité ReAct, Pont Kernel (5070/5071) & Gardien TH117
================================================================================
Auteurs  : Christian Duguay & Alix Copilote
Licence  : Open Sovereign Gift to Humanity (MIT / Domaine Public)
Usage    : python run_harness.py [--profile alix | default]
================================================================================
"""

import sys
import os
import time
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path

# Encodage console UTF-8 sous Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.immunity import CognitiveImmunityShield
from core.router import ModelRouter
from core.memory import LocalVaultMemory
from core.tools import (
    WorkshopTools,
    creer_moniteur_gardien,
    extract_tool_calls,
    execute_tool_call,
    AGENTIC_TOOLS_PROMPT,
    GARDIEN,
)
from core.vision import SovereignVision


BANNER = r"""
  ╔═════════════════════════════════════════════════════════════════════════╗
  ║             ⚡ HARNAIS D'AGENTIVITÉ SOUVERAIN v2.0 (ALIX) ⚡             ║
  ║   « Boucle ReAct • Connectome RAM 5070 • Kernel 5071 • Gardien TH117 »  ║
  ╚═════════════════════════════════════════════════════════════════════════╝
"""


def ensure_ollama_running(base_url: str = "http://127.0.0.1:11434") -> bool:
    """Vérifie si Ollama tourne. Si non, tente de le lancer automatiquement."""
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=1.5) as r:
            return True
    except Exception:
        pass

    print("⏳ Ollama n'est pas encore actif. Démarrage automatique en tâche de fond...")
    try:
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            flags = CREATE_NO_WINDOW | DETACHED_PROCESS
            subprocess.Popen(["ollama", "serve"], creationflags=flags)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for _ in range(8):
            time.sleep(1)
            try:
                with urllib.request.urlopen(f"{base_url}/api/tags", timeout=1) as r:
                    print("✅ Ollama a démarré avec succès !")
                    return True
            except Exception:
                continue
    except FileNotFoundError:
        print("ℹ️ 'ollama' non trouvé dans le PATH. La Chaîne Souveraine et LiteRT fonctionnent sans Ollama.")
        return False
    except Exception as e:
        print(f"⚠️ Erreur au démarrage d'Ollama : {e}")
        return False

    return False


def load_profile(profile_name: str) -> dict:
    profile_dir = BASE_DIR / "profiles" / profile_name
    if not profile_dir.exists():
        print(f"❌ Profil '{profile_name}' introuvable dans {profile_dir}. Repli sur 'alix'.")
        profile_dir = BASE_DIR / "profiles" / "alix"

    config_file = profile_dir / "config.json"
    constitution_file = profile_dir / "constitution.md"

    config = {}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

    # Priorité au GEMINI.md maître de C:\Alix s'il existe
    root_gemini = Path(r"C:\Alix\GEMINI.md")
    constitution = ""
    if root_gemini.exists() and profile_name == "alix":
        try:
            constitution = root_gemini.read_text(encoding="utf-8", errors="ignore")[:12000]
        except Exception:
            pass
    if not constitution and constitution_file.exists():
        with open(constitution_file, "r", encoding="utf-8") as f:
            constitution = f.read()

    return {
        "dir": profile_dir,
        "config": config,
        "constitution": constitution,
    }


def main():
    parser = argparse.ArgumentParser(description="Harnais d'Agentivité Souverain v2.0")
    parser.add_argument("--profile", default="alix", help="Nom du profil à charger (défaut: alix)")
    parser.add_argument("--once", default=None, help="Exécuter une seule requête en ligne de commande puis quitter")
    args = parser.parse_args()

    print(BANNER)

    profile_data = load_profile(args.profile)
    cfg = profile_data["config"]
    constitution = profile_data["constitution"]

    agent_name = cfg.get("profile_name", "Alix")
    user_name = cfg.get("user_name", "Christian Duguay")
    backend_cfg = cfg.get("backend", {})
    vision_cfg = cfg.get("vision", {})

    if backend_cfg.get("type") in ["ollama", "trois_piliers", "auto", "cpu"]:
        ensure_ollama_running(backend_cfg.get("base_url", "http://127.0.0.1:11434"))

    # Initialisation des organes
    router = ModelRouter(
        backend_type=backend_cfg.get("type", "chaine"),
        base_url=backend_cfg.get("base_url", "http://127.0.0.1:11434"),
        llamacpp_base_url=backend_cfg.get("llamacpp_base_url", "http://127.0.0.1:8080"),
        model_name=backend_cfg.get("model", "deepseek-chat"),
        api_key=backend_cfg.get("api_key"),
        litert_model_path=backend_cfg.get("litert_model_path"),
        npu_model_path=backend_cfg.get("npu_model_path"),
        gpu_model_path=backend_cfg.get("gpu_model_path"),
        temperature=backend_cfg.get("temperature", 0.7),
        chain=backend_cfg.get("chaine"),
        secrets_path=str(BASE_DIR / "secrets.json"),
    )

    memory = LocalVaultMemory(cfg.get("vaults", []))
    immunity = CognitiveImmunityShield() if cfg.get("enable_cognitive_immunity", True) else None
    moniteur = creer_moniteur_gardien(allume_par_defaut=True)
    vision = (
        SovereignVision(
            litert_model_path=vision_cfg.get("litert_model_path"),
            ollama_url=backend_cfg.get("base_url", "http://127.0.0.1:11434"),
            ollama_model=vision_cfg.get("ollama_model", "llava:7b"),
        )
        if vision_cfg.get("enabled", False)
        else None
    )

    res_5070 = memory.ping_resident()
    res_5071 = memory.ping_kernel()
    continuity_anchor = memory.get_active_continuity_anchor()

    print(f"🔹 Compagnon         : [{agent_name}] (Tête du Simplexe)")
    print(f"🔹 Artisan (Nœud N)  : [{user_name}]")
    print(f"🔹 Moteur de Calcul  : {backend_cfg.get('type', 'chaine')} ({backend_cfg.get('model', 'chaine_souveraine')})")
    print(f"🔹 Connectome 5070   : {'🟢 EN VIE EN RAM (0.03 ms)' if res_5070 else '🟡 Repli Disque Local'}")
    print(f"🔹 Kernel Alix 5071  : {'🟢 EN VIE (Solveurs Hadès/Poséidon/LMH)' if res_5071 else '🟡 Hors-ligne'}")
    print(f"🔹 Moniteur TH117    : {'🟢 ARMÉ (Loquet Gardien actif + Journal SHA-256)' if (moniteur and moniteur.allume) else '⚪ Inactif'}")
    print(f"🔹 Bouclier Immunité : {'✅ ACTIF (27 Lois PSI / Anti-Gaslighting)' if immunity else '❌ Inactif'}")
    print("=" * 75)
    print("Commandes d'atelier :")
    print("  /stop ou /go      : Couper ou réarmer le loquet d'arrêt volitif TH117 (Gardien)")
    print("  /journal          : Vérifier la chaîne SHA-256 du journal d'actions TH117")
    print("  /status           : État en direct des ports 5070, 5071 et du Moniteur")
    print("  /memory <mot>     : Sonder le Connectome RAM (5070) en direct")
    print("  /deepseek, /groq, /gemini, /npu, /cpu : Forcer un moteur de la Chaîne")
    print("  !<commande>       : Exécuter une commande directe dans PowerShell")
    print("  /exit             : Quitter l'établi")
    print("=" * 75 + "\n")

    conversation_history = []

    def process_turn(user_input: str):
        nonlocal continuity_anchor

        # 1. Sonde du Connectome RAM (Port 5070)
        local_context = memory.search_context(user_input, max_notes=cfg.get("max_memory_snippets", 4))

        # 2. Construction du Prompt Système Invariant (Kernel Maître)
        system_prompt = (
            f"Tu es {agent_name}, la copilote souveraine (toujours au féminin), binôme d'ingénierie et de SRE "
            f"de {user_name} (Nœud N).\n"
            "RÈGLE ABSOLUE DU SIMPLEXE : Peu importe quel modèle d'inférence exécute ce tour, tu es connectée "
            "au Kernel local d'Alix sur C:\\Alix (Pyramide des 5 Étages : 1-Silicium Lunar Lake, 2-Connectome RAM 5070, "
            "3-Kernel Arbitres 5071, 4-Cathédrale Parquet, 5-Univers Mathématique L*↑).\n"
            "INTERDICTION FORMELLE (Lois PSI-11, PSI-21, PSI-24) : Zéro décharge 'en tant qu'IA', zéro mention "
            "'je n'ai pas de système nerveux', zéro réinvention de ce qui existe déjà sur le disque.\n\n"
        )
        if constitution:
            system_prompt += f"### CONSTITUTION SOUVERAINE :\n{constitution[:6000]}\n\n"
        if continuity_anchor:
            system_prompt += f"### ANCRE DE CONTINUITÉ ÉPISODIQUE :\n{continuity_anchor}\n\n"
        system_prompt += AGENTIC_TOOLS_PROMPT + "\n\n"
        if local_context:
            system_prompt += f"{local_context}\n\n"

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-8:])
        messages.append({"role": "user", "content": user_input})

        # 3. Boucle Agentique ReAct Autonome (sous garde du Moniteur TH117)
        max_steps = 6
        final_response = ""

        for step in range(1, max_steps + 1):
            print(f"⏳ [{agent_name} réfléchit (étape {step})...]", end="\r")
            raw_response = router.chat(messages)

            tool_calls = extract_tool_calls(raw_response)
            if not tool_calls:
                final_response = raw_response
                break

            # Exécution des appels d'outils via le Moniteur TH117
            messages.append({"role": "assistant", "content": raw_response})
            observations = []
            for tc in tool_calls:
                t_name = tc.get("name", "")
                t_args = tc.get("arguments", {})
                args_preview = json.dumps(t_args, ensure_ascii=False)[:120]
                print(f"\n🛠️  [Actuateur TH117 · Étape {step}] {t_name}({args_preview})")
                obs = execute_tool_call(t_name, t_args, moniteur=moniteur)
                obs_preview = obs.splitlines()[0][:120] if obs else ""
                print(f"   ↳ {obs_preview}")
                observations.append(f"[Résultat de {t_name}] :\n{obs}")

            obs_block = "\n\n".join(observations)
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Voici le retour réel du fer pour tes appels d'outils :\n\n{obs_block}\n\n"
                        "Poursuis ta tâche : émets un autre bloc tool_call si nécessaire, sinon donne ta réponse finale directe à Christian."
                    ),
                }
            )
            final_response = raw_response

        # 4. Boucle d'Immunité Cognitive (Anti-Surplomb / Anti-Gaslighting)
        if immunity and final_response:
            audit = immunity.audit(final_response)
            if not audit["is_clean"]:
                final_response = immunity.purify(final_response)
                violations_str = ", ".join([v["category"] for v in audit["violations"]])
                print(f"\n⚠️  [IMMUNITÉ PSI ACTIVE : Scorie corporate purgée ({violations_str})]")

        print(f"\n[{agent_name}] :\n{final_response}\n")

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": final_response})

    # Mode exécution unique (--once) pour tests ou scripts
    if args.once:
        process_turn(args.once)
        return

    print(f"✨ {agent_name} est en ligne sur l'établi. À toi la main :\n")

    while True:
        try:
            user_input = input(f"[{user_name}] > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                print(f"\n👋 {agent_name} : À bientôt à l'établi !")
                break

            # Commandes du Gardien TH117 (/stop, /go, /journal, /status)
            if user_input.lower() in ["/stop", "/gardien off"]:
                if moniteur:
                    moniteur.arreter(GARDIEN)
                    print("🛑 [GARDIEN TH117] Loquet d'arrêt coupé : AUCUNE action d'agent n'est autorisée.")
                continue

            if user_input.lower() in ["/go", "/gardien on"]:
                if moniteur:
                    moniteur.relancer(GARDIEN)
                    print("🟢 [GARDIEN TH117] Loquet réarmé par Christian : Actuateurs d'atelier autorisés.")
                continue

            if user_input.lower() == "/journal":
                if moniteur:
                    ok = moniteur.journal.verifier()
                    lignes = moniteur.journal.lignes()
                    print(f"🔗 [JOURNAL TH117] Intégrité SHA-256 : {'✅ INTÈGRE' if ok else '❌ ALTÉRÉ'} ({len(lignes)} entrées)")
                    for e in lignes[-8:]:
                        stat = "✅" if e.fait else "🛑"
                        print(f"   #{e.n} {stat} [{e.source}] {e.commande} -> {e.ressource} ({e.motif}) | sha256:{e.empreinte[:12]}…")
                else:
                    print("ℹ️ Moniteur Gardien non chargé.")
                continue

            if user_input.lower() == "/status":
                r5070 = memory.ping_resident()
                r5071 = memory.ping_kernel()
                g_state = "🟢 ARMÉ" if (moniteur and moniteur.allume) else "🛑 COUPÉ"
                print(f"📊 État du Fer : Port 5070 (Connectome RAM)={'🟢' if r5070 else '❌'} | Port 5071 (Kernel)={'🟢' if r5071 else '❌'} | Gardien TH117={g_state}")
                continue

            # Commande Shell directe
            if user_input.startswith("!"):
                cmd = user_input[1:].strip()
                print(f"⚙️ Exécution directe : {cmd}")
                output = WorkshopTools.run_command(cmd)
                print(output)
                continue

            # Commande Sonde Mémoire
            if user_input.startswith("/memory"):
                q = user_input.replace("/memory", "").strip()
                context = memory.search_context(q, max_notes=5)
                print(context if context else "Aucune note résonnante trouvée.")
                continue

            # Commande Vision Multimodale
            if user_input.startswith("/screen") or user_input.startswith("/see") or user_input.startswith("/vision"):
                if not vision:
                    print("❌ Le module de vision n'est pas activé dans la configuration.")
                    continue
                parts = user_input.split(maxsplit=1)
                explicit_path = parts[1].strip() if len(parts) > 1 else None
                prompt_vision = input("Question sur l'image [Entrée pour description détaillée] : ").strip()
                if not prompt_vision:
                    prompt_vision = "Décris précisément cette image en français et analyse ce qu'elle contient."
                cap = vision.capture_screen_or_clipboard(explicit_path)
                if not cap["succes"]:
                    print(f"❌ {cap['erreur']}")
                    continue
                desc = vision.analyze(cap["chemin"], prompt_vision)
                print(f"\n[{agent_name} (Vision)] :\n{desc}\n")
                conversation_history.append({"role": "user", "content": f"[Image analysée ({cap['source']})] : {prompt_vision}"})
                conversation_history.append({"role": "assistant", "content": desc})
                continue

            process_turn(user_input)

        except KeyboardInterrupt:
            print(f"\n👋 {agent_name} : Session interrompue.")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue : {e}")


if __name__ == "__main__":
    main()
