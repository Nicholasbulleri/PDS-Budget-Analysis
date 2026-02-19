# Curated Schema Data Profiling Exercise - Overview

## Executive Summary

A comprehensive data profiling exercise was performed on the `work_dynamics.curated` schema to assess data volume, structure, and quality across all tables. The exercise analyzed 100 tables (sampled from a total of 387 tables in the schema) and successfully profiled 8 accessible tables containing over 23.9 million rows of data.

---

## Exercise Scope

### Objectives
1. **Inventory**: Identify all tables in the curated schema
2. **Volume Analysis**: Determine row counts and data volume per table
3. **Structure Analysis**: Document column schemas, data types, and table structures
4. **Quality Assessment**: Analyze null percentages, distinct values, and data patterns
5. **Accessibility Assessment**: Identify tables accessible with current permissions

### Methodology
- **Discovery**: Queried `system.information_schema.tables` to identify all tables
- **Schema Analysis**: Used `DESCRIBE TABLE` to extract column metadata
- **Volume Profiling**: Executed `COUNT(*)` queries to determine row counts
- **Column Profiling**: Analyzed null percentages, distinct counts, and sample values
- **Sampling Strategy**: Profiled first 100 tables alphabetically, with detailed column analysis on first 50

---

## Key Findings

### Schema Overview

| Metric | Value |
|--------|-------|
| **Total Tables in Schema** | 387 |
| **Tables Analyzed** | 100 (sampled) |
| **Accessible Tables** | 8 (8%) |
| **Total Rows (Accessible)** | 23,963,691 |
| **Total Columns (Accessible)** | 252 |

### Access Patterns

**Accessibility Breakdown:**
- **Accessible**: 8 tables (8% of analyzed)
- **Permission Denied**: 92 tables (92% of analyzed)

**Note**: The high percentage of inaccessible tables indicates that most tables in the curated schema require additional permissions beyond the current user's access level. This is expected in a production data warehouse environment where access is typically restricted by role and data sensitivity.

### Data Volume Analysis

#### Tables by Row Count Range

| Range | Count |
|-------|-------|
| 0 rows | 0 |
| 1-100 rows | 0 |
| 101-1K rows | 0 |
| 1K-10K rows | 0 |
| 10K-100K rows | 3 |
| 100K-1M rows | 0 |
| 1M+ rows | 5 |

#### Top Tables by Volume

| Table Name | Row Count | Column Count | Category |
|------------|-----------|--------------|----------|
| `commitment` | 5,768,034 | 55 | Financial/Budget |
| `budgetdetail` | 5,661,644 | 53 | Financial/Budget |
| `budgetchange` | 5,645,852 | 36 | Financial/Budget |
| `budgetforecast` | 5,554,130 | 22 | Financial/Budget |
| `directorycontactprojectlnk` | 1,186,886 | 21 | Relationship/Link |
| `companysourcesystemrelationship` | 68,867 | 9 | Metadata/Relationship |
| `customvalue` | 41,719 | 23 | Custom Data |
| `costsave` | 36,559 | 33 | Financial |

**Key Observations:**
- **Budget/Financial Tables Dominate**: 4 of the top 5 tables are budget-related, representing ~22.6M rows (94% of accessible data)
- **High Volume**: All accessible tables contain substantial data volumes (36K+ rows)
- **Consistent Structure**: Tables range from 9 to 55 columns, indicating well-normalized structures

### Source System Distribution

| Source System | Total Rows | Tables | Percentage |
|--------------|------------|--------|------------|
| **Clarizen** | 23,925,743 | 8 | 99.8% |
| **Ingenious** | 34,153 | 3 | 0.2% |

