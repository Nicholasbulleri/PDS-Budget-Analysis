# EDP Integrated Systems Analysis Report

## Executive Summary

The JLL Enterprise Data Platform (EDP) has **229 integrated source systems** organized in the `edp_sourcesystem` catalog. Each system has its own schema within this catalog, representing data sources that feed into the platform.

## Total Systems: 229

## Systems by Category

### Project Management (4 systems)
- **clarizen** - Project management and collaboration
- **ingenious** - Project and development services
- **pega** - Business process management
- **workfront** - Work management platform

### Property/Facilities Management (16 systems)
- **archibus** - Facilities management
- **corrigo** - Facilities and property management
- **corrigo-staging** - Corrigo staging environment
- **corrigotest** - Corrigo test environment
- **costar** - Commercial real estate data
- **leasingos** - Leasing operations
- **leasingos_amer** - Leasing operations (Americas)
- **mri** - Property management software
- **mriau** - MRI (Australia)
- **mrisg** - MRI (Singapore)
- **mrith** - MRI (Thailand)
- **prism** - Property management system
- **reonomy** - Property intelligence
- **tririga** - Integrated workplace management
- **vts** - Lease management
- **yardi** - Property management

### CRM/Sales (11 systems)
- **be_salesforce** - Salesforce (Business Europe)
- **brazilsalesforce** - Salesforce (Brazil)
- **crm365** - Microsoft Dynamics CRM
- **dssf** - Salesforce
- **eloqua** - Marketing automation
- **emea_salesforce** - Salesforce (EMEA)
- **leadgenius** - Lead generation
- **marketing_leads** - Marketing lead data
- **oval** - Sales opportunity management tool (similar to Salesforce)
- **zoom** - Video conferencing (likely for sales)
- **zoominfo** - B2B contact database

### Finance/ERP (8 systems)
- **e1** - Enterprise resource planning
- **ffs** - APAC revenue forecasting system
- **jll** - JLL internal finance
- **jll_finance** - JLL finance systems
- **netsuite** - Cloud ERP
- **peoplesoft** - Enterprise software
- **sage_intacct** - Financial management
- **tm1** - IBM Planning Analytics

### Research/Data (9 systems)
- **car** - Commercial real estate data
- **catastro** - Property registry (Spain)
- **debtinsight** - Debt market data
- **definitive_healthcare** - Healthcare data
- **preqin** - Alternative assets data
- **rca** - Real Capital Analytics
- **registro** - Property registry
- **str** - Hotel/real estate data
- **uklandregistry** - UK Land Registry

### Analytics/BI (6 systems)
- **alteryx** - Data analytics platform
- **medallia** - Customer experience
- **powerbi** - Microsoft Power BI
- **qualtrics** - Experience management
- **splunk** - Data analytics platform
- **tableau** - Business intelligence

### Marketing (6 systems)
- **ado** - Marketing platform
- **adobe_analytics** - Web analytics
- **facebook** - Social media data
- **linkedin** - Professional network data
- **sproutsocial** - Social media management
- **twitter** - Social media data

### Procurement/Vendor (5 systems)
- **aravo** - Supplier management
- **avetta** - Supply chain risk management
- **isn** - Contractor management
- **jaggaer** - Procurement software
- **jaggaeradvantage** - Jaggaer Advantage module

### ESG/Sustainability (5 systems)
- **breeam** - Building sustainability assessment
- **envizi** - ESG data management
- **epc** - Energy Performance Certificate
- **esgmet** - ESG metrics
- **ukdomesticepc** - UK domestic EPC

### Collaboration (3 systems)
- **outlook** - Microsoft Outlook
- **sharepoint** - Microsoft SharePoint
- **webex** - Cisco Webex

### Compliance/Legal (4 systems)
- **cmo** - Legacy health and safety system
- **fortify** - Security software
- **legal** - Legal systems
- **sec** - SEC filings/data

### Development/IT (3 systems)
- **github** - Code repository
- **service_now_tables** - ServiceNow IT service management
- **zendesk** - Customer support

### Customer Experience (2 systems)
- **pendo** - Product analytics
- **totango** - Customer success platform

### Document Management (1 system)
- **box** - Cloud content management

### HR/People (1 system)
- **workday** - Human capital management

### Other/Unknown (147 systems)
Many additional systems including:
- Regional research systems (belux_research, de_research, emea_research, fr_research, etc.)
- Property data systems (propertydata, propertyhub, property_lite)
- Various internal JLL systems (jlltracker, jllreferencedata, jlllocalcomps)
- Data processing systems (curated, analytical, data, data1, data2)
- And many more specialized systems

**Note**: Systems not found in catalog:
- **donesafe** - Not found in edp_sourcesystem catalog
- **cost x** - Not found in edp_sourcesystem catalog (only `costar` exists)

## Active Systems (with data in curated tables)

Based on analysis of curated consumption tables, the following systems are actively providing data:

- **clarizen** - 249,544 project records
- **ingenious** - 5,189 project records

## Key Findings

1. **Scale**: 229 integrated systems represents a comprehensive data integration platform
2. **Diversity**: Systems span multiple business functions (PM, CRM, Finance, Property, etc.)
3. **Regional Coverage**: Multiple regional variants (e.g., mriau, mrisg, mrith for different countries)
4. **Environment Separation**: Staging and test environments (corrigo-staging, corrigotest)
5. **Data Processing Layers**: Analytical and curated schemas indicate data transformation pipelines

## Recommendations

1. **Documentation**: Create detailed documentation for each system's purpose and data flow
2. **Data Quality**: Implement monitoring for systems with data in curated tables
3. **Consolidation**: Review if some systems can be consolidated or retired
4. **Governance**: Establish data governance policies for the 229 systems

