import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from xinliflow.voicestudio import VoiceStudioClient

c = VoiceStudioClient()
print("health:")
print(json.dumps(c.health(), ensure_ascii=False, indent=2))
print("\nvoices:")
print(json.dumps(c.voices(), ensure_ascii=False, indent=2))
