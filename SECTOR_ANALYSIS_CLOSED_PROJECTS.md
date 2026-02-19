# Sector availability for Closed projects – analysis summary

## Finding: sector is sparse by **source system**, not by phase

| Phase (USD)        | Total projects | With sector | %    |
|--------------------|----------------|-------------|------|
| Closed             | 55,138         | 208         | 0.38 |
| Construct          | 3,463          | 304         | 8.78 |
| Planning/Design    | 674            | 635         | **94.21** |

For **Closed USD**, sector is populated only for **Ingenious**-sourced projects:

| sourcesystem | Closed USD projects | With sector |
|--------------|---------------------|-------------|
| **clarizen** | 54,930              | **0**       |
| **ingenious**| 208                 | **208**     |

So the missing sector on Closed is because most Closed projects are **Clarizen**-sourced, and **sector is not populated for Clarizen** in `work_dynamics.curated.project`.

---

## Where else was sector checked?

1. **project.sector**  
   Only populated for Ingenious (as above). No other sector-related column on `project` holds sector for Clarizen.

2. **propertyextended.industrysectorname**  
   - `project.propertyidentifier` is populated for 53,759 of 55,138 Closed USD projects.  
   - Join to `propertyextended` on `propertyidentifier` matches **127** Closed USD projects.  
   - For those 127, **none** of the matching `propertyextended` rows have `industrysectorname` populated.  
   So this does not provide sector for Closed.

3. **Backfill from Construct**  
   Closed projects with missing sector: **54,930**.  
   Of those, **0** have a Construct-phase row with the same `workitemidentifier` and a non-null sector.  
   So sector cannot be filled from Construct for Closed.

4. **Other curated tables**  
   - `phub_oneviewclientproperty.industrysector` exists but would require a reliable link from `project` to that table (no standard join key was used here).  
   - `company` does not expose a sector/segment column in the same curated schema.  
   - `dssf_opportunity_processed` has sector-like columns; linkage to Closed projects was not verified.

**Conclusion:** In the curated objects checked, **sector is not available elsewhere** for Clarizen Closed projects. The only populated sector in this analysis is **project.sector for Ingenious**.

---

## Alternative: jllbusinessline (well populated for Closed)

For Closed USD, **jllbusinessline** is populated for 32,491 projects (59%):

| jllbusinessline                          | Count  |
|------------------------------------------|--------|
| PDS Dedicated                            | 20,937 |
| PDS Markets                              | 8,046  |
| JLL IFM                                  | 2,818  |
| Non-JLL                                  | 424    |
| 350001 PDS - Healthcare                  | 12     |
| 350003 PDS - Office [RPM]                | 11     |
| 350007 PDS - Industrial                 | 9      |
| 350005 PDS - Hospitality                | 2      |
| …                                        | …      |

This is **business line**, not sector, but:

- It is available for most Closed (including Clarizen).
- Some values map to sector-like categories (Healthcare, Office, Industrial, Hospitality).

**Recommendation:** For Closed (and similar phases where sector is sparse):

- Keep **sector** where it exists (Ingenious).
- For reporting, consider adding **jllbusinessline** as a dimension, or a derived column such as **sector_or_business_line** = `COALESCE(TRIM(sector), jllbusinessline)` so Clarizen projects still have a usable segment for analysis.

---

## Scripts used

- `analyze_sector_availability.py` – sector by phase, column discovery, backfill check.
- `analyze_sector_sources.py` – propertyextended, company, jllbusinessline.
- `analyze_sector_join.py` – project–propertyextended join, sourcesystem vs sector, jllbusinessline distribution.
