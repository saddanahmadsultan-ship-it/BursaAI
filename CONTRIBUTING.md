# Contributing to BursaAI

## Sebelum commit

```powershell
python -m compileall -q .
python Tools\pre_commit_security_check.py
python -m unittest discover -s Tests -p "test_*.py" -v
```

## Prinsip

- Jangan ubah formula scoring tanpa test.
- Jangan ubah risk engine tanpa regression.
- Jangan campur output eksperimen dengan source code.
- Setiap bug fix mesti mempunyai test apabila praktikal.
- Gunakan type hints untuk modul baharu.
- Fail baharu mesti mempunyai tujuan yang jelas.