**Source System Insights:**
- **Clarizen Dominance**: Clarizen is the primary source system, contributing 99.8% of all accessible data
- **Ingenious Integration**: Ingenious appears in 3 tables (commitment, directorycontactprojectlnk, costsave) with smaller volumes
- **Table Coverage**: Clarizen appears in all 8 accessible tables, while Ingenious appears in 3 tables
- **Multi-Source Tables**: 3 tables contain data from both systems:
  - `commitment`: 99.9% Clarizen, 0.1% Ingenious
  - `directorycontactprojectlnk`: 97.7% Clarizen, 2.3% Ingenious
  - `costsave`: 95.4% Clarizen, 4.6% Ingenious

### Geography Data

**Status**: No country or region columns were found in the accessible tables. The tables do not contain explicit geographic data fields such as `country`, `region`, `location`, or similar columns.

---

## Detailed Table Profiles

### 1. commitment
- **Rows**: 5,768,034
- **Columns**: 55
- **Category**: Financial/Budget Management
- **Purpose**: Tracks financial commitments and obligations
- **Key Characteristics**: Largest table by volume, comprehensive financial tracking
- **Source Systems**: 
  - Clarizen: 5,764,167 rows (99.9%)
  - Ingenious: 3,999 rows (0.1%)
- **Geography Data**: Not available

### 2. budgetdetail
- **Rows**: 5,661,644
- **Columns**: 53
- **Category**: Financial/Budget Management
- **Purpose**: Detailed budget line items and breakdowns
- **Key Characteristics**: Second largest table, detailed budget granularity
- **Source Systems**: 
  - Clarizen: 5,658,501 rows (100%)
- **Geography Data**: Not available

### 3. budgetchange
- **Rows**: 5,645,852
- **Columns**: 36
- **Category**: Financial/Budget Management
- **Purpose**: Tracks budget modifications and change history
- **Key Characteristics**: Change tracking with approval workflows
- **Source Systems**: 
  - Clarizen: 5,643,301 rows (100%)
- **Geography Data**: Not available

### 4. budgetforecast
- **Rows**: 5,554,130
- **Columns**: 22
- **Category**: Financial/Budget Management
- **Purpose**: Budget forecasting and projections
- **Key Characteristics**: Forecast data with fewer columns than detail tables
- **Source Systems**: 
  - Clarizen: 5,554,150 rows (100%)
- **Geography Data**: Not available

### 5. directorycontactprojectlnk
- **Rows**: 1,186,886
- **Columns**: 21
- **Category**: Relationship/Link Table
- **Purpose**: Links directory contacts to projects
- **Key Characteristics**: Many-to-many relationship table
- **Source Systems**: 
  - Clarizen: 1,160,152 rows (97.7%)
  - Ingenious: 27,923 rows (2.3%)
- **Geography Data**: Not available

### 6. companysourcesystemrelationship
- **Rows**: 68,867
- **Columns**: 9
- **Category**: Metadata/System Integration
- **Purpose**: Maps companies to their source systems
- **Key Characteristics**: Metadata table with minimal columns
- **Source Systems**: 
  - Clarizen: 68,872 rows (100%)
- **Geography Data**: Not available

### 7. customvalue
- **Rows**: 41,719
- **Columns**: 23
- **Category**: Custom Data
- **Purpose**: Stores custom field values
- **Key Characteristics**: Flexible schema for custom attributes
- **Source Systems**: 
  - Clarizen: 41,723 rows (100%)
- **Geography Data**: Not available

### 8. costsave
- **Rows**: 36,559
- **Columns**: 33
- **Category**: Financial
- **Purpose**: Tracks cost savings initiatives
- **Key Characteristics**: Financial performance tracking
- **Source Systems**: 
  - Clarizen: 34,877 rows (95.4%)
  - Ingenious: 2,231 rows (4.6%)
- **Geography Data**: Not available

---

## Data Quality Insights

### Column-Level Analysis (Sample)

For the accessible tables, column-level profiling was performed on the first 10 columns of each table. Key metrics analyzed include:

1. **Null Percentage**: Percentage of null values per column
2. **Distinct Count**: Number of unique values
3. **Sample Values**: Representative data samples
4. **Data Types**: Column type distribution

