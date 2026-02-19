# Ingenious Source System - Entity Relationship Schema

**Total Tables:** 66

**Total Relationships Identified:** 96

---

## Tables

### Ingenious Tables

#### ingenious_analytic_cost_code

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_analytic_cost_code_backup

**Row Count:** 669

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| analytic_cost_code_category_id | string | None |  |
| code | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| description | string | None |  |
| **id** (PK) | string | None |  |
| name | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_analytical_milestone

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_analytical_milestone_backup

**Row Count:** 13

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| archived_at | string | None |  |
| archived_by | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| description | string | None |  |
| **id** (PK) | string | None |  |
| is_required | string | None |  |
| name | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_budget_apprvl_phases

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_budget_changes

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_budget_changes_backup

**Row Count:** 1,423

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| budget_id | string | None |  |
| category | string | None |  |
| date_of_change | string | None |  |
| description | string | None |  |
| **id** (PK) | string | None |  |
| items | string | None |  |
| overall_net_change_value | string | None |  |
| reason | string | None |  |
| status | string | None |  |
| total_value | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_budgets

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_budgets_backup

**Row Count:** 2,044

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| categories | string | None |  |
| cost_code_lists | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| financeable_sites | string | None |  |
| **id** (PK) | string | None |  |
| is_shared | string | None |  |
| items | string | None |  |
| phases | string | None |  |
| project_id | string | None |  |
| status | string | None |  |
| totals | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| has_approved_phase | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_buildings

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_buildings_backup

**Row Count:** 6,288

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| address | string | None |  |
| archived_at | string | None |  |
| archived_by | string | None |  |
| area_unit | string | None |  |
| asset_type | string | None |  |
| campus | string | None |  |
| classification | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| custom_id | string | None |  |
| description | string | None |  |
| generated_id | string | None |  |
| gross_area | string | None |  |
| **id** (PK) | string | None |  |
| is_confidential | string | None |  |
| latitude | string | None |  |
| longitude | string | None |  |
| name | string | None |  |
| occupants | string | None |  |
| owner_company_id | string | None |  |
| owner_contact_id | string | None |  |
| projects_ids | string | None |  |
| rentable_area | string | None |  |
| secondary_classification | string | None |  |
| status | string | None |  |
| subsites | string | None |  |
| tags | string | None |  |
| unit_type | string | None |  |
| unit_value | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| usable_area | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_business_units

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_business_units_backup

**Row Count:** 177

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| children | string | None |  |
| description | string | None |  |
| **id** (PK) | string | None |  |
| is_archived | string | None |  |
| name | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_comp_office_location

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_comp_office_location_backup

**Row Count:** 3,548

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| address_line1 | string | None |  |
| address_line2 | string | None |  |
| city | string | None |  |
| country | string | None |  |
| custom_id | string | None |  |
| **id** (PK) | string | None |  |
| label | string | None |  |
| state | string | None |  |
| updated_at | string | None |  |
| workspace_id | string | None |  |
| zip | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_companies

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_companies_backup

**Row Count:** 2,463

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| account_type | string | None |  |
| address1 | string | None |  |
| address2 | string | None |  |
| city | string | None |  |
| country_code | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| email | string | None |  |
| **id** (PK) | string | None |  |
| is_archived | string | None |  |
| name | string | None |  |
| office_locations | string | None |  |
| phone | string | None |  |
| state | string | None |  |
| tags | string | None |  |
| updated_at | string | None |  |
| website | string | None |  |
| zip | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_contacts

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_contacts_backup

**Row Count:** 7,089

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| company_id | string | None |  |
| created_at | string | None |  |
| email | string | None |  |
| first_name | string | None |  |
| full_name | string | None |  |
| **id** (PK) | string | None |  |
| internal_notes | string | None |  |
| is_archived | string | None |  |
| last_name | string | None |  |
| office_phone | string | None |  |
| prefix | string | None |  |
| status | string | None |  |
| title | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_contract_changes

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_contract_changes_backup

**Row Count:** 2,870

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| category | string | None |  |
| contract_id | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| description | string | None |  |
| due_date | string | None |  |
| **id** (PK) | string | None |  |
| name | string | None |  |
| project_id | string | None |  |
| stage_type | string | None |  |
| status | string | None |  |
| total_value | string | None |  |
| updated_at | string | None |  |
| wbs1 | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_contract_invoice

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_contract_invoice_backup

