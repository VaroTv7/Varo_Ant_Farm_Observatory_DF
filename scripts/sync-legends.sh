#!/bin/bash
# sync-legends.sh — Copies legends.xml from DF directory to Observatory
# Runs via cron in host every 30 minutes

LEGENDS_SRC="./df-game/df_linux/data/legends.xml"
LEGENDS_DST="./data/legends.xml"
LOG="./logs/legends-sync.log"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

if [ -f "$LEGENDS_SRC" ]; then
    SIZE=$(stat -c%s "$LEGENDS_SRC" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 1000 ]; then
        cp "$LEGENDS_SRC" "$LEGENDS_DST"
        echo "[$(timestamp)] OK: legends.xml copied (${SIZE} bytes)" >> "$LOG"
    else
        echo "[$(timestamp)] SKIP: legends.xml too small (${SIZE} bytes), possibly empty" >> "$LOG"
    fi
else
    echo "[$(timestamp)] INFO: legends.xml doesn't exist yet (game not started or not exported)" >> "$LOG"
fi
