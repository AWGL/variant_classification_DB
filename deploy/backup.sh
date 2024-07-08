
# for details on backup and restore - see https://www.postgresql.org/docs/9.1/backup-dump.html#BACKUP-DUMP-RESTORE

BACKUP_DIR="/home/webapps/acmg_backups/"
UPLOAD_DIR="/home/webapps/variant_classification_DB/mysite/media/uploads/"

# Backup Postgres DB
/usr/pgsql-9.6/bin/pg_dump variant_classification_db -U variant_classification_db_user -h localhost | gzip >  "$BACKUP_DIR"/"$(date '+%Y%m%d%H%M%S')_acmg_db.txt.gz"

# Backup media uploads
# First remove existing media backups so the backup size doesn't get out of control
rm "$BACKUP_DIR"/media/*
# Then make new backup
cd "$UPLOAD_DIR"
cd ..
tar -czf "$BACKUP_DIR"/media/"$(date '+%Y%m%d%H%M%S')_media.tar.gz" uploads/



