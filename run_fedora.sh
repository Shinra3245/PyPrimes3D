#!/usr/bin/env bash
#
# PyPrimes 3D - Lanzador para Fedora
#
# Crea (si hace falta) un entorno virtual con las dependencias correctas
# para Fedora/Python 3.14 y arranca el juego.
#
#   Uso:   ./run_fedora.sh
#
set -euo pipefail

# Directorio del proyecto (donde vive este script)
cd "$(dirname "$(readlink -f "$0")")"

VENV_DIR="venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# --- 1. Comprobar librerias de sistema necesarias -------------------------
missing_pkgs=()
check_lib() { ldconfig -p 2>/dev/null | grep -q "$1" || missing_pkgs+=("$2"); }
check_lib "libglut.so"  "freeglut"
check_lib "libGLU.so"   "mesa-libGLU"
check_lib "libGL.so"    "mesa-libGL"

if [ "${#missing_pkgs[@]}" -gt 0 ]; then
    echo "Faltan librerias de sistema. Instalalas con:"
    echo "    sudo dnf install ${missing_pkgs[*]}"
    exit 1
fi

# --- 2. Crear entorno virtual e instalar dependencias ---------------------
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo ">> Creando entorno virtual ($PYTHON_BIN)..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Instalar dependencias solo si falta alguna (marcador .deps_ok)
if [ ! -f "$VENV_DIR/.deps_ok" ] || [ requirements-fedora.txt -nt "$VENV_DIR/.deps_ok" ]; then
    echo ">> Instalando dependencias..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip -q
    "$VENV_DIR/bin/python" -m pip install -r requirements-fedora.txt
    touch "$VENV_DIR/.deps_ok"
fi

# --- 3. Ejecutar el juego -------------------------------------------------
echo ">> Iniciando PyPrimes 3D..."
exec "$VENV_DIR/bin/python" PyPrimes3D.py
