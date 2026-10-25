# Repository structure

```text
studyforge-project/
├── README.md
├── .env.example
├── compose.yaml
├── api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/studyforge/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   └── ai.py
│   └── tests/
├── web/
│   ├── Dockerfile
│   ├── package.json
│   └── src/app/
│       ├── page.tsx
│       ├── attempt/page.tsx
│       ├── layout.tsx
│       └── globals.css
└── docs/
    ├── product/
    ├── architecture/
    ├── security/
    ├── engineering/
    ├── RESEARCH.md
    └── adr/
```

Keep business rules in API services, never rely on frontend state for authorization or grading. Prompt templates and schema changes should be version controlled.