**Row Count:** 7,647

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| contract_id | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| description | string | None |  |
| end_date | string | None |  |
| gross_value | string | None |  |
| **id** (PK) | string | None |  |
| invoice_date | string | None |  |
| items | string | None |  |
| net_value | string | None |  |
| paid_value | string | None |  |
| project_id | string | None |  |
| start_date | string | None |  |
| status | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| document_ids | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_contracts

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_contracts_backup

**Row Count:** 3,820

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| client_company_id | string | None |  |
| client_contact_id | string | None |  |
| contract_holder | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| effective_date | string | None |  |
| **id** (PK) | string | None |  |
| initiation_date | string | None |  |
| name | string | None |  |
| project_id | string | None |  |
| retention | string | None |  |
| source | string | None |  |
| sov_status | string | None |  |
| status | string | None |  |
| total_value | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| vendor_company_id | string | None |  |
| vendor_contact_id | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| project_sites | string | None |  |
| wbs1 | string | None |  |
| accounting_company_id | string | None |  |
| payment_term_id | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_custom_attributes

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_custom_attributes_backup

**Row Count:** 133

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| list_id | string | None |  |
| name | string | None |  |
| options | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_deleted_resources

**Row Count:** 31,495

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| deleted_at | string | None |  |
| deleted_by | string | None |  |
| **id** (PK) | string | None |  |
| resource_id | string | None |  |
| resource_type | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_direct_costs

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_direct_costs_backup

**Row Count:** 38

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| assigned_employee_id | string | None |  |
| budget_code_id | string | None |  |
| category | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| date | string | None |  |
| documents | string | None |  |
| **id** (PK) | string | None |  |
| mileage | string | None |  |
| name | string | None |  |
| notes | string | None |  |
| paid_by | string | None |  |
| project_id | string | None |  |
| proposal_id | string | None |  |
| related_to | string | None |  |
| status | string | None |  |
| total_value | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_employees

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_employees_backup

**Row Count:** 4,037

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| account_type | string | None |  |
| account_type_id | string | None |  |
| additional_business_units | string | None |  |
| assigned_office_location_id | string | None |  |
| business_unit | string | None |  |
| cell_phone | string | None |  |
| client_company_ids | string | None |  |
| company_id | string | None |  |
| company_name | string | None |  |
| created_at | string | None |  |
| custom_attributes | string | None |  |
| custom_id | string | None |  |
| email | string | None |  |
| first_name | string | None |  |
| **id** (PK) | string | None |  |
| is_admin | string | None |  |
| is_archived | string | None |  |
| last_login | string | None |  |
| last_name | string | None |  |
| office_phone | string | None |  |
| project_roles | string | None |  |
| secondary_email | string | None |  |
| supervisor_id | string | None |  |
| termination_date | string | None |  |
| title | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_forms

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_forms_backup

**Row Count:** 841

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| comment | string | None |  |
| completed_at | string | None |  |
| completed_by | string | None |  |
| created_at | string | None |  |
| date | string | None |  |
| document_ids | string | None |  |
| examination | string | None |  |
| final_result | string | None |  |
| **id** (PK) | string | None |  |
| inspection_template_id | string | None |  |
| inspector_id | string | None |  |
| member_ids | string | None |  |
| originator_id | string | None |  |
| project_id | string | None |  |
| status | string | None |  |
| survey_id | string | None |  |
| title | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_inspection_templates

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_inspection_templates_backup

**Row Count:** 55

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| created_at | string | None |  |
| created_by | string | None |  |
| description | string | None |  |
| generate_punch_items_on_flagging | string | None |  |
| **id** (PK) | string | None |  |
| inspection_type | string | None |  |
| name | string | None |  |
| survey_template_id | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_non_contract_invoice

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_non_contract_invoice_backup

**Row Count:** 846

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| created_at | string | None |  |
| custom_id | string | None |  |
| description | string | None |  |
| end_date | string | None |  |
| gross_value | string | None |  |
| **id** (PK) | string | None |  |
| invoice_date | string | None |  |
| items | string | None |  |
| net_value | string | None |  |
| paid_value | string | None |  |
| project_id | string | None |  |
| start_date | string | None |  |
| status | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| accounting_company_id | string | None |  |
| document_ids | string | None |  |
| payment_term_id | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_portfolios

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_portfolios_backup

