#!/bin/bash
# wait-for-db.sh
# Script para aguardar o PostgreSQL estar pronto antes de iniciar a API

set -e

host="$1"
shift
cmd="$@"

echo "Aguardando o banco de dados em $host:5432..."

# Loop até a porta 5432 estar aberta
while ! nc -z "$host" 5432; do
  echo "Banco ainda não disponível - aguardando 2 segundos..."
  sleep 2
done

echo "Banco de dados pronto! Iniciando a aplicação..."
exec $cmd
