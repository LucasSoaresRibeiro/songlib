# conda deactivate
# conda activate base

# Parâmetros para receber credenciais como argumentos externos
param (
    [string]$username = "lucas.sax@gmail.com",
    [string]$password = "123456"
)

# Executa o backup com as credenciais como argumentos
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-clone-pro-32\python.exe" "$PSScriptRoot\songlib_backup.py" --username $username --password $password
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-clone-pro-32\python.exe" "$PSScriptRoot\songlib_relation.py"
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-clone-pro-32\python.exe" "$PSScriptRoot\songlib_report.py"

# Commit e push das alterações
git add *
git commit -m "feat: Auto backup"
git push
TIMEOUT 15