**Row Count:** 58

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| client_company_id | string | None |  |
| created_at | string | None |  |
| currency | string | None |  |
| has_land_acquisition | string | None |  |
| **id** (PK) | string | None |  |
| is_archived | string | None |  |
| is_closed | string | None |  |
| name | string | None |  |
| project_ids | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_proj_funding_sources

**Row Count:** 437

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| account_number | string | None |  |
| allocated_value | string | None |  |
| covered_value | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| end_date | string | None |  |
| **id** (PK) | string | None |  |
| name | string | None |  |
| note | string | None |  |
| paid_value | string | None |  |
| project_id | string | None |  |
| provider_id | string | None |  |
| start_date | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| value | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_project_directories

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_project_directories_backup

**Row Count:** 5,566

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| project_id | string | None |  |
| updated_at | string | None |  |
| workspaces | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_project_journal

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_project_journal_backup

**Row Count:** 1,985

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| created_at | string | None |  |
| created_by | string | None |  |
| date | string | None |  |
| **id** (PK) | string | None |  |
| project_health | string | None |  |
| project_id | string | None |  |
| text | string | None |  |
| title | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_project_roles

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_project_roles_backup

**Row Count:** 59

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| created_at | string | None |  |
| **id** (PK) | string | None |  |
| is_archived | string | None |  |
| is_assignable_to_employees | string | None |  |
| name | string | None |  |
| permissions | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_project_schedules

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_project_schedules_backup

**Row Count:** 4,029

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| created_at | string | None |  |
| created_by | string | None |  |
| **id** (PK) | string | None |  |
| is_main | string | None |  |
| name | string | None |  |
| project_id | string | None |  |
| published_at | string | None |  |
| published_by | string | None |  |
| shared_with_persons_ids | string | None |  |
| tickets | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_projects

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_projects_backup

**Row Count:** 5,551

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| base_line_end_date | string | None |  |
| base_line_start_date | string | None |  |
| business_unit_id | string | None |  |
| client_company_id | string | None |  |
| client_contact_id | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| currency | string | None |  |
| custom_attributes | string | None |  |
| custom_attributes_owner | string | None |  |
| custom_id | string | None |  |
| description | string | None |  |
| employees | string | None |  |
| exclusions | string | None |  |
| financial_health | string | None |  |
| forecasted_end_date | string | None |  |
| forecasted_start_date | string | None |  |
| generated_id | string | None |  |
| gross_area | string | None |  |
| health | string | None |  |
| **id** (PK) | string | None |  |
| name | string | None |  |
| office_location_id | string | None |  |
| phase | string | None |  |
| rentable_area | string | None |  |
| risk | string | None |  |
| scheduled_health | string | None |  |
| scope | string | None |  |
| sector | string | None |  |
| status_id | string | None |  |
| status_name | string | None |  |
| tags | string | None |  |
| type | string | None |  |
| unit_of_measure | string | None |  |
| unit_type | string | None |  |
| updated_at | string | None |  |
| usable_area | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_projects_sites

**Row Count:** 1,881

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| address | string | None |  |
| building_id | string | None |  |
| created_at | string | None |  |
| created_by | string | None |  |
| gross_area | string | None |  |
| **id** (PK) | string | None |  |
| jobsite_locations | string | None |  |
| project_id | string | None |  |
| rentable_area | string | None |  |
| subsite_id | string | None |  |
| unit_type | string | None |  |
| unit_value | string | None |  |
| updated_at | string | None |  |
| updated_by | string | None |  |
| usable_area | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| is_primary | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_projects_sites_dummy

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_punch_items

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_punch_items_backup

**Row Count:** 585

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| ball_in_court_id | string | None |  |
| comment | string | None |  |
| created_at | string | None |  |
| documents_ids | string | None |  |
| due_date | string | None |  |
| external_references | string | None |  |
| **id** (PK) | string | None |  |
| internal_id | string | None |  |
| members_ids | string | None |  |
| originator_id | string | None |  |
| project_id | string | None |  |
| punch_list_id | string | None |  |
| responsible_contractor_id | string | None |  |
| stamp_id | string | None |  |
| status | string | None |  |
| title | string | None |  |
| updated_at | string | None |  |
| site_ids | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_punch_lists_list

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_punch_lists_list_backup

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_punch_stamps

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_punch_stamps_backup

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_survey

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_survey_backup

