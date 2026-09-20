# PACT - canonical commands. `make help` lists them. Windows: use WSL2.
SHELL := /bin/bash
.DEFAULT_GOAL := help

PY      ?= python3.12
VENV    ?= .venv
BIN     := $(VENV)/bin
STACK   ?= pact-dev
REGION  ?= us-east-1
LOCAL_PROFILE ?= ddb
LOCAL_API ?= http://127.0.0.1:3000
API     ?= $(shell $(BIN)/python scripts/stack_output.py ApiUrl --stack $(STACK) --region $(REGION) 2>/dev/null)
BACKEND ?= bedrock
MODEL   ?= nova-2-lite
K       ?= 4
N       ?= 20
SMOKE_ARGS ?=

ifeq ($(LOCAL_PROFILE),localstack)
LOCAL_ENV := env.localstack.json
else
LOCAL_ENV := env.local.json
endif

.PHONY: help doctor setup test test-backend test-frontend lint fmt build deploy web-env web-bootstrap web-deploy \
        smoke local-up local-down local-api local-smoke cedar-demo imu-demo shapes viz bench report logs

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

doctor: ## Check toolchain, Docker and AWS access
	@bash scripts/doctor.sh

setup: ## Create .venv, install backend dev deps and frontend deps
	test -d $(VENV) || $(PY) -m venv $(VENV)
	$(BIN)/pip install -q -U pip
	$(BIN)/pip install -q -r backend/requirements-dev.txt
	cd frontend && npm install

test: test-backend test-frontend ## Run all unit tests

test-backend: ## Backend + policy + generator tests (pytest)
	$(BIN)/python -m pytest -q backend/tests

test-frontend: ## Frontend unit tests (vitest)
	cd frontend && npx vitest run

lint: ## ruff + eslint + TypeScript typecheck
	$(BIN)/ruff check backend redteam scripts
	$(BIN)/ruff format --check backend redteam scripts
	cd frontend && npm run lint && npx tsc -b

fmt: ## Auto-format Python
	$(BIN)/ruff format backend redteam scripts
	$(BIN)/ruff check --fix backend redteam scripts

build: ## sam validate --lint + sam build
	cd backend && sam validate --lint && sam build

deploy: build ## Deploy backend stack, then refresh frontend env files
	cd backend && sam deploy
	$(BIN)/python scripts/write_frontend_env.py --stack $(STACK) --region $(REGION)

web-bootstrap: ## One-time: create Amplify app + branch, patch CORS origins in samconfig.toml
	$(BIN)/python scripts/bootstrap_amplify.py --region $(REGION)

web-env: ## Write frontend/.env.*.local from stack outputs
	$(BIN)/python scripts/write_frontend_env.py --stack $(STACK) --region $(REGION)

web-deploy: ## Build frontend and publish to Amplify Hosting
	$(BIN)/python scripts/deploy_frontend.py --region $(REGION)

smoke: ## End-to-end smoke test against the deployed API (SMOKE_ARGS=--no-agent to skip step 10)
	$(BIN)/python scripts/smoke.py --api "$(API)" --stack $(STACK) --region $(REGION) $(SMOKE_ARGS)

local-up: ## Start local data plane (LOCAL_PROFILE=ddb|localstack) and create the table
	docker compose -f local/docker-compose.yml --profile $(LOCAL_PROFILE) up -d
	$(BIN)/python scripts/local_bootstrap.py --profile $(LOCAL_PROFILE)

local-down: ## Stop local data plane
	docker compose -f local/docker-compose.yml --profile ddb --profile localstack down

local-api: ## Serve the API on :3000 with sam local (run local-up first)
	cd backend && sam build && sam local start-api --port 3000 --docker-network pact-local --env-vars $(LOCAL_ENV) --warm-containers LAZY

local-smoke: ## Smoke test against sam local
	$(BIN)/python scripts/smoke.py --api $(LOCAL_API) --local --profile $(LOCAL_PROFILE)

cedar-demo: ## Print the Cedar decision table (offline)
	$(BIN)/python scripts/cedar_demo.py

imu-demo: ## Phone-tilt (imu-v1) attack table: offline, or against the API with IMU_API=<url>
	$(BIN)/python scripts/imu_attack_demo.py $(if $(IMU_API),--api $(IMU_API),)

shapes: ## Regenerate frontend/src/lib/shapes.ts from the generator geometry
	$(BIN)/python scripts/gen_shapes_ts.py backend/layers/core/pact_core frontend/src/lib/shapes.ts

viz: ## Render docs/assets/screenshot-vs-motion.png
	$(BIN)/python scripts/make_viz.py --out docs/assets/screenshot-vs-motion.png

bench: ## Red-team benchmark: make bench BACKEND=bedrock|ollama MODEL=<alias> K=4 N=20 [API=...]
	$(BIN)/python -m redteam.bench --api "$(API)" --backend $(BACKEND) --model $(MODEL) --frames $(K) --n $(N)

report: ## Rebuild eval/report.md from eval/results/*.jsonl and live /v1/stats
	$(BIN)/python -m redteam.report --api "$(API)"

logs: ## Tail authorizer logs (Cedar decisions)
	cd backend && sam logs -n AuthorizerFunction --stack-name $(STACK) --region $(REGION) --tail
