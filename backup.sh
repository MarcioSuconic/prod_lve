#!/bin/bash
# backup.sh — faz backup do banco LVE e limpa os antigos (>30 dias)

set -e

# Configurações
BACKUP_DIR="/home/marcio/Desktop/projetos/app_prod_lve/backups"
DB_USER="marcio_gcs"
DB_PASSWORD="3737_Mgcs"
DB_NAME="lve"
DB_HOST="localhost"
DB_PORT="5432"
RETENCAO_DIAS=30

# Cria pasta
mkdir -p "$BACKUP_DIR"

# Nome do arquivo
DATA=$(date +%Y-%m-%d_%H-%M)
ARQUIVO="$BACKUP_DIR/lve_${DATA}.dump"

# Faz o dump
PGPASSWORD="$DB_PASSWORD" pg_dump -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" \
  -d "$DB_NAME" -F c -f "$ARQUIVO"

echo "[$(date)] Backup criado: $ARQUIVO"

# Limpa backups antigos
find "$BACKUP_DIR" -name "lve_*.dump" -mtime +$RETENCAO_DIAS -delete

echo "[$(date)] Backups antigos (>${RETENCAO_DIAS} dias) removidos."
