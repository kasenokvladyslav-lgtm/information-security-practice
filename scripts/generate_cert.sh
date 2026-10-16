#!/usr/bin/env bash
set -euo pipefail
mkdir -p nginx/certs
if [ ! -f nginx/certs/selfsigned.key ] || [ ! -f nginx/certs/selfsigned.crt ]; then
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/selfsigned.key -out nginx/certs/selfsigned.crt -subj "/C=UA/O=University/OU=IT/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" >/dev/null 2>&1
  chmod 600 nginx/certs/selfsigned.key
fi
echo 'SELF-SIGNED CERTIFICATE READY'
