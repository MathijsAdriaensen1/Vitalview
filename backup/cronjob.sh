#!/bin/bash

DATE=$(date +%Y-%m-%d_%H-%M)
export PGPASSWORD=SecurePass456

pg_dump -U vitaladmin -h db -d vitalview_db > /backups/backup_$DATE.sql
cp /backups/backup_$DATE.sql /backups/latest.sql