# conda deactivate
# conda activate base

# Parameters for external credentials
param (
    [string]$username = "lucas.sax@gmail.com",
    [string]$password = "123456"
)

# Update report
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-pro-35\arcgispro-pro-35\python.exe" "$PSScriptRoot\songlib_report.py"

# Commit and push changes
git add *
git commit -m "feat: Auto report"
git push
TIMEOUT 15