#!/usr/bin/env bash
# PACT toolchain doctor. Prints OK / MISSING / WARN for everything the build needs. Never modifies anything.
set -u
fail=0
ok()   { printf "  \033[32mOK\033[0m      %-22s %s\n" "$1" "$2"; }
bad()  { printf "  \033[31mMISSING\033[0m %-22s %s\n" "$1" "$2"; fail=1; }
warn() { printf "  \033[33mWARN\033[0m    %-22s %s\n" "$1" "$2"; }
ver_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]; }   # ver_ge have need

echo "PACT doctor"
command -v git >/dev/null && ok git "$(git --version)" || bad git "install git"

if command -v python3.12 >/dev/null; then ok python3.12 "$(python3.12 --version)";
else bad python3.12 "install Python 3.12 (brew install python@3.12 / pyenv / uv python install 3.12)"; fi

if command -v node >/dev/null; then
  v=$(node --version | sed 's/^v//'); if ver_ge "$v" "20.19.0"; then ok node "v$v"; else bad node "v$v found; need >= 20.19 (Node 22 LTS recommended)"; fi
else bad node "install Node 22 LTS"; fi
command -v npm >/dev/null && ok npm "$(npm --version)" || bad npm "comes with Node"

if command -v docker >/dev/null; then
  if docker info >/dev/null 2>&1; then ok docker "$(docker --version | cut -d, -f1) (daemon running)";
  else bad docker "installed but daemon not running - start Docker Desktop"; fi
  docker compose version >/dev/null 2>&1 && ok "docker compose" "$(docker compose version --short 2>/dev/null)" || bad "docker compose" "need Compose v2"
else bad docker "install Docker Desktop (needed for sam build --use-container and sam local)"; fi

if command -v aws >/dev/null; then
  av=$(aws --version 2>&1 | awk '{print $1}' | cut -d/ -f2)
  case "$av" in 2.*) ok "aws cli" "$av";; *) bad "aws cli" "$av found; need v2";; esac
  if ident=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null); then ok "aws credentials" "$ident";
  else bad "aws credentials" "run: aws configure  (or aws sso login) - region us-east-1"; fi
  region=$(aws configure get region 2>/dev/null || true)
  [ "${AWS_REGION:-${AWS_DEFAULT_REGION:-$region}}" = "us-east-1" ] && ok "aws region" "us-east-1" \
    || warn "aws region" "'${AWS_REGION:-${AWS_DEFAULT_REGION:-$region}}' - PACT deploys to us-east-1 (samconfig pins it)"
else bad "aws cli" "install AWS CLI v2"; fi

if command -v sam >/dev/null; then
  sv=$(sam --version | awk '{print $4}'); if ver_ge "$sv" "1.100.0"; then ok "sam cli" "$sv"; else bad "sam cli" "$sv found; need >= 1.100"; fi
else bad "sam cli" "install AWS SAM CLI (brew install aws-sam-cli)"; fi

if command -v ollama >/dev/null; then
  if ollama list >/dev/null 2>&1; then ok ollama "$(ollama --version 2>/dev/null | tail -1)";
  else warn ollama "installed but server not running - run: ollama serve"; fi
else warn ollama "optional (Build It local red-team): https://ollama.com/download"; fi

command -v gh >/dev/null && ok gh "$(gh --version | head -1)" || warn gh "optional (create/push the public repo from CLI)"
[ -n "${LOCALSTACK_AUTH_TOKEN:-}" ] && ok "localstack token" "set" || warn "localstack token" "optional - without it use LOCAL_PROFILE=ddb (DynamoDB Local)"

if [ "$fail" -ne 0 ]; then echo "doctor: fix the MISSING items above"; exit 1; fi
echo "doctor: all required tools present"