**Common Patterns Observed:**
- **Identifier Columns**: High distinct counts, low null percentages (primary/foreign keys)
- **Financial Columns**: Numeric types (double) for amounts, rates, and calculations
- **Timestamp Columns**: Date/time fields for audit trails and temporal tracking
- **String Columns**: Codes, indicators, and descriptive text fields

---

## Technical Implementation

### Tools & Technologies
- **Python 3**: Scripting language
- **Databricks SQL Connector**: Database connectivity
- **Azure AD Authentication**: Secure authentication
- **Unity Catalog**: Metadata access via `system.information_schema`

### Script Components
1. **Table Discovery**: `get_all_curated_tables()` - Lists all tables
2. **Volume Profiling**: `get_table_row_count()` - Counts rows
3. **Schema Extraction**: `get_table_schema()` - Extracts column metadata
4. **Column Profiling**: `profile_column()` - Analyzes column statistics
5. **Report Generation**: `generate_profiling_report()` - Creates markdown and JSON outputs

### Output Files Generated
- **CURATED_SCHEMA_PROFILING_REPORT.md**: Human-readable markdown report
- **CURATED_SCHEMA_PROFILING_REPORT.json**: Machine-readable JSON export

---

## Limitations & Constraints

### Permission Constraints
- **92% of analyzed tables inaccessible**: Current user lacks SELECT permissions on most tables
- **Metadata Access**: Can query table names but not data content for majority of tables
- **Impact**: Profiling limited to 8 accessible tables (2% of total schema)

### Scope Limitations
- **Sampling**: Only first 100 tables analyzed (26% of total 387 tables)
- **Column Profiling**: Limited to first 10 columns per table for performance
- **Performance**: Large tables may require extended query times

### Data Access Patterns
- **Row-Level Access**: Requires explicit SELECT permissions
- **Schema Access**: Metadata queries work via `information_schema`
- **Lineage Access**: `system.access.table_lineage` requires additional privileges

---

## Recommendations

### Immediate Actions
1. **Permission Review**: Request expanded SELECT permissions for broader profiling coverage
2. **Prioritization**: Focus profiling on high-value tables based on business needs
3. **Automation**: Schedule periodic profiling to track data growth and quality trends

### Enhanced Profiling
1. **Full Schema Coverage**: Extend analysis to all 387 tables once permissions are granted
2. **Deep Column Analysis**: Profile all columns, not just samples
3. **Data Quality Rules**: Implement automated data quality checks based on profiling results
4. **Lineage Integration**: Combine with upstream/downstream lineage analysis

### Data Governance
1. **Documentation**: Maintain up-to-date schema documentation
2. **Change Tracking**: Monitor schema changes over time
3. **Access Management**: Document and manage table-level permissions
4. **Data Catalog**: Integrate profiling results into data catalog for discoverability

---

## Conclusion

The data profiling exercise successfully identified and analyzed 8 accessible tables in the `work_dynamics.curated` schema, revealing a data warehouse with substantial volume (23.9M+ rows) primarily focused on financial and budget management. The exercise demonstrates the schema's structure and provides a foundation for further analysis, though expanded permissions would enable more comprehensive profiling across all 387 tables.

**Key Takeaway**: The curated schema contains well-structured, high-volume financial data with clear patterns around budget management, commitments, and forecasting. The limited accessibility suggests a mature data governance model with role-based access controls.

---

## Appendix

### Files Generated
- `profile_curated_schema.py`: Profiling script
- `CURATED_SCHEMA_PROFILING_REPORT.md`: Detailed markdown report
- `CURATED_SCHEMA_PROFILING_REPORT.json`: JSON export for programmatic use

### Execution Date
Profiling exercise completed on: [Date of execution]

### Next Steps
1. Review detailed report: `CURATED_SCHEMA_PROFILING_REPORT.md`
2. Analyze JSON export: `CURATED_SCHEMA_PROFILING_REPORT.json`
3. Request expanded permissions for comprehensive coverage
4. Plan follow-up profiling exercises for remaining tables

