.DEFAULT_GOAL := help

.PHONY: check-env help stats preprocess experiments train report api all clean

check-env:
	@uv --version > /dev/null 2>&1 || (echo "ERROR: uv is not installed. Install it from https://docs.astral.sh/uv/" && exit 1)

help:
	@echo "Available targets:"
	@echo "  stats"
	@echo "  preprocess"
	@echo "  experiments"
	@echo "  train"
	@echo "  report"
	@echo "  api"
	@echo "  all"
	@echo "  clean"

stats: check-env
	uv run python -m src.stats

preprocess: stats
	uv run python -m src.preprocess

experiments: preprocess
	uv run python -m src.experiments

train: experiments
	uv run python -m src.train

report: train
	uv run python -m src.report

api: check-env
	uv run uvicorn backend.app:app --reload

all: report

clean: check-env
	uv run python -m src.clean


.PHONY: dev

dev: check-env
	uv run python -m src.dev
