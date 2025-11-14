# conda deactivate
# conda activate base

# Parameters for external credentials
param (
    [string]$username = "lucas.sax@gmail.com",
    [string]$password = "123456"
)

# Execute the partial backup with credentials as arguments
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-pro-35\arcgispro-pro-35\python.exe" "$PSScriptRoot\songlib_partial_backup.py" --username $username --password $password

# Commit and push changes
git add *
git commit -m "feat: Auto partial backup"
git push
TIMEOUT 15