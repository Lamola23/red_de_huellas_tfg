# Crear carpeta si no existe
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupDir = "C:\db_backups"
$archivo = "$backupDir\backup_$fecha.sql"

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# Ejecutar pg_dump usando cmd.exe para redirigir correctamente
cmd.exe /c ('"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres Red_de_huellas > "' + $archivo + '"')


# Eliminar archivos de más de 7 días
Get-ChildItem -Path $backupDir -Filter *.sql |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item

