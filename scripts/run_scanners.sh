#!/usr/bin/env bash
set -u
mkdir -p reports
# Preserve honest tool outputs; findings are expected and belong in the audit report.
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.56.2 image --severity HIGH,CRITICAL information-security-practice-api > reports/trivy.txt 2>&1; echo "Trivy exit: $?"
docker run --rm -v "$PWD":/src -w /src python:3.11-slim sh -c 'pip install -q pip-audit && pip-audit -r requirements.txt' > reports/pip-audit.txt 2>&1; echo "pip-audit exit: $?"
docker run --rm -v "$PWD":/src -w /src python:3.11-slim sh -c 'pip install -q bandit && bandit -r app -f txt' > reports/bandit.txt 2>&1; echo "Bandit exit: $?"
echo 'SCANNER REPORTS GENERATED'
