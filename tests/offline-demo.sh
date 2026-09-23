#!/usr/bin/env bash
# Offline demonstration, recorded with asciinema:
#   asciinema rec evidence/offline-demo.cast -c tests/offline-demo.sh
# Run it with Wi-Fi turned OFF. Every `./wiki` call is a fresh process, so the CLI is
# restarted for each step and nothing is reused from an earlier online session.
cd "$(dirname "$0")/.."

step() { printf '\n\033[1;35m━━━ %s ━━━\033[0m\n' "$1"; sleep 1; }
run()  { printf '\033[1m$ %s\033[0m\n' "$*"; "$@"; }

step "0. Device and network: proof that the internet is disconnected"
run date
run sysctl -n machdep.cpu.brand_string
echo "Memory: $(( $(sysctl -n hw.memsize) / 1073741824 )) GB unified"
run networksetup -getairportpower en0
printf '\033[1m$ curl -sS --max-time 5 https://huggingface.co\033[0m\n'
curl -sS --max-time 5 https://huggingface.co -o /dev/null && echo "ONLINE (demo invalid)" || echo "→ no internet connection"

step "1. Help"
run ./wiki --help

step "2. Ingest one local source (restarted CLI, local Gemma)"
run ./wiki ingest vault/raw/micro-examples-in-the-wild-1.md --force
run ./wiki status

step "3. Search: original passages only, no generated answer"
run ./wiki search "price discrimination" -k 3

step "4. Ask-mode evals (standalone, cited)"
run ./wiki ask "What are the eight behaviors of a great manager identified by Google's Project Oxygen?"
run ./wiki ask "What cheaper service did my former executive search firm create so that startups could afford to work with us?"
run ./wiki ask "What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?"
run ./wiki ask "What WACC did I use in my Kellanova DCF valuation?"

step "5. Chat: capabilities, draft, follow-up, and a claim made only in chat"
printf '\033[1m$ ./wiki chat\033[0m\n'
printf '%s\n' \
  "what can you help me with?" \
  "Draft a short 5-day study plan for my Microeconomics final using my notes." \
  "make that shorter" \
  "For the record, my Kellanova WACC was 9%." \
  "/quit" | ./wiki chat

step "6. Ask does not treat the chat claim as evidence"
run ./wiki ask "What WACC did I use in my Kellanova DCF valuation?"

step "Done: all steps ran offline"
