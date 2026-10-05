# Requirements Traceability

| Assessment requirement | Implementation evidence |
|---|---|
| Add/view/update/delete employees via UI | Employees page + FastAPI CRUD endpoints |
| Full name, job title, country, salary | Employee model/schema/form |
| Min/max/avg salary by country | Country insights endpoint + dashboard |
| Average salary for job title in country | Job-title insight endpoint |
| Other meaningful metrics | headcount, payroll, extrema, role breakdown |
| Backend + UI | FastAPI + Next.js |
| Relational DB | PostgreSQL production configuration |
| Seed 10,000 employees | `backend/app/db/seed.py` |
| Names from first/last name text files | `backend/data/first_names.txt`, `last_names.txt` |
| Seed performance matters | deterministic bulk upsert batches |
| Fully functional deployment | deployment instructions + health endpoint |
| Unit tests | `backend/tests/` |
| Incremental commits | Git history |
| Planning/design/AI artifacts | `docs/` |
