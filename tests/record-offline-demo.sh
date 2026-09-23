#!/usr/bin/env bash
# One command for the offline demonstration. Turn Wi-Fi OFF first, then run:
#   ./tests/record-offline-demo.sh
# It refuses to run while online, records the terminal demo (asciinema), runs the
# eval script, and renders evidence/offline-demo.gif. Takes about 5 minutes.
set -e
cd "$(dirname "$0")/.."

if curl -sS --max-time 5 https://huggingface.co -o /dev/null 2>/dev/null; then
  echo "You are still online. Turn Wi-Fi off (menu bar → Wi-Fi → off) and run this again."
  exit 1
fi
echo "Offline confirmed. Recording the demo (about 3 minutes)…"
mkdir -p evidence
asciinema rec --overwrite -q --cols 110 --rows 32 \
  -t "Personal wiki CLI: offline demo" evidence/offline-demo.cast -c tests/offline-demo.sh

echo "Running the eval script offline (about 2 minutes)…"
HF_HUB_OFFLINE=1 .venv/bin/python -W ignore -m tests.run_evals | tee evidence/offline-evals.log

echo "Rendering the GIF…"
agg --speed 1 --idle-time-limit 4 --last-frame-duration 6 evidence/offline-demo.cast evidence/offline-demo.gif
echo
echo "Done. You can turn Wi-Fi back on and tell Claude the recording is finished."
