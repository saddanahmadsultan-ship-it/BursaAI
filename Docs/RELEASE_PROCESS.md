# BursaAI Release Process

## Release Candidate

1. Semua feature telah digabungkan ke `develop`.
2. Bina atau kemas kini `release/7.0`.
3. Jalankan:
   - compile check
   - security check
   - unit test
   - regression test
   - demo validation
4. Kemas kini `VERSION.json` dan `CHANGELOG.md`.
5. Tag RC, contohnya:

```powershell
git tag -a v7.0.0-rc2 -m "BursaAI v7.0.0 RC2"
git push origin v7.0.0-rc2
```

## Stable

Selepas RC disahkan:

```powershell
git switch main
git merge --no-ff release/7.0
git tag -a v7.0.0 -m "BursaAI v7.0.0 Stable"
git push origin main --tags
```

## Fail yang tidak patut masuk Git

- token Telegram
- API key
- `.env`
- data sejarah besar
- hasil eksperimen
- checkpoint
- log
- database lokal
- laporan yang dijana