**Row Count:** 657

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| categories | string | None |  |
| **id** (PK) | string | None |  |
| status | string | None |  |
| updated_at | string | None |  |
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| priority | string | None |  |
| score | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

#### ingenious_tasks

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|

#### ingenious_tasks_backup

**Row Count:** 2,032

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| domain_name | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| actual_date | string | None |  |
| anticipated_date | string | None |  |
| ball_in_court_ids | string | None |  |
| base_line_date | string | None |  |
| created_at | string | None |  |
| description | string | None |  |
| documents_ids | string | None |  |
| due_date | string | None |  |
| expected_costs | string | None |  |
| expected_delay_unit | string | None |  |
| expected_delay_value | string | None |  |
| **id** (PK) | string | None |  |
| is_risk | string | None |  |
| members_ids | string | None |  |
| mitigation_strategy | string | None |  |
| name | string | None |  |
| originator_id | string | None |  |
| priority | string | None |  |
| project_id | string | None |  |
| risk_level | string | None |  |
| risk_to | string | None |  |
| scheduled_variance | string | None |  |
| status | string | None |  |
| type | string | None |  |
| updated_at | string | None |  |
| # col_name | data_type | comment |  |
| domain_name | string | None |  |

### Ovp Tables

#### ovp_cashflowforecasts

**Row Count:** 58,922

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| CashFlowForecastID | string | None |  |
| ClientID | string | None |  |
| ProjectNumber | string | None |  |
| FiscalYear | string | None |  |
| CostType | string | None |  |
| Period1 | string | None |  |
| Period2 | string | None |  |
| Period3 | string | None |  |
| Period4 | string | None |  |
| Period5 | string | None |  |
| Period6 | string | None |  |
| Period7 | string | None |  |
| Period8 | string | None |  |
| Period9 | string | None |  |
| Period10 | string | None |  |
| Period11 | string | None |  |
| Period12 | string | None |  |
| CreatedDate | string | None |  |
| CreatedBy | string | None |  |
| UpdatedDate | string | None |  |
| UpdatedBy | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |

#### ovp_invlogfullclient

**Row Count:** 178

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| CCCO | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |

#### ovp_preprjctplanningcustmflds

**Row Count:** 59,148

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| PlanningProjectNumber | string | None |  |
| BACRisk | string | None |  |
| BACCriticality | string | None |  |
| BACEnhEmployeeExperience | string | None |  |
| BACTimeSensitivity | string | None |  |
| BACCWYr1ExpDepr | string | None |  |
| BACCWYr2Depr | string | None |  |
| BACCWYr3Depr | string | None |  |
| BACCWYr4Depr | string | None |  |
| BACCWYr5Depr | string | None |  |
| BACLOBYr1ExpDepr | string | None |  |
| BACLOBYr2Depr | string | None |  |
| BACLOBYr3Depr | string | None |  |
| BACLOBYr4Depr | string | None |  |
| BACLOBYr5Depr | string | None |  |
| BACRecoverableVAT | string | None |  |
| BACMarketPlanningContact | string | None |  |
| BACDecommissioning | string | None |  |
| BACADAWeightedScore | string | None |  |
| BACPropertyID | string | None |  |
| BACCountry | string | None |  |
| BACPortfolioRegion | string | None |  |
| BACLineOfBusiness | string | None |  |
| BACProgramTactic | string | None |  |
| BACRequestorContact | string | None |  |
| BACBaselineCompletionDate | string | None |  |
| BACFCIACIScore | string | None |  |
| BACEnhClientExperience | string | None |  |
| BACGeneralComments | string | None |  |
| BACTotalCWCapital | string | None |  |
| BACTotalCWExpense | string | None |  |
| BACTotalLOBCapital | string | None |  |
| BACTotalLOBExpense | string | None |  |
| BACCapitalDriver | string | None |  |
| BACProjectSubType | string | None |  |
| BACProjectDuration | string | None |  |
| BACTIAllowanceAvailable | string | None |  |
| BACTIAAppliedToRent | string | None |  |
| BACPlannedMigrationMonth | string | None |  |
| BACTacticID | string | None |  |
| BACActionID | string | None |  |
| BACAttachments | string | None |  |
| BACFacilityManager | string | None |  |
| BACLocationInFacility | string | None |  |
| BACCompanyCostCenter | string | None |  |
| BACBusinessJustification | string | None |  |
| BACProjectFacilityPartner | string | None |  |
| BACFundingApprovalDate | string | None |  |
| BACAdminRetail | string | None |  |
| BACSiteStrategy | string | None |  |
| BACSiteStrategyYear | string | None |  |
| BACRequestType | string | None |  |
| BACCREMID | string | None |  |
| BACSpaceCharacteristic | string | None |  |
| BACMarketClassification | string | None |  |
| BACTacticGrouping | string | None |  |
| BACTimeSensitivity2017 | string | None |  |
| BACRisk2017 | string | None |  |
| BACProjectDriver | string | None |  |
| BACFundingSource | string | None |  |
| BACCPTReceiptDate | string | None |  |
| BACEstimateCatego | string | None |  |
| BACBudgetROMInputDate | string | None |  |
| BACProgram | string | None |  |
| TechComplexityLevel | string | None |  |
| EstPeopleMoved | string | None |  |
| EstMeetingConfRooms | string | None |  |
| EstTPUnits | string | None |  |
| EventSpace | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |

