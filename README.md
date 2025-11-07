
# PowerFlow Pack — Option A (Ready-to-Run)

**Contenuto**:
- Core solver Newton–Raphson (H, N, M, L)
- Costruzione Y-bus (modello π, tap, sfasamento)
- Loader **MATPOWER** (`.m` → `Network`)
- Esempio e rete **IEEE14** inclusa
- Script eseguibile: `python examples/run_ieee14.py`

**Aggiungere altre reti (IEEE30/57/118)**:
1. Scarica i file MATPOWER originali (`case30.m`, `case57.m`, `case118.m`).
2. Copiali in `networks/`.
3. Crea uno script come `examples/run_ieee30.py` copiando `run_ieee14.py` e cambiando il nome del file.

**Note**:
- Le convenzioni sono in per-unit sul `baseMVA` del caso.
- Nei PV, i limiti Q sono rispettati convertendo PV→PQ quando necessario.

Riferimenti ai casi MATPOWER: vedere la documentazione ufficiale (Case Reference Pages).
