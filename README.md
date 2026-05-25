# AI-Assisted Portfolio Rebalancing System

A professional institutional-style portfolio management dashboard that monitors allocation drift, generates AI-driven rebalancing recommendations, and provides risk analytics — built with Python and Streamlit.

## Run & Operate

- `cd portfolio-dashboard && streamlit run app.py --server.port 8000` — run the Streamlit dashboard
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- Required env: `DATABASE_URL` — Postgres connection string (for API server, not Streamlit app)

## Stack

- **Frontend/App**: Python 3.11 + Streamlit
- **Data**: pandas, numpy
- **Charts**: Plotly (interactive)
- **API Server**: Express 5 (Node.js 24, TypeScript 5.9)
- **DB**: PostgreSQL + Drizzle ORM (API server only)

## Where things live

- `portfolio-dashboard/app.py` — main Streamlit app (all pages/sections)
- `portfolio-dashboard/utils.py` — data loading, KPI computation, filtering, report generation
- `portfolio-dashboard/charts.py` — all Plotly chart functions
- `portfolio-dashboard/synthetic_portfolio_management_dataset.csv` — source dataset (1001 records)
- `portfolio-dashboard/.streamlit/config.toml` — Streamlit server config (headless, port 8000)

## Architecture decisions

- Single-file app with `st.radio` navigation (no multi-page file structure) — simpler for prototype demos
- All chart functions isolated in `charts.py` for reuse and testability
- `@st.cache_data` on data load to avoid re-reading CSV on every interaction
- Rebalancing logic is rule-based (SAA threshold engine) — deterministic and explainable
- Filters are applied globally before any section renders, so all charts reflect the same slice

## Product

Five dashboard sections targeting institutional investment users:

1. **Executive Summary** — KPI cards, allocation pies, drift status, downloadable reports
2. **Portfolio Monitoring** — tabbed drift detection table (Above/Below/Within Range), allocation trend by asset
3. **Rebalancing Intelligence** — AI BUY/SELL/HOLD recommendations with deviation analysis
4. **Risk Analytics** — risk score distribution, volatility breakdown, risk heatmap
5. **Historical Trends** — monthly return trend, risk trend, drift frequency area chart
6. **Institutional Insights** — market sentiment, stakeholder mapping, governance panel

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Streamlit requires `~/.streamlit/credentials.toml` with `email = ""` to suppress onboarding prompt on first run
- Use `width='stretch'` instead of `use_container_width=True` (deprecated after 2025-12-31)
- Run from inside `portfolio-dashboard/` directory so relative CSV path resolves correctly

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
