# Ingenious ER Diagram (Mermaid)

This diagram can be viewed in any Mermaid-compatible viewer (GitHub, GitLab, etc.)

```mermaid
erDiagram
    ingenious_analytic_cost_code {
        id PK
        analytic_cost_code_category_id
        code
        created_at
        created_by
        description
    }
    ingenious_analytical_milestone {
        id PK
        archived_at
        archived_by
        created_at
        created_by
        description
    }
    ingenious_budget_changes {
        id PK
        budget_id
        category
        date_of_change
        description
        items
    }
    ingenious_budgets {
        id PK
        categories
        cost_code_lists
        created_at
        created_by
        financeable_sites
    }
    ingenious_buildings {
        id PK
        address
        archived_at
        archived_by
        area_unit
        asset_type
    }
    ingenious_business_units {
        id PK
        children
        description
        is_archived
        name
        updated_at
    }
    ingenious_comp_office_location {
        id PK
        address_line1
        address_line2
        city
        country
        custom_id
    }
    ingenious_companies {
        id PK
        account_type
        address1
        address2
        city
        country_code
    }
    ingenious_contacts {
        id PK
        company_id
        created_at
        email
        first_name
        full_name
    }
    ingenious_contract_changes {
        id PK
        category
        contract_id
        created_at
        custom_id
        description
    }
    ingenious_contract_invoice {
        id PK
        contract_id
        created_at
        custom_id
        description
        end_date
    }
    ingenious_contracts {
        id PK
        client_company_id
        client_contact_id
        contract_holder
        created_at
        custom_id
    }
    ingenious_custom_attributes {
        id PK
        list_id
        name
        options
        type
        updated_at
    }
    ingenious_deleted_resources {
        id PK
        deleted_at
        deleted_by
        resource_id
        resource_type
    }
    ingenious_direct_costs {
        id PK
        assigned_employee_id
    }
    ingenious_employees {
        id PK
        account_type
        account_type_id
        additional_business_units
        assigned_office_location_id
        business_unit
    }
    ingenious_forms {
        id PK
        comment
        completed_at
        completed_by
        created_at
        date
    }
    ingenious_inspection_templates {
        id PK
        created_at
        created_by
        description
        generate_punch_items_on_flagging
        inspection_type
    }
    ingenious_non_contract_invoice {
        id PK
        created_at
    }
    ingenious_portfolios {
        id PK
        client_company_id
        created_at
        currency
        has_land_acquisition
        is_archived
    }
    ingenious_proj_funding_sources {
        id PK
        account_number
        allocated_value
        covered_value
        created_at
        created_by
    }
    ingenious_project_directories {
        project_id
        updated_at
        workspaces
    }
    ingenious_project_journal {
        id PK
        created_at
        created_by
        date
        project_health
        project_id
    }
    ingenious_project_roles {
        id PK
        created_at
        is_archived
        is_assignable_to_employees
        name
        permissions
    }
    ingenious_project_schedules {
        id PK
        created_at
        created_by
        is_main
        name
        project_id
    }
    ingenious_projects {
        id PK
        base_line_end_date
        base_line_start_date
        business_unit_id
        client_company_id
        client_contact_id
    }
    ingenious_projects_sites {
        id PK
        address
        building_id
        created_at
        created_by
        gross_area
    }
    ingenious_punch_items {
        id PK
        ball_in_court_id
    }
    ingenious_survey {
        id PK
        categories
        status
        updated_at
    }
    ingenious_tasks {
        id PK
        actual_date
    }
    ovp_cashflowforecasts {
        CashFlowForecastID
        ClientID
        ProjectNumber
        FiscalYear
        CostType
    }
    ovp_invlogfullclient {
        CCCO
    }
    ovp_preprjctplanningcustmflds {
        PlanningProjectNumber
        BACRisk
        BACCriticality
        BACEnhEmployeeExperience
        BACTimeSensitivity
    }

    ingenious_budget_changes ||--o{ ingenious_budget_changes : "budget_id"
    ingenious_budget_changes ||--o{ ingenious_budgets : "budget_id"
    ingenious_budgets ||--o{ ingenious_project_journal : "project_id"
    ingenious_budgets ||--o{ ingenious_project_roles : "project_id"
    ingenious_budgets ||--o{ ingenious_project_schedules : "project_id"
    ingenious_budgets ||--o{ ingenious_projects : "project_id"
    ingenious_budgets ||--o{ ingenious_projects_sites : "project_id"
    ingenious_buildings ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_comp_office_location ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_companies ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_contract_changes ||--o{ ingenious_contract_changes : "contract_id"
    ingenious_contract_changes ||--o{ ingenious_contract_invoice : "contract_id"
    ingenious_contract_changes ||--o{ ingenious_contracts : "contract_id"
    ingenious_contract_changes ||--o{ ingenious_non_contract_invoice : "contract_id"
    ingenious_contract_changes ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_contract_changes ||--o{ ingenious_project_journal : "project_id"
    ingenious_contract_changes ||--o{ ingenious_project_roles : "project_id"
    ingenious_contract_changes ||--o{ ingenious_project_schedules : "project_id"
    ingenious_contract_changes ||--o{ ingenious_projects : "project_id"
    ingenious_contract_changes ||--o{ ingenious_projects_sites : "project_id"
    ingenious_contract_invoice ||--o{ ingenious_contract_changes : "contract_id"
    ingenious_contract_invoice ||--o{ ingenious_contract_invoice : "contract_id"
    ingenious_contract_invoice ||--o{ ingenious_contracts : "contract_id"
    ingenious_contract_invoice ||--o{ ingenious_non_contract_invoice : "contract_id"
    ingenious_contract_invoice ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_contract_invoice ||--o{ ingenious_project_journal : "project_id"
    ingenious_contract_invoice ||--o{ ingenious_project_roles : "project_id"
    ingenious_contract_invoice ||--o{ ingenious_project_schedules : "project_id"
    ingenious_contract_invoice ||--o{ ingenious_projects : "project_id"
    ingenious_contract_invoice ||--o{ ingenious_projects_sites : "project_id"
    ingenious_contracts ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_contracts ||--o{ ingenious_project_journal : "project_id"
    ingenious_contracts ||--o{ ingenious_project_roles : "project_id"
    ingenious_contracts ||--o{ ingenious_project_schedules : "project_id"
    ingenious_contracts ||--o{ ingenious_projects : "project_id"
    ingenious_contracts ||--o{ ingenious_projects_sites : "project_id"
    ingenious_deleted_resources ||--o{ ingenious_deleted_resources : "resource_id"
    ingenious_direct_costs ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_direct_costs ||--o{ ingenious_project_journal : "project_id"
    ingenious_direct_costs ||--o{ ingenious_project_roles : "project_id"
    ingenious_direct_costs ||--o{ ingenious_project_schedules : "project_id"
    ingenious_direct_costs ||--o{ ingenious_projects : "project_id"
    ingenious_direct_costs ||--o{ ingenious_projects_sites : "project_id"
    ingenious_employees ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_forms ||--o{ ingenious_inspection_templates : "inspection_template_id"
    ingenious_forms ||--o{ ingenious_project_journal : "project_id"
    ingenious_forms ||--o{ ingenious_project_roles : "project_id"
    ingenious_forms ||--o{ ingenious_project_schedules : "project_id"
    ingenious_forms ||--o{ ingenious_projects : "project_id"
    ingenious_forms ||--o{ ingenious_projects_sites : "project_id"
    ingenious_forms ||--o{ ingenious_survey : "survey_id"
    ingenious_non_contract_invoice ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_non_contract_invoice ||--o{ ingenious_project_journal : "project_id"
    ingenious_non_contract_invoice ||--o{ ingenious_project_roles : "project_id"
    ingenious_non_contract_invoice ||--o{ ingenious_project_schedules : "project_id"
    ingenious_non_contract_invoice ||--o{ ingenious_projects : "project_id"
    ingenious_non_contract_invoice ||--o{ ingenious_projects_sites : "project_id"
    ingenious_proj_funding_sources ||--o{ ingenious_project_journal : "project_id"
    ingenious_proj_funding_sources ||--o{ ingenious_project_roles : "project_id"
    ingenious_proj_funding_sources ||--o{ ingenious_project_schedules : "project_id"
    ingenious_proj_funding_sources ||--o{ ingenious_projects : "project_id"
    ingenious_proj_funding_sources ||--o{ ingenious_projects_sites : "project_id"
    ingenious_project_directories ||--o{ ingenious_project_journal : "project_id"
    ingenious_project_directories ||--o{ ingenious_project_roles : "project_id"
    ingenious_project_directories ||--o{ ingenious_project_schedules : "project_id"
    ingenious_project_directories ||--o{ ingenious_projects : "project_id"
    ingenious_project_directories ||--o{ ingenious_projects_sites : "project_id"
    ingenious_project_journal ||--o{ ingenious_project_journal : "project_id"
    ingenious_project_journal ||--o{ ingenious_project_roles : "project_id"
    ingenious_project_journal ||--o{ ingenious_project_schedules : "project_id"
    ingenious_project_journal ||--o{ ingenious_projects : "project_id"
    ingenious_project_journal ||--o{ ingenious_projects_sites : "project_id"
    ingenious_project_schedules ||--o{ ingenious_project_journal : "project_id"
    ingenious_project_schedules ||--o{ ingenious_project_roles : "project_id"
    ingenious_project_schedules ||--o{ ingenious_project_schedules : "project_id"
    ingenious_project_schedules ||--o{ ingenious_projects : "project_id"
    ingenious_project_schedules ||--o{ ingenious_projects_sites : "project_id"
    ingenious_projects ||--o{ ingenious_business_units : "business_unit_id"
    ingenious_projects ||--o{ ingenious_custom_attributes : "custom_id"
    ingenious_projects ||--o{ ingenious_comp_office_location : "office_location_id"
    ingenious_projects_sites ||--o{ ingenious_buildings : "building_id"
    ingenious_projects_sites ||--o{ ingenious_project_journal : "project_id"
    ingenious_projects_sites ||--o{ ingenious_project_roles : "project_id"
    ingenious_projects_sites ||--o{ ingenious_project_schedules : "project_id"
    ingenious_projects_sites ||--o{ ingenious_projects : "project_id"
    ingenious_projects_sites ||--o{ ingenious_projects_sites : "project_id"
    ingenious_punch_items ||--o{ ingenious_project_journal : "project_id"
    ingenious_punch_items ||--o{ ingenious_project_roles : "project_id"
    ingenious_punch_items ||--o{ ingenious_project_schedules : "project_id"
    ingenious_punch_items ||--o{ ingenious_projects : "project_id"
    ingenious_punch_items ||--o{ ingenious_projects_sites : "project_id"
    ingenious_tasks ||--o{ ingenious_project_journal : "project_id"
    ingenious_tasks ||--o{ ingenious_project_roles : "project_id"
    ingenious_tasks ||--o{ ingenious_project_schedules : "project_id"
    ingenious_tasks ||--o{ ingenious_projects : "project_id"
    ingenious_tasks ||--o{ ingenious_projects_sites : "project_id"

```
