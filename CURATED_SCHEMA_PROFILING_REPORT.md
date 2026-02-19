# Curated Schema Data Profiling Report

**Schema:** `work_dynamics.curated`

**Total Tables:** 100

**Accessible Tables:** 8

**Total Rows:** 23,963,691

**Total Columns:** 252

---

## Summary Statistics

### Tables by Row Count Range

| Range | Count |
|-------|-------|
| 0 | 0 |
| 1-100 | 0 |
| 101-1K | 0 |
| 1K-10K | 0 |
| 10K-100K | 3 |
| 100K-1M | 0 |
| 1M+ | 5 |

### Top 20 Tables by Row Count

| Table Name | Row Count | Column Count |
|------------|-----------|--------------|
| commitment | 5,768,034 | 55 |
| budgetdetail | 5,661,644 | 53 |
| budgetchange | 5,645,852 | 36 |
| budgetforecast | 5,554,130 | 22 |
| directorycontactprojectlnk | 1,186,886 | 21 |
| companysourcesystemrelationship | 68,867 | 9 |
| customvalue | 41,719 | 23 |
| costsave | 36,559 | 33 |

---

## Detailed Table Profiles

### accountbalances

*Table not accessible (permission denied or doesn't exist)*

---

### accounthierarchy

*Table not accessible (permission denied or doesn't exist)*

---

### accountledger

*Table not accessible (permission denied or doesn't exist)*

---

### accountmaster

*Table not accessible (permission denied or doesn't exist)*

---

### accountmastercategory

*Table not accessible (permission denied or doesn't exist)*

---

### accountpayableledger

*Table not accessible (permission denied or doesn't exist)*

---

### action

*Table not accessible (permission denied or doesn't exist)*

---

### address

*Table not accessible (permission denied or doesn't exist)*

---

### addresstosmartzone

*Table not accessible (permission denied or doesn't exist)*

---

### adl_active_pipeline_snapshot_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_bookings_detail_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_bookings_summary_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_netsuite_booking_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_netsuite_net_revenue_retention_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_netsuite_revenue_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_pipeline_silver

*Table not accessible (permission denied or doesn't exist)*

---

### adl_pipeline_walk_dssf_silver

*Table not accessible (permission denied or doesn't exist)*

---

### altchartofaccounts

*Table not accessible (permission denied or doesn't exist)*

---

### alternateaccount

*Table not accessible (permission denied or doesn't exist)*

---

### alternatebusinessunit

*Table not accessible (permission denied or doesn't exist)*

---

### annualcost

*Table not accessible (permission denied or doesn't exist)*

---

### answer

*Table not accessible (permission denied or doesn't exist)*

---

### approvaltemplate

*Table not accessible (permission denied or doesn't exist)*

---

### areaemployeestatistics

*Table not accessible (permission denied or doesn't exist)*

---

### asset

*Table not accessible (permission denied or doesn't exist)*

---

### assetattributes

*Table not accessible (permission denied or doesn't exist)*

---

### assetattributestemplates

*Table not accessible (permission denied or doesn't exist)*

---

### assetlog

*Table not accessible (permission denied or doesn't exist)*

---

### assignments

*Table not accessible (permission denied or doesn't exist)*

---

### assumptions

*Table not accessible (permission denied or doesn't exist)*

---

### auditeecustomfield

*Table not accessible (permission denied or doesn't exist)*

---

### auditlosttime

*Table not accessible (permission denied or doesn't exist)*

---

### autodispatch

*Table not accessible (permission denied or doesn't exist)*

---

### bid

*Table not accessible (permission denied or doesn't exist)*

---

### billingevent

*Table not accessible (permission denied or doesn't exist)*

---

### billingeventitem

*Table not accessible (permission denied or doesn't exist)*

---

### budget_opportunity

*Table not accessible (permission denied or doesn't exist)*

---

### budget_projects

*Table not accessible (permission denied or doesn't exist)*

---

### budgetchange

**Row Count:** 5,645,852

**Column Count:** 36

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| approvedamount | double | None |
| approvedprojectamount | double | None |
| workitemidentifier | string | None |
| currencytypecode | string | None |
| declinedamount | double | None |
| declinedprojectamount | double | None |
| exchangerate | double | None |
| fundstransferindicator | string | None |
| numericdatatransitionindicator | string | None |
| pendingamount | double | None |
| pendingprojectamount | double | None |
| reimbursableindicator | string | None |
| submissiondate | timestamp | None |
| submittinguseridentifier | string | None |
| transfertotaskidentifier | string | None |
| id | string | None |
| sourcebudgetchangeidentifier | string | None |
| changename | string | None |
| sourcecreatedby | string | None |
| sourcecreateddatetime | timestamp | None |

*... and 16 more columns*

**Column Statistics (Sample):**

| Column | Data Type | Null % | Distinct | Sample Values |
|--------|-----------|--------|----------|---------------|
| approvedamount | double | 98.3% | 59050 | 3400.0, -2817.27, 25000.0 |
| approvedprojectamount | double | 85.4% | 57942 | 20296.0, 48729.6, 5201.04 |
| workitemidentifier | string | 85.5% | 763950 | a49937084f2176f9ce516871e2fc5277, c72a9271ad4a763aea6a5fb6d44e1223, b9892c51caf8cce484988dab0593a8bb |
| currencytypecode | string | 85.6% | 62 | USD, USD, USD |
| declinedamount | double | 99.9% | 436 | 0.0, 0.0, 19748.0 |
| declinedprojectamount | double | 85.5% | 389 | 0.0, 0.0, 0.0 |
| exchangerate | double | 85.4% | 23 | 1.0, 1.0, 1.0 |
| fundstransferindicator | string | 85.4% | 4 | false, false, false |
| numericdatatransitionindicator | string | 100.0% | 2 | false, false, False |
| pendingamount | double | 99.9% | 1639 | 0.0, 0.0, 0.0 |

---

### budgetdetail

**Row Count:** 5,661,644

**Column Count:** 53

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| sourcebudgetdetailidentifier | string | None |
| workitemidentifier | string | None |
| budgetitemname | string | None |
| unitcount | int | None |
| unitofmeasurecode | string | None |
| perunitcostamount | double | None |
| totalbudgetcostamount | double | None |
| totalapprovedbudgetamount | double | None |
| budgetitemdescription | string | None |
| currencytypecode | string | None |
| budgetcurrencyexchangerate | double | None |
| currencyexchangeratetimestamp | timestamp | None |
| sourcemodifieddatetime | timestamp | None |
| sourcecreateddatetime | timestamp | None |
| sourcecreatedby | string | None |
| sourcemodifiedby | string | None |
| sourcesystemname | string | None |
| udp_create_ts | timestamp | None |
| udp_update_ts | timestamp | None |

*... and 33 more columns*

**Column Statistics (Sample):**

| Column | Data Type | Null % | Distinct | Sample Values |
|--------|-----------|--------|----------|---------------|
| id | string | 0.0% | 5661643 | 23481ea876f5b19368f51fb9a7564d7c, 6ad9dffb908faf758106f5a8a0c6ad93, f5511387404ca50f7b240b3165e2a059 |
| sourcebudgetdetailidentifier | string | 5.8% | 5331371 | C-BD-278374, C-BD-278379, C-BD-616122 |
| workitemidentifier | string | 6.1% | 5272649 | 9fa9a0e747ce1c487c9ab61c7fb4a290, 56dfa08696082ea3d7d174fdbe5e2536, c6f44dee0607542a496051db04f56e78 |
| budgetitemname | string | 5.9% | 55412 | <blank>, <blank>, <blank> |
| unitcount | int | 97.8% | 3757 | 59893, 1, 1 |
| unitofmeasurecode | string | 98.3% | 39 | Item, Each, Each |
| perunitcostamount | double | 97.8% | 56074 | 268.0, 21735.77, 75000.0 |
| totalbudgetcostamount | double | 19.8% | 65644 | 0.0, 0.0, 0.0 |
| totalapprovedbudgetamount | double | 5.9% | 64545 | 0.0, 0.0, 0.0 |
| budgetitemdescription | string | 99.4% | 25728 | JLL Furniture consultant., Build out on floors 6 & 7, IT total equipment costs outlined above, includes tax and shipping. |

---

### budgetforecast

**Row Count:** 5,554,130

**Column Count:** 22

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| sourcebudgetforecastidentifier | string | None |
| budgetitemname | string | None |
| totalbudgetcostamount | double | None |
| totalprojectbudgetcostamount | double | None |
| workitemidentifier | string | None |
| currencytypecode | string | None |
| budgetcurrencyexchangerate | double | None |
| numericdatatransitionindicator | string | None |
| sourcecreatedby | string | None |
| sourcecreatedon | timestamp | None |
| sourcemodifiedby | string | None |
| sourcemodifiedon | timestamp | None |
| sourcesystemname | string | None |
| udp_create_ts | timestamp | None |
| udp_update_ts | timestamp | None |
| isdeleted | string | None |
| udp_delete_flag | string | None |
| udp_hash | string | None |
| sourcesystem | string | None |

*... and 2 more columns*

**Column Statistics (Sample):**

| Column | Data Type | Null % | Distinct | Sample Values |
|--------|-----------|--------|----------|---------------|
| id | string | 0.0% | 5554130 | 7237959ebdf0e93e7c3af9c683eaa4ea, 72380433c5157d0fc53348294333a2ca, 723857294a72d0207782ccc875d4318f |
| sourcebudgetforecastidentifier | string | 5.8% | 5232498 | C-BF-3400251, C-BF-5708019, C-BF-1648248 |
| budgetitemname | string | 5.8% | 10985 | <blank>, <blank>, <blank> |
| totalbudgetcostamount | double | 99.7% | 7060 | 8273.0, 0.0, 0.0 |
| totalprojectbudgetcostamount | double | 5.8% | 7082 | 0.0, 0.0, 0.0 |
| workitemidentifier | string | 5.9% | 5219290 | 1da569d2a8cd2c71cb212ea5203891f1, cb9dad2c78d974967b36eb0d18f47ecd, 29d51bc00bd7ecdc8e1673dc9b9fc126 |
| currencytypecode | string | 5.8% | 78 | USD, PEN, USD |
| budgetcurrencyexchangerate | double | 5.8% | 35 | 1.0, 1.0, 1.0 |
| numericdatatransitionindicator | string | 100.0% | 2 | false, false, False |
| sourcecreatedby | string | 5.8% | 1722 | 634db9286ef9275707b69152de77c4aa, 1ae5027b8281be034d36977e67dda1aa, 493a898edd3b6db97899f56f3e96aed1 |

---

### businessunit

*Table not accessible (permission denied or doesn't exist)*

---

### businessunitcategory

*Table not accessible (permission denied or doesn't exist)*

---

### businessunitsmasterproperty

*Table not accessible (permission denied or doesn't exist)*

---

### businessunittag

*Table not accessible (permission denied or doesn't exist)*

---

### busline

*Table not accessible (permission denied or doesn't exist)*

---

### cad_simulationdm

*Table not accessible (permission denied or doesn't exist)*

---

### case

*Table not accessible (permission denied or doesn't exist)*

---

### changerequest

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdgemvw

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdleaseareacategory

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdleasecostcategory

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdleaseeventcategory

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdoscrevw

*Table not accessible (permission denied or doesn't exist)*

---

### colb_wdspacetypeoscremappingvw

*Table not accessible (permission denied or doesn't exist)*

---

### commercialcontract

*Table not accessible (permission denied or doesn't exist)*

---

### commissions

*Table not accessible (permission denied or doesn't exist)*

---

### commitment

**Row Count:** 5,768,034

**Column Count:** 55

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| sourcecommitmentidentifier | string | None |
| commitmentname | string | None |
| adjustedcontractamount | double | None |
| approvedamount | double | None |
| approvedprojectamount | double | None |
| approvedsaveamount | double | None |
| approvedvariationamount | double | None |
| balancetofinishamount | double | None |
| changeordertext | string | None |
| workitemidentifier | string | None |
| currencytypecode | string | None |
| declinedamount | double | None |
| declinedprojectamount | double | None |
| exchangedate | timestamp | None |
| exchangeratepercent | double | None |
| finishdate | timestamp | None |
| keycontracttermstext | string | None |
| lesspreviouspaymentsamount | double | None |
| numericdatatransitionindicator | string | None |

*... and 35 more columns*

---

### commitmentchanges

*Table not accessible (permission denied or doesn't exist)*

---

### companybusinessunit

*Table not accessible (permission denied or doesn't exist)*

---

### companyclient

*Table not accessible (permission denied or doesn't exist)*

---

### companyclientextended

*Table not accessible (permission denied or doesn't exist)*

---

### companycontact

*Table not accessible (permission denied or doesn't exist)*

---

### companycustomfms

*Table not accessible (permission denied or doesn't exist)*

---

### companyextended

*Table not accessible (permission denied or doesn't exist)*

---

### companyorganisation

*Table not accessible (permission denied or doesn't exist)*

---

### companyorganisationassignment

*Table not accessible (permission denied or doesn't exist)*

---

### companyorganisationassignmentcustomfms

*Table not accessible (permission denied or doesn't exist)*

---

### companyorganisationcustomfms

*Table not accessible (permission denied or doesn't exist)*

---

### companysourcesystemrelationship

**Row Count:** 68,867

**Column Count:** 9

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| companyidentifier | string | None |
| sourcesystem | string | None |
| targetsystem | string | None |
| targetsystemidentifier | string | None |
| targetsystementity | string | None |
| udp_hash | string | None |
| # col_name | data_type | comment |
| sourcesystem | string | None |

---

### contactextended

*Table not accessible (permission denied or doesn't exist)*

---

### contract

*Table not accessible (permission denied or doesn't exist)*

---

### conversionunit

*Table not accessible (permission denied or doesn't exist)*

---

### costcentre

*Table not accessible (permission denied or doesn't exist)*

---

### costmetrics

*Table not accessible (permission denied or doesn't exist)*

---

### costsave

**Row Count:** 36,559

**Column Count:** 33

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| sourcecostsaveidentifier | string | None |
| submitteruseridentifier | string | None |
| submissiondate | timestamp | None |
| categorycode | string | None |
| vendoridentifier | string | None |
| costsavingoravoidancedescription | string | None |
| recurringpaymentperiodicfrequencyindicator | string | None |
| periodicfrequencytext | string | None |
| costsavingvalueamount | double | None |
| statusname | string | None |
| statusdate | timestamp | None |
| updatemanageruseridentifier | string | None |
| commenttext | string | None |
| costsavingdescription | string | None |
| costsavingname | string | None |
| sourcemodifieddatetime | timestamp | None |
| sourcecreateddatetime | timestamp | None |
| sourcecreatedby | string | None |
| sourcemodifiedby | string | None |

*... and 13 more columns*

---

### costtype

*Table not accessible (permission denied or doesn't exist)*

---

### cs_employee

*Table not accessible (permission denied or doesn't exist)*

---

### currencyexchangerate

*Table not accessible (permission denied or doesn't exist)*

---

### customattribute

*Table not accessible (permission denied or doesn't exist)*

---

### customer

*Table not accessible (permission denied or doesn't exist)*

---

### customergroups

*Table not accessible (permission denied or doesn't exist)*

---

### customergroupslinkage

*Table not accessible (permission denied or doesn't exist)*

---

### customfield

*Table not accessible (permission denied or doesn't exist)*

---

### customvalue

**Row Count:** 41,719

**Column Count:** 23

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| sourcecustomvalueidentifier | string | None |
| customvaluetext | string | None |
| sourcecreatedby | string | None |
| sourcemodifiedby | string | None |
| entityowneruseridentifier | string | None |
| companyidentifier | string | None |
| propertyidentifier | string | None |
| sourcecreateddatetime | timestamp | None |
| sourcemodifieddatetime | timestamp | None |
| customvaluename | string | None |
| customvaluedescription | string | None |
| customvaluefieldname | string | None |
| customvalueattributeweightedscore | double | None |
| customvalueattributescore | double | None |
| sourcesystem | string | None |
| isdeleted | string | None |
| udp_create_ts | timestamp | None |
| udp_update_ts | timestamp | None |
| udp_delete_flag | string | None |

*... and 3 more columns*

---

### datefiscalpatterns

*Table not accessible (permission denied or doesn't exist)*

---

### dealdetails

*Table not accessible (permission denied or doesn't exist)*

---

### directorycontactprojectlnk

**Row Count:** 1,186,886

**Column Count:** 21

**Columns:**

| Column Name | Data Type | Nullable |
|-------------|-----------|----------|
| id | string | None |
| spendroleidentifer | string | None |
| sourcecreatedby | string | None |
| sourcecreateddatetime | timestamp | None |
| externaltext | string | None |
| sourcemodifiedby | string | None |
| sourcemodifieddatetime | timestamp | None |
| contactidentifier | string | None |
| projectidentifier | string | None |
| projectroleidentifier | string | None |
| udp_hash | string | None |
| projectroletext | string | None |
| status | string | None |
| companycategory | string | None |
| sourcesystem | string | None |
| udp_delete_flag | string | None |
| udp_create_ts | timestamp | None |
| udp_update_ts | timestamp | None |
| domainname | string | None |
| # col_name | data_type | comment |

*... and 1 more columns*

---

### document

*Table not accessible (permission denied or doesn't exist)*

---

### dssf_invoice_details

*Table not accessible (permission denied or doesn't exist)*

---

### dssf_opplineitem_processed

*Table not accessible (permission denied or doesn't exist)*

---

### dssf_opportunity_processed

*Table not accessible (permission denied or doesn't exist)*

---

### dssf_report_project

*Table not accessible (permission denied or doesn't exist)*

---

### electronicaddress

*Table not accessible (permission denied or doesn't exist)*

---

### employeefuturemove

*Table not accessible (permission denied or doesn't exist)*

---

### employeefuturemovecustomfms

*Table not accessible (permission denied or doesn't exist)*

---

### employeehistoricmove

*Table not accessible (permission denied or doesn't exist)*

---

### employeehistoricmovecustomfms

*Table not accessible (permission denied or doesn't exist)*

---

### enhancementrequest

*Table not accessible (permission denied or doesn't exist)*

---

### equipment

*Table not accessible (permission denied or doesn't exist)*

---

