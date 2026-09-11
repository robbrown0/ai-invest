#!/bin/bash
# Trusted checkout only; no root, service startup or runtime data access.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
umask 077
test ! -L infrastructure/postgres/build
mkdir -p infrastructure/postgres/build
/usr/bin/cc -shared -fPIC -O2 -Wall -Wextra -Werror -Wl,-z,relro,-z,now \
  -o infrastructure/postgres/build/runtime_guard.so infrastructure/postgres/runtime_guard.c
/usr/bin/cc -DGUARD_PROBE -O2 -Wall -Wextra -Werror \
  -o infrastructure/postgres/build/guard_probe infrastructure/postgres/runtime_guard.c
/usr/bin/docker compose -f infrastructure/postgres/compose.yaml build postgres
/usr/bin/docker compose -f infrastructure/application/compose.yaml build cli
