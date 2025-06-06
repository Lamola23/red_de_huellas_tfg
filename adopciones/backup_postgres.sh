#!/bin/bash
# Guarda backups con fecha en una carpeta

fecha=$(date +%Y-%m-%d_%H-%M)
mkdir -p C:\Users\mortm\OneDrive - Conselleria d'Educació\Escritorio\TFG\Backup

pg_dump -U postgres -F c -f /home/tu_usuario/backups/backup_$fecha.dump Red_de_huellas
