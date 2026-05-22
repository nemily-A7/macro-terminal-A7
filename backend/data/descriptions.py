"""
Static factual descriptions for every catalog indicator.
Displayed in the IndicatorInsight panel alongside the AI interpretation.
"""

DESCRIPTIONS: dict[str, str] = {
    # ── US Inflation ──────────────────────────────────────────────────────────
    "us_cpi": "Consumer Price Index measuring inflation across a broad basket of goods and services. The Fed monitors CPI alongside PCE to assess price stability.",
    "us_core_cpi": "CPI excluding volatile food and energy prices — isolates the underlying inflation trend watched by policymakers.",
    "us_pce": "Personal Consumption Expenditures price index — broader than CPI, covers all household spending. The Fed officially targets PCE at 2%.",
    "us_core_pce": "Core PCE (excluding food and energy) is the Fed's primary inflation benchmark and the measure it explicitly targets at 2% annually.",
    "us_ppi": "Producer Price Index tracking wholesale input costs — a leading indicator of future consumer inflation as pricing pressure flows downstream.",
    "us_infl_exp_1y": "University of Michigan 1-year consumer inflation expectations — measures where households expect prices to be in 12 months.",
    "us_infl_exp_5y": "5-year breakeven inflation rate derived from TIPS spreads — the bond market's forward-looking inflation forecast over 5 years.",
    "us_infl_exp_10y": "10-year breakeven inflation rate — the long-term inflation expectation priced into Treasury markets, reflecting credibility of the Fed's 2% target.",

    # ── US Rates ──────────────────────────────────────────────────────────────
    "us_fed_funds": "Federal Reserve benchmark overnight lending rate — the primary monetary policy lever directly influencing all borrowing costs economy-wide.",
    "us_3m": "3-month Treasury bill yield — closely tracks the current Fed funds rate and near-term rate expectations.",
    "us_2y": "2-year Treasury yield — the most rate-sensitive maturity, driven by Fed policy expectations over the coming two years.",
    "us_10y": "10-year Treasury yield — the global benchmark for long-term borrowing costs and a critical input for equity valuations and mortgage rates.",
    "us_30y": "30-year Treasury yield — reflects the market's long-term view on growth, inflation, and US fiscal sustainability.",
    "us_spread_10y_2y": "10Y–2Y yield curve spread. Sustained inversions (negative readings) have preceded every US recession since 1955.",
    "us_spread_10y_3m": "10Y–3M yield curve spread — cited by the NY Fed as the most statistically reliable recession-prediction signal.",

    # ── US Labor ──────────────────────────────────────────────────────────────
    "us_unrate": "US unemployment rate — the headline labor market gauge. The Fed considers 4–5% to be broadly consistent with full employment.",
    "us_nfp": "Nonfarm Payrolls monthly change — the single most market-moving US economic release, covering ~80% of US workers excluding farms.",
    "us_participation": "Labor force participation rate — the share of working-age Americans who are employed or actively seeking work.",
    "us_job_openings": "JOLTS job openings — measures unfilled positions and labor demand; a key input to the Beveridge curve and Fed assessment of slack.",
    "us_wages": "Average hourly earnings YoY — a critical wage inflation gauge; persistently elevated readings signal sustained consumer price pressures.",

    # ── US Growth ─────────────────────────────────────────────────────────────
    "us_gdp": "Real GDP growth (annualized quarterly rate) — the broadest measure of US economic output, adjusted for inflation.",
    "us_gdp_nominal": "Nominal GDP — total economic output at current prices, used for assessing debt-to-GDP ratios and global comparisons.",
    "us_indpro": "Industrial Production index — measures output across manufacturing, mining, and utilities, providing a real-time activity signal.",
    "us_retail_sales": "Advance retail and food service sales MoM — a high-frequency gauge of consumer spending, which accounts for ~70% of US GDP.",
    "us_housing_starts": "New residential units started — a leading economic indicator sensitive to mortgage rates, construction employment, and demand.",
    "us_building_permits": "Building permits issued — leads housing starts by 1–2 months, providing early visibility into future construction activity.",
    "us_trade_balance": "Trade balance (goods and services) — a deficit reduces GDP directly; reflects domestic demand strength and currency competitiveness.",

    # ── US Money & Credit ─────────────────────────────────────────────────────
    "us_m2": "M2 money supply — broad money including cash, savings, and money market funds. Rapid M2 expansion can precede inflationary episodes.",
    "us_hy_spread": "High-yield (junk bond) option-adjusted spread over Treasuries — a real-time credit stress indicator and risk appetite barometer.",

    # ── US Risk & Sentiment ───────────────────────────────────────────────────
    "us_vix": "CBOE Volatility Index — the market's expectation of 30-day S&P 500 volatility. Known as the 'fear gauge'; readings above 30 signal elevated stress.",
    "us_sentiment": "University of Michigan Consumer Sentiment index — a leading indicator of household spending intentions and economic confidence.",
    "us_gpr": "Geopolitical Risk Index (Caldara & Iacoviello, Fed) — quantifies geopolitical risk from automated text analysis of news across 44 countries.",

    # ── EU Inflation ──────────────────────────────────────────────────────────
    "eu_cpi": "HICP (Harmonised Index of Consumer Prices) — the ECB's official inflation measure, targeting 2% over the medium term. Published monthly by Eurostat.",
    "eu_core_cpi": "Core HICP excluding energy, food, alcohol, and tobacco — captures underlying inflationary dynamics the ECB focuses on.",

    # ── EU Rates ──────────────────────────────────────────────────────────────
    "eu_mro": "ECB Main Refinancing Operations rate — the primary ECB policy rate governing one-week liquidity provided to commercial banks.",
    "eu_dfr": "ECB Deposit Facility Rate — the rate at which commercial banks park overnight excess reserves at the ECB, the effective floor on euro rates.",
    "eu_10y_yield": "10-year government bond yield — sovereign borrowing costs and a measure of country-specific risk premium over the Bund.",
    "eu_bund_10y": "German Bund 10Y yield (AAA ECB yield curve) — the Euro Area's risk-free rate benchmark, derived daily from the ECB Statistical Data Warehouse.",
    "eu_schatz_2y": "German Schatz 2Y yield — the short end of the Bund curve, closely driven by near-term ECB rate path expectations.",
    "eu_all_sov_10y": "EA All Sovereigns composite 10Y yield (ECB yield curve) — includes peripheral spreads, showing the blended sovereign risk premium.",
    "eu_eurusd": "EUR/USD exchange rate — the world's most liquid currency pair, driven by ECB/Fed policy divergence and global risk sentiment.",
    "eu_eurgbp": "EUR/GBP exchange rate — reflects relative monetary conditions and economic performance between the Euro Area and United Kingdom.",

    # ── EU Labor ──────────────────────────────────────────────────────────────
    "eu_unemployment": "Eurostat seasonally-adjusted unemployment rate — harmonized across all Euro Area member states for cross-country comparability.",

    # ── EU Growth ─────────────────────────────────────────────────────────────
    "eu_gdp_growth": "Annual real GDP growth rate (World Bank) — year-on-year economic output change for Euro Area or individual member states.",
    "eu_gdp_qoq": "Quarterly GDP growth, chain-linked volume, % change on prior quarter — the real-time pulse of Euro Area economic momentum.",
    "eu_indpro": "Industrial production index (B–D: mining + manufacturing) — a leading cyclical indicator of Euro Area economic health.",
    "eu_retail_sales": "Retail trade volume index YoY — tracks consumer spending across Euro Area countries using Eurostat harmonized data.",
    "eu_cli": "OECD Composite Leading Indicator — designed to anticipate turning points in economic activity approximately 6–9 months ahead.",

    # ── EU Money & Credit ─────────────────────────────────────────────────────
    "eu_m3": "Euro Area M3 broad money supply YoY — monitored by the ECB as an intermediate target; sustained acceleration can foreshadow inflation.",
    "eu_hy_spread": "European high-yield option-adjusted spread — measures the credit risk premium demanded in the European junk bond market.",

    # ── EU Risk & Sentiment ───────────────────────────────────────────────────
    "eu_consumer_confidence": "OECD consumer confidence indicator — surveys household expectations about income, major purchases, and economic outlook.",
    "eu_business_confidence": "OECD business confidence indicator — surveys firms on production expectations, order books, and hiring intentions.",
    "eu_gpr": "Geopolitical Risk Index (Caldara & Iacoviello) — country-level geopolitical risk quantified from automated news media analysis.",

    # ── ASIA Inflation ────────────────────────────────────────────────────────
    "asia_cpi": "Annual consumer price inflation (World Bank) — headline CPI for the selected Asian economy.",
    "asia_cpi_monthly": "Monthly CPI YoY (OECD MEI via FRED) — higher-frequency inflation data for Japan, South Korea, Australia, India, and China.",

    # ── ASIA Rates ────────────────────────────────────────────────────────────
    "asia_rates": "Short-term interest rate — the central bank policy rate or overnight interbank rate for the selected ASIA economy.",
    "asia_10y": "10-year government bond yield — long-term sovereign borrowing costs for the selected ASIA country.",

    # ── ASIA Labor ────────────────────────────────────────────────────────────
    "asia_unemployment": "ILO-harmonized monthly unemployment rate via FRED — available for Japan, South Korea, and Australia.",

    # ── ASIA Growth ───────────────────────────────────────────────────────────
    "asia_gdp": "Annual real GDP growth rate (World Bank) — the broadest measure of economic output for the selected ASIA country.",
    "asia_indpro": "Industrial production index YoY (OECD MEI via FRED) — manufacturing and mining output for major ASIA-Pacific economies.",

    # ── ASIA Money & Credit ───────────────────────────────────────────────────
    "asia_m2": "Broad money supply as % of GDP (World Bank) — reflects financial sector depth and monetary conditions relative to economic size.",

    # ── ASIA Risk & Sentiment ─────────────────────────────────────────────────
    "asia_cli": "OECD Composite Leading Indicator — designed to anticipate GDP turning points in Asia-Pacific economies 6–9 months ahead.",
    "asia_current_account": "Current account balance as % of GDP (World Bank) — a surplus signals net exporter status and external balance strength.",
    "asia_gpr": "Geopolitical Risk Index (Caldara & Iacoviello) — country-specific risk quantified from geopolitical event and conflict news analysis.",

    # ── Global FX ─────────────────────────────────────────────────────────────
    "global_dxy": "Trade-Weighted US Dollar Index — measures USD strength against a broad basket of trading partner currencies.",

    # ── Global Markets — Equities ─────────────────────────────────────────────
    "market_sp500": "S&P 500 — benchmark for 500 large-cap US stocks, representing approximately 80% of total US equity market capitalization.",
    "market_nasdaq": "NASDAQ Composite — technology-heavy US equity index with ~3,000 stocks; highly sensitive to interest rate changes and growth expectations.",
    "market_djia": "Dow Jones Industrial Average — price-weighted index of 30 large-cap US blue-chip companies across diverse sectors.",
    "market_eurostoxx": "Euro Stoxx 50 — benchmark index of 50 blue-chip companies across 11 Euro Area countries; the most-traded European equity index.",
    "market_dax": "DAX — 40 largest German companies by market cap; heavily weighted toward automotive, chemicals, industrial, and financial sectors.",
    "market_cac40": "CAC 40 — index of the 40 largest French companies; significant weights in luxury goods (LVMH, Hermès), energy, and financials.",
    "market_nikkei": "Nikkei 225 — Japan's primary equity benchmark; influenced by yen movements, Bank of Japan policy, and global risk appetite.",
    "market_hangseng": "Hang Seng Index — Hong Kong's benchmark, heavily weighted toward mainland Chinese companies, property, and financials.",
    "market_kospi": "KOSPI — South Korea's main equity index; sensitive to the semiconductor cycle, China trade dynamics, and geopolitical risks.",
    "market_asx200": "S&P/ASX 200 — Australia's benchmark index; dominated by financials, materials (iron ore, copper), and energy sectors.",

    # ── Global Markets — FX ───────────────────────────────────────────────────
    "market_eurusd": "EUR/USD — the world's most traded currency pair, driven by ECB/Fed policy divergence and global risk sentiment.",
    "market_usdjpy": "USD/JPY — the primary yen pair; reflects Bank of Japan policy, US–Japan rate differentials, and safe-haven demand for yen.",
    "market_gbpusd": "GBP/USD (Cable) — sensitive to Bank of England policy, UK economic data, and political/fiscal developments.",
    "market_audusd": "AUD/USD — a commodity currency pair closely tied to Chinese economic demand, iron ore prices, and RBA policy.",
    "market_usdcny": "USD/CNY — managed by the People's Bank of China; movements reflect trade tensions, PBoC policy, and Chinese growth outlook.",

    # ── Global Markets — Commodities ──────────────────────────────────────────
    "market_wti": "WTI Crude — the US benchmark for crude oil pricing, driven by OPEC+ output policy, US inventory data, and global demand.",
    "market_brent": "Brent Crude — the global oil benchmark, pricing approximately two-thirds of world oil supply. Influenced by geopolitical risk premium.",
    "market_natgas": "Henry Hub natural gas spot price — the US benchmark, driven by weather demand, storage levels, and LNG export capacity.",
    "market_gold": "Gold spot price (London AM Fix, USD/troy oz) — a safe-haven asset and inflation hedge; historically inversely correlated with real rates.",

    # ── Global Markets — Crypto ───────────────────────────────────────────────
    "market_btc": "Bitcoin — the leading cryptocurrency by market cap; increasingly used as a macro liquidity and risk-on/risk-off barometer.",
}
