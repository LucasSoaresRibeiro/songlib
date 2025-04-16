# conda deactivate
# conda activate base
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "$PSScriptRoot\songlib_backup.py"
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "$PSScriptRoot\songlib_relation.py"
git add *
git commit -m "feat: Auto backup"
git push
TIMEOUT 15