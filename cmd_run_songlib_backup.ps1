# conda deactivate
# conda activate base
python songlib_backup.py
python songlib_relation.py
git add *
git commit -m "feat: Auto backup"
git push
TIMEOUT 15