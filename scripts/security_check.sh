#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
FAIL=0; WARN=0
ok(){ echo "[OK] $1"; }
fail(){ echo "[FAIL] $1"; FAIL=$((FAIL+1)); }
warn(){ echo "[WARN] $1"; WARN=$((WARN+1)); }
grep -qxF '.env' .gitignore && ok '.env ignored' || fail '.env not ignored'
if git ls-files --error-unmatch .env >/dev/null 2>&1; then fail '.env tracked'; else ok '.env not tracked'; fi
if grep -q 'dev-only-secret' app/config.py docker-compose.yml 2>/dev/null; then fail 'fallback secret'; else ok 'no fallback secret'; fi
grep -q '^USER appuser' Dockerfile && ok 'nonroot Docker user' || fail 'no appuser'
grep -q '^HEALTHCHECK' Dockerfile && ok 'healthcheck defined' || fail 'healthcheck missing'
grep -q 'read_only: true' docker-compose.yml && ok 'read-only root filesystem' || fail 'read-only missing'
grep -q 'no-new-privileges:true' docker-compose.yml && ok 'no-new-privileges' || fail 'privileges option missing'
grep -q 'cap_drop:' docker-compose.yml && ok 'capabilities dropped' || fail 'capabilities not dropped'
USER=$(docker compose exec -T api whoami 2>/dev/null || true)
[ "$USER" = 'appuser' ] && ok 'running as appuser' || fail "wrong runtime user: $USER"
H=$(docker inspect --format='{{.State.Health.Status}}' dean_office_api 2>/dev/null || true)
[ "$H" = 'healthy' ] && ok 'runtime healthy' || fail "runtime health: $H"
CODE=$(curl -ks -o /dev/null -w '%{http_code}' https://localhost/health)
[ "$CODE" = 200 ] && ok 'HTTPS 200' || fail "HTTPS health: $CODE"
REDIRECT=$(curl -s -o /dev/null -w '%{http_code}' http://localhost/)
[ "$REDIRECT" = 301 ] && ok 'HTTP redirects to HTTPS' || fail "HTTP redirect: $REDIRECT"
HDR=$(curl -ks -D - -o /dev/null https://localhost/health)
for h in content-security-policy x-frame-options x-content-type-options strict-transport-security; do
 echo "$HDR" | grep -qi "^${h}:" && ok "$h" || fail "$h missing"
done
if docker compose exec -T api sh -c 'touch /app_code/not_allowed' >/dev/null 2>&1; then fail 'filesystem writable'; else ok 'filesystem protected'; fi
if [ -f reports/pip-audit.txt ]; then ok 'pip-audit report present'; else warn 'pip-audit not run yet'; fi
if [ -f reports/trivy.txt ]; then ok 'trivy report present'; else warn 'Trivy not run yet'; fi
if [ -f reports/bandit.txt ]; then ok 'Bandit report present'; else warn 'Bandit not run yet'; fi
echo "FAIL: $FAIL WARN: $WARN"
if [ "$FAIL" -eq 0 ]; then echo 'SECURITY CHECK PASSED'; else echo 'SECURITY CHECK FAILED'; fi
[ "$FAIL" -eq 0 ]