---

## Relationships

| From Table | From Column | To Table | To Column | Type | Confidence |
|------------|-------------|----------|-----------|------|------------|
| ingenious_budget_changes_backup | budget_id | ingenious_budget_changes_backup | id | foreign_key | medium |
| ingenious_budget_changes_backup | budget_id | ingenious_budgets_backup | id | foreign_key | medium |
| ingenious_budgets_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_budgets_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_budgets_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_budgets_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_budgets_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_buildings_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_comp_office_location_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_companies_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | contract_id | ingenious_contract_changes_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | contract_id | ingenious_contract_invoice_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | contract_id | ingenious_contracts_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | contract_id | ingenious_non_contract_invoice_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_contract_changes_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_contract_invoice_backup | contract_id | ingenious_contract_changes_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | contract_id | ingenious_contract_invoice_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | contract_id | ingenious_contracts_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | contract_id | ingenious_non_contract_invoice_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_contract_invoice_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_contracts_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_contracts_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_contracts_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_contracts_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_contracts_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_contracts_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_deleted_resources | resource_id | ingenious_deleted_resources | id | foreign_key | medium |
| ingenious_direct_costs_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_direct_costs_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_direct_costs_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_direct_costs_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_direct_costs_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_direct_costs_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_employees_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_forms_backup | inspection_template_id | ingenious_inspection_templates_backup | id | foreign_key | medium |
| ingenious_forms_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_forms_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_forms_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_forms_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_forms_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_forms_backup | survey_id | ingenious_survey_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_non_contract_invoice_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_proj_funding_sources | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_proj_funding_sources | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_proj_funding_sources | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_proj_funding_sources | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_proj_funding_sources | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_project_directories_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_project_directories_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_project_directories_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_project_directories_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_project_directories_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_project_journal_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_project_journal_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_project_journal_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_project_journal_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_project_journal_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_project_schedules_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_project_schedules_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_project_schedules_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_project_schedules_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_project_schedules_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_projects_backup | business_unit_id | ingenious_business_units_backup | id | foreign_key | medium |
| ingenious_projects_backup | office_location_id | ingenious_comp_office_location_backup | id | foreign_key | medium |
| ingenious_projects_backup | custom_id | ingenious_custom_attributes_backup | id | foreign_key | medium |
| ingenious_projects_sites | building_id | ingenious_buildings_backup | id | foreign_key | medium |
| ingenious_projects_sites | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_projects_sites | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_projects_sites | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_projects_sites | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_projects_sites | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_punch_items_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_punch_items_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_punch_items_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_punch_items_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_punch_items_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |
| ingenious_tasks_backup | project_id | ingenious_project_journal_backup | id | foreign_key | medium |
| ingenious_tasks_backup | project_id | ingenious_project_roles_backup | id | foreign_key | medium |
| ingenious_tasks_backup | project_id | ingenious_project_schedules_backup | id | foreign_key | medium |
| ingenious_tasks_backup | project_id | ingenious_projects_backup | id | foreign_key | medium |
| ingenious_tasks_backup | project_id | ingenious_projects_sites | id | foreign_key | medium |

---

## Entity Relationship Diagram (Text Representation)

