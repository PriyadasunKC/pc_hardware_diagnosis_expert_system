#!/usr/bin/env python3
"""
PC Hardware Troubleshooting Expert System — Flask Web Interface
Imports from pc_troubleshoot_expert.py WITHOUT modifying it.
"""

import os
import sys
import threading

# Fix Unicode characters that crash on Windows terminals
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import webbrowser
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from pc_troubleshoot_expert import PCTroubleshootingExpert, PCSymptom, BeepCode

# Create the engine once at startup and reuse it for all requests
_lock = threading.Lock()
_engine = PCTroubleshootingExpert()

VALID_PATTERNS = {
    "1_short", "continuous", "1_long_2_short",
    "1_long_3_short", "3_short", "2_short",
}

VALID_SYMPTOMS = {
    "no_display", "no_power", "fans_running", "no_lights",
    "random_shutdown", "system_hot", "slow_boot", "disk_noise",
    "blue_screen", "memory_errors", "random_restart", "power_fluctuation",
}

# Initialize Flask app with CORS support
app = Flask(__name__)
CORS(app)


def _run(facts):
    """Reset engine, declare facts, run inference, return report."""
    with _lock:
        _engine.reset()
        _engine.diagnosis = []
        _engine.solutions = []
        _engine.confidence_level = 0
        for kind, value in facts:
            if kind == "symptom":
                _engine.declare(PCSymptom(issue=value))
            elif kind == "beep":
                _engine.declare(BeepCode(pattern=value))
        _engine.run()
        return _engine.get_diagnosis_report()


# API Routes

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    with _lock:
        facts = len(_engine.prolog.facts)
    return jsonify({"status": "ok", "kb_facts": facts})


@app.route("/api/diagnose/beep", methods=["POST"])
def diagnose_beep():
    data = request.get_json(force=True, silent=True) or {}
    pattern = data.get("pattern", "")
    if pattern not in VALID_PATTERNS:
        return jsonify({"error": f"Invalid pattern '{pattern}'"}), 400
    try:
        return jsonify(_run([("beep", pattern)]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diagnose/symptoms", methods=["POST"])
def diagnose_symptoms():
    data = request.get_json(force=True, silent=True) or {}
    symptoms = [s for s in data.get("symptoms", []) if s in VALID_SYMPTOMS]
    if not symptoms:
        return jsonify({"error": "No valid symptoms provided"}), 400
    try:
        return jsonify(_run([("symptom", s) for s in symptoms]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diagnose/auto", methods=["POST"])
def diagnose_auto():
    data = request.get_json(force=True, silent=True) or {}
    pc_on       = data.get("pc_on", True)
    has_display = data.get("has_display", True)
    fans        = data.get("fans_running", False)
    beep_pat    = data.get("beep_pattern") or None

    facts = []
    if not pc_on:
        facts += [("symptom", "no_power"), ("symptom", "no_lights")]
    else:
        if not has_display:
            facts.append(("symptom", "no_display"))
        if fans:
            facts.append(("symptom", "fans_running"))
        if beep_pat and beep_pat in VALID_PATTERNS:
            facts.append(("beep", beep_pat))

    if not facts:
        return jsonify({"error": "No diagnostic data — answer at least one question"}), 400
    try:
        return jsonify(_run(facts))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge-base")
def knowledge_base():
    with _lock:
        stats = {
            "total_predicates": len(_engine.prolog.facts),
            "total_rules":      len(_engine.prolog.rules),
        }
    return jsonify({
        "stats": stats,
        "ami_bios_beeps": [
            {"pattern": "1 short",    "meaning": "System OK / Normal POST"},
            {"pattern": "2 short",    "meaning": "Parity circuit failure"},
            {"pattern": "3 short",    "meaning": "Base 64K RAM failure"},
            {"pattern": "Continuous", "meaning": "Memory or video problem"},
        ],
        "award_bios_beeps": [
            {"pattern": "1 long, 2 short",    "meaning": "Video card error"},
            {"pattern": "1 long, 3 short",    "meaning": "Video card not detected"},
            {"pattern": "Continuous high",    "meaning": "CPU overheating"},
            {"pattern": "Repeating high/low", "meaning": "CPU issue"},
        ],
        "common_issues": [
            {"issue": "No Display",       "check": "Check cables, RAM, GPU"},
            {"issue": "No Power",         "check": "Check PSU, motherboard connections"},
            {"issue": "Overheating",      "check": "Clean fans, replace thermal paste"},
            {"issue": "Random Crashes",   "check": "Test RAM, check PSU"},
            {"issue": "Slow Performance", "check": "Check HDD/SSD health"},
        ],
    })


# Run the server
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("   PC HARDWARE DIAGNOSIS EXPERT SYSTEM")
    print("   Flask + Prolog Knowledge Base + Experta")
    print("=" * 55)
    print(f"\n   KB loaded  : {len(_engine.prolog.facts)} predicates")
    print(f"   Server     : http://localhost:5000")
    print(f"   Press Ctrl+C to stop\n" + "-" * 55)
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
