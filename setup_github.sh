#!/bin/bash
# ============================================================
# GitHub repo setup voor Zigbee Battery Monitor
# Voer dit uit vanuit je lokale map: github/ZigbeeBatteryMonitor
# ============================================================

# 1. Git initialiseren (als dat nog niet gedaan is)
git init

# 2. Koppel aan jouw GitHub repo
git remote add origin https://github.com/joohann/ZigbeeBatteryMonitor.git

# 3. Zorg dat je op de main branch zit
git branch -M main

# 4. Alles toevoegen
git add .

# 5. Eerste commit
git commit -m "feat: initial release v1.0.0 - Zigbee Battery Monitor HACS integration"

# 6. Push naar GitHub
git push -u origin main

echo ""
echo "✅ Klaar! Je repo is live op:"
echo "   https://github.com/joohann/ZigbeeBatteryMonitor"
echo ""
echo "📦 Volgende stap: HACS release aanmaken"
echo "   Ga naar: https://github.com/joohann/ZigbeeBatteryMonitor/releases/new"
echo "   Tag: v1.0.0"
echo "   Title: v1.0.0 - Initial Release"
