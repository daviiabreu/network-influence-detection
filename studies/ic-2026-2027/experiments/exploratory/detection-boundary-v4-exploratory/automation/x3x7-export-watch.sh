#!/bin/bash
set -euo pipefail
dir=$(cd "$(dirname "$0")" && pwd)
support=$dir/v4_event_automation.py
test -f "$support" || support=$dir/../v4_event_automation.py
exec python3 "$support" watch "$@"
