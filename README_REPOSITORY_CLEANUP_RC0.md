# BursaAI Sprint 7 Repository Cleanup RC0

1. Extract ZIP.
2. Copy semua kandungan ke root BursaAI.
3. Jalankan:

```powershell
Scripts\10_REPOSITORY_CLEANUP_RC0.cmd
```

4. Semak:

```powershell
git status
git diff --cached --name-only
```

5. Commit:

```powershell
git commit -m "chore(repo): clean repository and exclude local artifacts"
```

6. Audit penuh:

```powershell
Scripts\11_REPOSITORY_FINAL_AUDIT.cmd
```

7. Push:

```powershell
git push --force-with-lease origin feature/7a5-rc4-pareto-confidence
```

`git rm --cached` membuang fail daripada Git index sahaja. Fail lokal kekal.
