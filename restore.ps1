#!/bin/bash

# Gebruik: ./restore.sh backups/backup_YYYY-MM-DD_HH-MM.sql
# Of: ./restore.sh backups/latest.sql

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "❌ Geef het pad naar het backupbestand op, bijvoorbeeld:"
  echo "   ./restore.sh backups/latest.sql"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ Bestand niet gevonden: $BACKUP_FILE"
  exit 1
fi

echo "⚠️ De database 'vitalview_db' zal worden overschreven met:"
echo "   $BACKUP_FILE"
read -p "❓ Weet je dit zeker? (ja/N): " CONFIRM

if [[ "$CONFIRM" != "ja" ]]; then
  echo "🚫 Herstel geannuleerd."
  exit 0
fi

echo "♻️ Herstellen..."
docker exec -i vitalview1-db-1 psql -U vitaladmin -d vitalview_db < "$BACKUP_FILE"

echo "✅ Herstel voltooid."
