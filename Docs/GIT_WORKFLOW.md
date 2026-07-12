# BursaAI Git Workflow

## Branch utama

- `main`: release yang telah disahkan.
- `develop`: integrasi pembangunan semasa.
- `release/7.0`: persediaan BursaAI v7.
- `feature/<nama>`: ciri baharu.
- `fix/<nama>`: pembaikan.
- `hotfix/<nama>`: pembaikan kritikal pada `main`.

## Aliran kerja

1. Mulakan daripada `develop`.
2. Bina branch `feature/...` atau `fix/...`.
3. Commit kecil dan jelas.
4. Push branch.
5. Buka Pull Request ke `develop`.
6. Pastikan CI lulus.
7. Gabungkan ke `release/7.0` untuk regression.
8. Gabungkan release yang sah ke `main`.
9. Tag release.

## Contoh

```powershell
git switch develop
git pull
git switch -c feature/7a5-rc2-robustness
git add .
git commit -m "feat(research): add robustness engine"
git push -u origin feature/7a5-rc2-robustness
```

## Format commit

```text
feat(research): add robustness engine
fix(ranking): correct risk normalization
test(research): add fold degradation tests
docs(release): update Sprint 7A.5 notes
refactor(core): simplify service registry
```
