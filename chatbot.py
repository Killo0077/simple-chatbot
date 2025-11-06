# CHATBOT .PY
cat > chatbot.py <<'PY'
#!/usr/bin/env python3
import json, re
from datetime import datetime
from pathlib import Path

INTENTS_PATH = Path(__file__).with_name("intents.json")
HISTORY_PATH = Path(__file__).with_name("history.log")

def load_intents():
    if not INTENTS_PATH.exists():
        default = {"intents":[
            {"tag":"greet","keywords":["hello","hi","hey","yo","sup"],"responses":["Hi! 👋","Hey there!","Hello!"]},
            {"tag":"bye","keywords":["bye","goodbye","see ya","cya"],"responses":["Bye! 👋","See you later.","Take care!"]},
            {"tag":"thanks","keywords":["thanks","thank you","thx"],"responses":["You're welcome!","Anytime!","No problem."]},
            {"tag":"name","keywords":["your name","who are you","what are you"],"responses":["I'm a tiny console chatbot. 🤖"]},
            {"tag":"help","keywords":["help","commands"],"responses":["Type anything! Commands: /help, /history, /train, /intents, /exit"]}
        ]}
        INTENTS_PATH.write_text(json.dumps(default, indent=2))
    return json.loads(INTENTS_PATH.read_text(encoding="utf-8"))

def save_intents(data): INTENTS_PATH.write_text(json.dumps(data, indent=2))

def normalize(text:str)->list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())

def score(user_tokens, intent_keywords):
    kw = []
    for k in intent_keywords: kw += normalize(k)
    return sum(1 for t in user_tokens if t in kw)

def best_intent(user_input, intents):
    tokens = normalize(user_input)
    best, best_s = None, 0
    for intent in intents["intents"]:
        s = score(tokens, intent.get("keywords", []))
        if s > best_s: best, best_s = intent, s
    return best, best_s

def respond(intent):
    import random
    return random.choice(intent.get("responses", ["..."]))

def log(user, bot):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] USER: {user}\n[{ts}] BOT : {bot}\n")

def cmd_help():
    return ("Commands:\n"
            "  /help    - show this help\n"
            "  /history - last 20 lines\n"
            "  /intents - list intent tags\n"
            "  /train   - add a new intent\n"
            "  /exit    - quit")

def cmd_history():
    if not HISTORY_PATH.exists(): return "No history yet."
    return "\n".join(HISTORY_PATH.read_text(encoding="utf-8").splitlines()[-20:])

def cmd_intents(intents): return "Intents: " + ", ".join(i["tag"] for i in intents["intents"])

def cmd_train(intents):
    print("Training wizard 🧠  (Enter to cancel)")
    tag = input("New intent tag: ").strip()
    if not tag: return "Cancelled."
    kws = input("Keywords (comma-separated): ").strip()
    resps = input("Responses (comma-separated): ").strip()
    intents["intents"].append({
        "tag": tag,
        "keywords": [k.strip() for k in kws.split(",") if k.strip()],
        "responses": [r.strip() for r in resps.split(",") if r.strip()],
    })
    save_intents(intents)
    return f"Added '{tag}'."

def main():
    intents = load_intents()
    print("Tiny Chatbot 🤖 — type /help for commands. Ctrl+C or /exit to quit.")
    while True:
        try: user = input("> ").strip()
        except (EOFError, KeyboardInterrupt): print("\nBye!"); break
        if not user: continue
        if user == "/help": bot = cmd_help()
        elif user == "/history": bot = cmd_history()
        elif user == "/intents": bot = cmd_intents(intents)
        elif user == "/train": bot = cmd_train(intents)
        elif user == "/exit": print("Bye!"); break
        else:
            intent, s = best_intent(user, intents)
            bot = respond(intent) if intent and s>0 else "I didn't catch that. Try /help or /train me."
        print(bot); log(user, bot)

if __name__ == "__main__": main()
PY
