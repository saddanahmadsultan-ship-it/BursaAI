# Security Policy

## Rahsia

Jangan commit:

- API key
- bot token
- password
- private key
- database credential
- webhook secret

Gunakan `.env` lokal dan simpan hanya `.env.example` dalam Git.

## Data trading

Data pasaran, jurnal trade sebenar, portfolio sebenar dan laporan akaun tidak boleh dimasukkan ke repository awam.

## Jika rahsia telah ter-commit

1. Batalkan atau rotate rahsia tersebut segera.
2. Buang rahsia daripada kod.
3. Bersihkan sejarah Git jika perlu.
4. Jangan menganggap `git rm` sahaja telah memadam rahsia daripada sejarah.
