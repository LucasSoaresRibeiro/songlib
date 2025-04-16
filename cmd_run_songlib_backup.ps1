# conda deactivate
# conda activate base
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-clone-pro-32\python.exe" "$PSScriptRoot\songlib_backup.py"
& "C:\Lucas\Programas\ArcGISPro\envs\arcgispro-clone-pro-32\python.exe" "$PSScriptRoot\songlib_relation.py"
git add *
git commit -m "feat: Auto backup"
git push
TIMEOUT 15