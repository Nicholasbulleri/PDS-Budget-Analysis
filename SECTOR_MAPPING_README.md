# Sector mapping (canonical 10)

Raw sector values (from project `sector` or property `usageTypeSourceValue`) are mapped into these **10 canonical sectors** (aligned with Ingenious):

1. **Special Purpose Facility**
2. **Residential**
3. **Data Center**
4. **Industrial and Logistics**
5. **Hotels/Hospitality**
6. **Infrastructure/Energy**
7. **Retail**
8. **Education**
9. **Mixed-use**
10. **Office**

## Files

- **`sector_mapping.json`** – Maps raw strings to one of the 10 canonical names. Structure: `"Canonical Name": [ "raw value 1", "raw value 2", ... ]`. The runner builds a lookup from each raw value to its canonical sector (case-insensitive).
- **Runner** – `run_budget_query_closed_by_category_with_state_using_mapping_exclude_missing_area_with_property_sector.py` loads this file and applies the mapping to the `sector` column before writing CSV/xlsx.

## Unmapped values

If a raw sector is not in the mapping, it is set to **Special Purpose Facility** and the script prints:  
`Unmapped sector values (mapped to 'Special Purpose Facility'): [...]`

To fix:

1. Open `sector_mapping.json`.
2. Add each unmapped value to the list under the desired canonical sector (use exact spelling/casing as in the message).
3. Re-run the script.

## Confirm mapping

If you’re unsure how to map a value, say which raw value(s) and preferred canonical sector and we can update the mapping.
