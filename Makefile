# Run from repo root. Windows without make: run the commands shown after each target manually.
PY ?= python
BENCH = PYTHONPATH=analysis $(PY) -m benchkit

.PHONY: help test lint validate summarize compare figures analyze paper clean devices check install run

help:
	@echo "make test | lint | validate | summarize | compare | figures | analyze | devices | check | install | run | paper | clean"

devices:         ## list and inspect connected ADB devices
	$(BENCH) devices

check:           ## pre-flight check on connected device
	$(BENCH) check

install:         ## deploy release APKs to connected device
	$(BENCH) install

run:             ## execute experiment session (DEVICE=<id> SESSION=<k>)
	$(BENCH) run --device $(DEVICE) --session $(SESSION)

test:            ## unit tests for the analysis pipeline (synthetic fixtures only)
	cd analysis && $(PY) -m pytest -q

lint:
	cd analysis && $(PY) -m ruff check .

validate:        ## schema-check data/raw
	$(BENCH) validate data/raw

summarize: validate
	$(BENCH) summarize data/raw --out data/processed/summary.csv

compare: validate
	$(BENCH) compare data/raw --out data/processed/comparisons.csv

figures: summarize compare
	$(BENCH) figures --summary data/processed/summary.csv --comparisons data/processed/comparisons.csv \
	  --figures paper/figures --tables paper/tables

analyze: figures

paper:           ## needs a TeX distribution with latexmk (or upload paper/ to Overleaf)
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

clean:
	rm -f data/processed/*.csv
	cd paper && latexmk -C || true
