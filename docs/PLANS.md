# ~/docs/PLANS.md — ExecPlan

Gunakan untuk perubahan Medium atau Large. Plan harus self-contained, executable, delta-focused, dan disetujui sebelum implementasi.

Level menunjukkan kedalaman plan, bukan klasifikasi perubahan:

- **Light:** perubahan jelas dan berisiko rendah.
- **Standard:** beberapa area atau perubahan flow dengan risiko moderat.
- **Full:** contract, schema, migration, integration, atau risiko tinggi.

Gunakan level paling ringan yang aman. Empat section utama wajib; tambahkan section Optional hanya ketika relevan.

---

# ExecPlan: <judul>

Level: **Light | Standard | Full**

## 1. Problem and Evidence

- Masalah, perilaku saat ini, dan bukti `file:line`, endpoint, schema, atau docs.

Untuk perubahan flow atau contract:

| Area | Existing | Outcome |
|---|---|---|
| ... | ... | ... |

## 2. Outcome and Scope

- Perilaku yang diharapkan setelah selesai.

**In scope:**
- ...

**Out of scope:**
- ...

## 3. Ordered Changes

1. ...
2. ...

## 4. Acceptance and Verification

**Acceptance criteria:**
- [ ] Perilaku konkret yang harus terpenuhi.

**Exact verification commands and/or manual checks:**
```bash
<command>
```

Tandai command yang membutuhkan approval. Hapus code block jika verifikasi hanya manual. Jangan gunakan klaim generik seperti “existing behavior aman” tanpa check konkret.

## Decisions and Affected Files (Optional)

- Keputusan hasil review atau brainstorming.
- `path/to/file`: alasan perubahan.

## Contract and Compatibility (Optional)

- Request, response, schema, migration, docs, atau compatibility impact.

## Risks and Open Questions (Optional)

- Risiko nyata dan mitigasi.
- Pertanyaan yang jawabannya materially mengubah plan.

---
