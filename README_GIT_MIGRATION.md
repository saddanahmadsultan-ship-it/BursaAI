# BursaAI Git Migration Release Pack

## Pemasangan

1. Extract ZIP.
2. Copy semua kandungan ke root BursaAI.
3. Jalankan:

```powershell
Scripts\01_INIT_LOCAL_GIT.cmd
```

4. Cipta repository kosong dan **private** di GitHub.
5. Jalankan:

```powershell
Scripts\02_CONNECT_GITHUB.cmd
```

6. Paste URL repository GitHub apabila diminta.

## Sebelum mula

Pastikan Git telah dipasang:

```powershell
git --version
```

Tetapkan identiti Git jika belum:

```powershell
git config --global user.name "Nama Anda"
git config --global user.email "email@example.com"
```

## Repository visibility

Gunakan **Private repository** kerana BursaAI mungkin mengandungi strategi proprietary, konfigurasi trading dan integrasi token.

## Branch

```text
main
develop
release/7.0
feature/*
fix/*
hotfix/*
```

## Validasi

```powershell
Scripts\04_VALIDATE_REPOSITORY.cmd
```

## GitHub branch protection

Selepas push:

1. Buka Settings.
2. Buka Rules atau Branches.
3. Lindungi `main`.
4. Require pull request.
5. Require status checks.
6. Block force push.
7. Ulang untuk `develop`.

## Git LFS

Jangan masukkan data pasaran atau hasil eksperimen besar ke Git.
Git LFS hanya patut digunakan untuk aset binari yang benar-benar perlu
dikongsi dan mempunyai polisi storan yang jelas.
