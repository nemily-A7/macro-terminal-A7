# Terminal Project

This project is organized into two main sections:

## 1. Macro Terminal (`terminal1_macro/`)
The user interface for the Macro Dashboard.
**To start the app:**
```bash
streamlit run terminal1_macro/app.py
```

## 2. Testing & Backend (`test1/`)
Contains all backend code, ingestion scripts, legacy UI, and configuration.
- `terminal_backend`: API & DB Models
- `terminal_ingestion`: Data Pipelines
- `terminal_ui_legacy`: Old Interface

*Note: The `.env` file must remain at the root for configuration.*
