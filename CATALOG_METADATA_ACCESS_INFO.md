# Databricks Catalog Metadata Access for Inaccessible Tables

## Overview

Even when you cannot `SELECT` from tables due to permission constraints, Databricks Unity Catalog provides metadata access through system tables that may still be queryable. This document outlines what catalog metadata should be accessible.

## Accessible Catalog Metadata

### 1. Table List and Basic Info
**Source**: `system.information_schema.tables`

**Accessible Information:**
- `table_catalog` - Catalog name (e.g., "work_dynamics")
- `table_schema` - Schema name (e.g., "curated")
- `table_name` - Table name
- `table_type` - Type (BASE TABLE, VIEW, etc.)
- `data_source_format` - Storage format (DELTA, PARQUET, etc.)
- `storage_path` - Storage location path
- `comment` - Table comment/description

**Query Example:**
```sql
SELECT 
    table_catalog,
    table_schema,
    table_name,
    table_type,
    data_source_format,
    storage_path,
    comment
FROM system.information_schema.tables
WHERE table_schema = 'curated'
ORDER BY table_name
```

### 2. Column Metadata
**Source**: `system.information_schema.columns`

**Accessible Information:**
- `column_name` - Column name
- `ordinal_position` - Column position (1, 2, 3, ...)
- `data_type` - Data type (STRING, INT, DECIMAL, etc.)
- `is_nullable` - Whether column allows NULL (YES/NO)
- `column_default` - Default value
- `comment` - Column comment/description

**Query Example:**
```sql
SELECT 
    column_name,
    ordinal_position,
    data_type,
    is_nullable,
    column_default,
    comment
FROM system.information_schema.columns
WHERE table_schema = 'curated'
AND table_name = 'your_table_name'
ORDER BY ordinal_position
```

### 3. DESCRIBE TABLE (May Work)
**Command**: `DESCRIBE TABLE work_dynamics.curated.table_name`

**Accessible Information:**
- Column names and types
- Column comments
- Sometimes works even without SELECT permission

**Note**: This may require `USE SCHEMA` permission or specific metadata access.

### 4. DESCRIBE DETAIL (May Work)
**Command**: `DESCRIBE DETAIL work_dynamics.curated.table_name`

**Accessible Information:**
- `format` - Storage format
- `location` - Storage location
- `numFiles` - Number of files
- `sizeInBytes` - Table size
- `numRows` - Row count (if available)
- `partitionColumns` - Partition columns
- `createdAt` - Creation timestamp
- `lastModified` - Last modification timestamp

**Note**: Row counts may not always be available, especially for large tables.

### 5. DESCRIBE EXTENDED (May Work)
**Command**: `DESCRIBE EXTENDED work_dynamics.curated.table_name`

**Accessible Information:**
- All column information
- Table properties
- Storage information
- Statistics (if available)

## Limitations

### What You CANNOT Access Without SELECT Permission:
- Actual data values
- Row counts via `SELECT COUNT(*)`
- Data quality metrics (null percentages, distinct counts)
- Sample data
- Source system distribution (without SELECT)
- Country/region data (without SELECT)

### What You MAY Be Able to Access:
- Table names and structure
- Column names and data types
- Table metadata (format, location, size)
- Schema information
- Comments and descriptions

## Testing Catalog Access

To test what catalog metadata is accessible, you can:

1. **Query information_schema tables:**
   ```sql
   SELECT COUNT(*) 
   FROM system.information_schema.tables 
   WHERE table_schema = 'curated'
   ```

2. **Try DESCRIBE commands:**
   ```sql
   DESCRIBE TABLE work_dynamics.curated.table_name
   DESCRIBE DETAIL work_dynamics.curated.table_name
   ```

3. **Check column metadata:**
   ```sql
   SELECT COUNT(*) 
   FROM system.information_schema.columns 
   WHERE table_schema = 'curated'
   ```

## Expected Results for Inaccessible Tables

Based on typical Databricks Unity Catalog permissions:

| Metadata Type | Likely Accessible | Notes |
|--------------|------------------|-------|
| Table names | ✅ Yes | Via `information_schema.tables` |
| Column names/types | ✅ Yes | Via `information_schema.columns` |
| Table type | ✅ Yes | BASE TABLE vs VIEW |
| Storage format | ✅ Yes | DELTA, PARQUET, etc. |
| Storage location | ⚠️ Maybe | May require additional permissions |
| Row counts | ❌ No | Requires SELECT or statistics |
| DESCRIBE TABLE | ⚠️ Maybe | Depends on metadata permissions |
| DESCRIBE DETAIL | ⚠️ Maybe | Depends on metadata permissions |
| Actual data | ❌ No | Requires SELECT permission |

## Next Steps

To fully explore catalog metadata for inaccessible tables:

1. **Re-authenticate** with Azure AD (if token expired)
2. **Run catalog exploration script** to test what's accessible
3. **Query information_schema** for table and column metadata
4. **Try DESCRIBE commands** on sample inaccessible tables
5. **Document findings** in a catalog metadata report

## Scripts Available

- `explore_catalog_metadata.py` - Tests catalog metadata access for inaccessible tables
- `profile_curated_schema.py` - Already profiled accessible tables

## Authentication Note

If you encounter authentication timeouts:
```bash
az logout
az login --tenant "bfef2b06-d256-4f8e-bd03-8d3687987063" --scope "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
```

Then re-run the catalog exploration script.