```

ingenious_analytic_cost_code
----------------------------
  Columns: 

ingenious_analytic_cost_code_backup
-----------------------------------
  PK: id
  Columns: analytic_cost_code_category_id, code, created_at, created_by, description ... (+11 more)

ingenious_analytical_milestone
------------------------------
  Columns: 

ingenious_analytical_milestone_backup
-------------------------------------
  PK: id
  Columns: archived_at, archived_by, created_at, created_by, description ... (+13 more)

ingenious_budget_apprvl_phases
------------------------------
  Columns: 

ingenious_budget_changes
------------------------
  Columns: 

ingenious_budget_changes_backup
-------------------------------
  PK: id
  Columns: budget_id, category, date_of_change, description, id ... (+12 more)
  Relationships:
    -> ingenious_budget_changes_backup via budget_id
    -> ingenious_budgets_backup via budget_id

ingenious_budgets
-----------------
  Columns: 

ingenious_budgets_backup
------------------------
  PK: id
  Columns: categories, cost_code_lists, created_at, created_by, financeable_sites ... (+18 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_buildings
-------------------
  Columns: 

ingenious_buildings_backup
--------------------------
  PK: id
  Columns: address, archived_at, archived_by, area_unit, asset_type ... (+34 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id

ingenious_business_units
------------------------
  Columns: 

ingenious_business_units_backup
-------------------------------
  PK: id
  Columns: children, description, id, is_archived, name ... (+8 more)

ingenious_comp_office_location
------------------------------
  Columns: 

ingenious_comp_office_location_backup
-------------------------------------
  PK: id
  Columns: address_line1, address_line2, city, country, custom_id ... (+13 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id

ingenious_companies
-------------------
  Columns: 

ingenious_companies_backup
--------------------------
  PK: id
  Columns: account_type, address1, address2, city, country_code ... (+20 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id

ingenious_contacts
------------------
  Columns: 

ingenious_contacts_backup
-------------------------
  PK: id
  Columns: company_id, created_at, email, first_name, full_name ... (+16 more)

ingenious_contract_changes
--------------------------
  Columns: 

ingenious_contract_changes_backup
---------------------------------
  PK: id
  Columns: category, contract_id, created_at, custom_id, description ... (+16 more)
  Relationships:
    -> ingenious_contract_changes_backup via contract_id
    -> ingenious_contract_invoice_backup via contract_id
    -> ingenious_contracts_backup via contract_id
    -> ingenious_non_contract_invoice_backup via contract_id
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_contract_invoice
--------------------------
  Columns: 

ingenious_contract_invoice_backup
---------------------------------
  PK: id
  Columns: contract_id, created_at, custom_id, description, end_date ... (+19 more)
  Relationships:
    -> ingenious_contract_changes_backup via contract_id
    -> ingenious_contract_invoice_backup via contract_id
    -> ingenious_contracts_backup via contract_id
    -> ingenious_non_contract_invoice_backup via contract_id
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_contracts
-------------------
  Columns: 

ingenious_contracts_backup
--------------------------
  PK: id
  Columns: client_company_id, client_contact_id, contract_holder, created_at, custom_id ... (+25 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_custom_attributes
---------------------------
  Columns: 

ingenious_custom_attributes_backup
----------------------------------
  PK: id
  Columns: id, list_id, name, options, type ... (+8 more)

ingenious_deleted_resources
---------------------------
  PK: id
  Columns: deleted_at, deleted_by, id, resource_id, resource_type ... (+7 more)
  Relationships:
    -> ingenious_deleted_resources via resource_id

ingenious_direct_costs
----------------------
  Columns: 

ingenious_direct_costs_backup
-----------------------------
  PK: id
  Columns: domain_name, udp_create_ts, udp_update_ts, udp_delete_flag, udp_hash ... (+21 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_employees
-------------------
  Columns: 

ingenious_employees_backup
--------------------------
  PK: id
  Columns: account_type, account_type_id, additional_business_units, assigned_office_location_id, business_unit ... (+28 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id

ingenious_forms
---------------
  Columns: 

ingenious_forms_backup
----------------------
  PK: id
  Columns: comment, completed_at, completed_by, created_at, date ... (+21 more)
  Relationships:
    -> ingenious_inspection_templates_backup via inspection_template_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id
    -> ingenious_survey_backup via survey_id

ingenious_inspection_templates
------------------------------
  Columns: 

ingenious_inspection_templates_backup
-------------------------------------
  PK: id
  Columns: created_at, created_by, description, generate_punch_items_on_flagging, id ... (+11 more)

ingenious_non_contract_invoice
------------------------------
  Columns: 

ingenious_non_contract_invoice_backup
-------------------------------------
  PK: id
  Columns: domain_name, udp_create_ts, udp_update_ts, udp_delete_flag, udp_hash ... (+20 more)
  Relationships:
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_portfolios
--------------------
  Columns: 

ingenious_portfolios_backup
---------------------------
  PK: id
  Columns: client_company_id, created_at, currency, has_land_acquisition, id ... (+12 more)

ingenious_proj_funding_sources
------------------------------
  PK: id
  Columns: account_number, allocated_value, covered_value, created_at, created_by ... (+19 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_project_directories
-----------------------------
  Columns: 

ingenious_project_directories_backup
------------------------------------
  Columns: project_id, updated_at, workspaces, domain_name, udp_create_ts ... (+5 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_project_journal
-------------------------
  Columns: 

ingenious_project_journal_backup
--------------------------------
  PK: id
  Columns: created_at, created_by, date, id, project_health ... (+12 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_project_roles
-----------------------
  Columns: 

ingenious_project_roles_backup
------------------------------
  PK: id
  Columns: created_at, id, is_archived, is_assignable_to_employees, name ... (+9 more)

ingenious_project_schedules
---------------------------
  Columns: 

ingenious_project_schedules_backup
----------------------------------
  PK: id
  Columns: created_at, created_by, id, is_main, name ... (+13 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_projects
------------------
  Columns: 

ingenious_projects_backup
-------------------------
  PK: id
  Columns: base_line_end_date, base_line_start_date, business_unit_id, client_company_id, client_contact_id ... (+39 more)
  Relationships:
    -> ingenious_business_units_backup via business_unit_id
    -> ingenious_custom_attributes_backup via custom_id
    -> ingenious_comp_office_location_backup via office_location_id

ingenious_projects_sites
------------------------
  PK: id
  Columns: address, building_id, created_at, created_by, gross_area ... (+18 more)
  Relationships:
    -> ingenious_buildings_backup via building_id
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_projects_sites_dummy
------------------------------
  Columns: 

ingenious_punch_items
---------------------
  Columns: 

ingenious_punch_items_backup
----------------------------
  PK: id
  Columns: domain_name, udp_create_ts, udp_update_ts, udp_delete_flag, udp_hash ... (+20 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ingenious_punch_lists_list
--------------------------
  Columns: 

ingenious_punch_lists_list_backup
---------------------------------
  Columns: 

ingenious_punch_stamps
----------------------
  Columns: 

ingenious_punch_stamps_backup
-----------------------------
  Columns: 

ingenious_survey
----------------
  Columns: 

ingenious_survey_backup
-----------------------
  PK: id
  Columns: categories, id, status, updated_at, domain_name ... (+8 more)

ingenious_tasks
---------------
  Columns: 

ingenious_tasks_backup
----------------------
  PK: id
  Columns: domain_name, udp_create_ts, udp_update_ts, udp_delete_flag, udp_hash ... (+27 more)
  Relationships:
    -> ingenious_project_journal_backup via project_id
    -> ingenious_project_roles_backup via project_id
    -> ingenious_project_schedules_backup via project_id
    -> ingenious_projects_backup via project_id
    -> ingenious_projects_sites via project_id

ovp_cashflowforecasts
---------------------
  Columns: CashFlowForecastID, ClientID, ProjectNumber, FiscalYear, CostType ... (+20 more)

ovp_invlogfullclient
--------------------
  Columns: CCCO, udp_create_ts, udp_update_ts, udp_delete_flag, udp_hash

ovp_preprjctplanningcustmflds
-----------------------------
  Columns: PlanningProjectNumber, BACRisk, BACCriticality, BACEnhEmployeeExperience, BACTimeSensitivity ... (+68 more)
```

---

## Summary Statistics

- **Total Tables:** 66
- **Total Columns:** 756
- **Total Rows:** 216,584
- **Tables with Primary Keys:** 29
- **Identified Relationships:** 96
- **Average Columns per Table:** 11.5
