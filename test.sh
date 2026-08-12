#!/usr/bin/env bash
# ==========================================================
# Script de testes do projeto OCDS
#
# Uso:
#   ./test.sh                     # roda TODOS os testes
#   ./test.sh members             # roda só o app members
#   ./test.sh members votes       # roda os apps members e votes
#   ./test.sh --coverage          # todos os testes com relatório de cobertura
#   ./test.sh members --coverage  # só o app members com cobertura
#   ./test.sh --list              # lista os apps disponíveis
# ==========================================================
set -euo pipefail

cd "$(dirname "$0")"

PY=".venv/Scripts/python.exe"
if [ ! -f "$PY" ]; then
    PY="python"
fi

APPS=(accounts base carmel contacts contributions members votes)
COVERAGE=0
APPS_TO_TEST=()

for arg in "$@"; do
    case "$arg" in
        --coverage) COVERAGE=1 ;;
        --list)
            echo "Apps disponíveis: ${APPS[*]}"
            exit 0
            ;;
        --help|-h)
            sed -n '2,12p' "$0"
            exit 0
            ;;
        *)
            APPS_TO_TEST+=("$arg")
            ;;
    esac
done

if [ ${#APPS_TO_TEST[@]} -eq 0 ]; then
    APPS_TO_TEST=("${APPS[@]}")
fi

echo "=============================================="
echo " Apps a testar: ${APPS_TO_TEST[*]}"
echo " Coverage:     $([ $COVERAGE -eq 1 ] && echo 'sim' || echo 'não')"
echo "=============================================="

if [ "$COVERAGE" -eq 1 ]; then
    SOURCE="$(IFS=,; echo "${APPS_TO_TEST[*]}")"
    "$PY" -m coverage erase
    "$PY" -m coverage run --source="$SOURCE" manage.py test "${APPS_TO_TEST[@]}" --parallel
    echo ""
    echo "--- Relatório de cobertura ---"
    "$PY" -m coverage report -m
else
    "$PY" manage.py test "${APPS_TO_TEST[@]}"
fi
