# Ingenious Curated Consumption Views - Entity Relationship Schema

**Total Views:** 25

**Total Relationships Identified:** 1

---

## Views

#### vw_ingenious_answer

**Row Count:** 12,649

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceansweridentifier | string | None |  |
| incidentidentifier | string | None |  |
| auditquestionidentifier | string | None |  |
| auditansweridentifier | string | None |  |
| sourceincidentidentifier | string | None |  |
| answervalue | string | None |  |
| answertext | string | None |  |
| answerscore | double | None |  |
| questionidentifier | string | None |  |
| questionuniqueidentifier | string | None |  |
| questionscore | string | None |  |
| questiontext | string | None |  |
| qcimpact | string | None |  |
| tetrisflag | string | None |  |
| project | string | None |  |
| homeofficeflag | string | None |  |
| qtemplatename | string | None |  |
| specificstatusidentifier | string | None |  |
| sectionname | string | None |  |
| sourcesystem | string | None |  |
| udp_update_ts | timestamp | None |  |
| udp_create_ts | timestamp | None |  |
| udp_hash | string | None |  |
| udp_delete_flag | string | None |  |
| companyidentifier | string | None |  |
| answerdate | timestamp | None |  |
| answerstatus | string | None |  |
| useridentifier | string | None |  |
| surveyidentifier | string | None |  |
| title | string | None |  |
| surveystatus | string | None |  |
| status | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourceactionlogsid | string | None |  |
| actionlogsnote | string | None |  |
| actionlogstype | string | None |  |
| answernote | string | None |  |
| sourcecategoryid | string | None |  |
| sourcedocumentsid | string | None |  |
| optioncontent | string | None |  |
| optionflag | string | None |  |
| sourceoptionid | string | None |  |
| sourcepunchitemsid | string | None |  |
| questionisrequired | string | None |  |
| questiontype | string | None |  |
| selectedoptioncontent | string | None |  |
| selectedoptionflag | string | None |  |
| sourceselectedoptionid | string | None |  |
| sourceupdateddatetime | timestamp | None |  |
| domainname | string | None |  |

#### vw_ingenious_budgetchange

**Row Count:** 2,580

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| approvedamount | double | None |  |
| approvedprojectamount | double | None |  |
| workitemidentifier | string | None |  |
| currencytypecode | string | None |  |
| declinedamount | double | None |  |
| declinedprojectamount | double | None |  |
| exchangerate | double | None |  |
| fundstransferindicator | string | None |  |
| numericdatatransitionindicator | string | None |  |
| pendingamount | double | None |  |
| pendingprojectamount | double | None |  |
| reimbursableindicator | string | None |  |
| submissiondate | timestamp | None |  |
| submittinguseridentifier | string | None |  |
| transfertotaskidentifier | string | None |  |
| **id** (PK) | string | None |  |
| sourcebudgetchangeidentifier | string | None |  |
| changename | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| isdeleted | string | None |  |
| sourcesystemname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| sourcesystem | string | None |  |
| budgetidentifier | string | None |  |
| domainname | string | None |  |
| sourcecostcode | string | None |  |
| targetcostcode | string | None |  |
| description | string | None |  |

#### vw_ingenious_budgetdetail

**Row Count:** 3,202

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcebudgetdetailidentifier | string | None |  |
| workitemidentifier | string | None |  |
| budgetitemname | string | None |  |
| unitcount | int | None |  |
| unitofmeasurecode | string | None |  |
| perunitcostamount | double | None |  |
| totalbudgetcostamount | double | None |  |
| totalapprovedbudgetamount | double | None |  |
| budgetitemdescription | string | None |  |
| currencytypecode | string | None |  |
| budgetcurrencyexchangerate | double | None |  |
| currencyexchangeratetimestamp | timestamp | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcecreatedby | string | None |  |
| sourcemodifiedby | string | None |  |
| sourcesystemname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| isdeleted | string | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| sourceitemid | string | None |  |
| projectidentifier | string | None |  |
| categoryname | string | None |  |
| sourcecategoryid | string | None |  |
| code | string | None |  |
| sourcecodeid | string | None |  |
| codename | string | None |  |
| sourcesystem | string | None |  |
| totalpendingamount | double | None |  |
| totalbudgetoriginalamount | double | None |  |
| totalbudgetcurrentamount | double | None |  |
| totalbudgetprojectedamount | double | None |  |
| variancetothebudgetamount | double | None |  |
| totalvalue | double | None |  |
| currentretentionamount | double | None |  |
| grossbalancetocompleteamount | double | None |  |
| grosscurrentapplicationamount | double | None |  |
| grosspreviousapplicationsamount | double | None |  |
| grosstotalcompletedandstoredamount | double | None |  |
| materialstoredoffsiteamount | double | None |  |
| materialstoredretentionamount | double | None |  |
| paidamount | double | None |  |
| previousretentionamount | double | None |  |
| totalretentionamount | double | None |  |
| unpaidamount | double | None |  |
| domainname | string | None |  |
| dateofchange | timestamp | None |  |
| budgetidentifier | string | None |  |

#### vw_ingenious_businessunit

**Row Count:** 177

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcebusinessunitidentifier | string | None |  |
| companyidentifier | string | None |  |
| addressidentifier | string | None |  |
| addressjobarnumber | string | None |  |
| businessunittypecode | string | None |  |
| accountlevelnumber | string | None |  |
| businessunitname | string | None |  |
| businessunithierarchylevel1 | string | None |  |
| businessunithierarchylevel2 | string | None |  |
| businessunithierarchylevel3 | string | None |  |
| businessunithierarchylevel4 | string | None |  |
| businessunitdescription | string | None |  |
| businessunitdescription02 | string | None |  |
| businessunitdescription03 | string | None |  |
| businessunitdescription04 | string | None |  |
| businessunitshortdescription | string | None |  |
| category | string | None |  |
| segment | string | None |  |
| departmenttype | string | None |  |
| division | string | None |  |
| group | string | None |  |
| lineofbusiness | string | None |  |
| clientbusinessunit | string | None |  |
| personresponsible | string | None |  |
| postingallowedindicator | string | None |  |
| region | string | None |  |
| state | string | None |  |
| subledgernotallowedindicator | string | None |  |
| branchofficecode | string | None |  |
| lastupdatedatetime | timestamp | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| sourcecompanyidentifier | string | None |  |
| contracttype | string | None |  |
| countrycode | string | None |  |
| subsequentbusinessunit | string | None |  |
| relatedbusinessunit | string | None |  |
| userid | string | None |  |
| sourceaddressidentifier | string | None |  |
| isarchived | boolean | None |  |
| domainname | string | None |  |

#### vw_ingenious_commitment

**Row Count:** 3,797

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcecommitmentidentifier | string | None |  |
| commitmentname | string | None |  |
| adjustedcontractamount | double | None |  |
| approvedamount | double | None |  |
| approvedprojectamount | double | None |  |
| approvedsaveamount | double | None |  |
| approvedvariationamount | double | None |  |
| balancetofinishamount | double | None |  |
| changeordertext | string | None |  |
| workitemidentifier | string | None |  |
| currencytypecode | string | None |  |
| declinedamount | double | None |  |
| declinedprojectamount | double | None |  |
| exchangedate | timestamp | None |  |
| exchangeratepercent | double | None |  |
| finishdate | timestamp | None |  |
| keycontracttermstext | string | None |  |
| lesspreviouspaymentsamount | double | None |  |
| numericdatatransitionindicator | string | None |  |
| originalcontractvalueamount | double | None |  |
| pendingamount | double | None |  |
| pendingprojectamount | double | None |  |
| pendingsaveamount | double | None |  |
| previouspaymentsamount | double | None |  |
| referencenumber | string | None |  |
| reimbursableindicator | string | None |  |
| retentionamount | double | None |  |
| retentionratepercent | double | None |  |
| startdate | timestamp | None |  |
| submissiondate | timestamp | None |  |
| submittinguseridentifier | string | None |  |
| totalinvoicedamount | double | None |  |
| totalpaymentamount | double | None |  |
| valuationcertifiedamount | double | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| isdeleted | string | None |  |
| sourcesystemname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_update_ts | timestamp | None |  |
| udp_hash | string | None |  |
| commitmentdescription | string | None |  |
| totalamount | double | None |  |
| sourcesystem | string | None |  |
| domainname | string | None |  |
| projectedtotalamount | double | None |  |
| status | string | None |  |
| type | string | None |  |
| sovstatus | string | None |  |

#### vw_ingenious_commitmentchanges

**Row Count:** 4,754

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| commitmentchangename | string | None |  |
| totalamount | double | None |  |
| customid | string | None |  |
| commitmentchangedescription | string | None |  |
| costcodename | string | None |  |
| costcodeamount | double | None |  |
| costcodeid | string | None |  |
| status | string | None |  |
| contractid | string | None |  |
| projectid | string | None |  |
| stagetype | string | None |  |
| codename | string | None |  |
| code | string | None |  |
| sourcecategoryid | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourcecreateddatetime | timestamp | None |  |
| isdeleted | string | None |  |
| sourcesystemname | string | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_directorycontactprojectlnk

**Row Count:** 25,886

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| spendroleidentifer | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| externaltext | string | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| contactidentifier | string | None |  |
| projectidentifier | string | None |  |
| projectroleidentifier | string | None |  |
| udp_hash | string | None |  |
| projectroletext | string | None |  |
| status | string | None |  |
| companycategory | string | None |  |
| sourcesystem | string | None |  |
| udp_delete_flag | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| domainname | string | None |  |

#### vw_ingenious_generictask

**Row Count:** 127,630

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcetaskidentifer | string | None |  |
| totalinvoicesamount | double | None |  |
| costcode | string | None |  |
| taskname | string | None |  |
| capitalexpense | string | None |  |
| costcodetype | int | None |  |
| originalbudgetamount | double | None |  |
| approvedchangesandtransfersamount | double | None |  |
| totalapprovedbudgetamount | double | None |  |
| pendingchangesandtransfersamount | double | None |  |
| totalprojectedbudgetamount | double | None |  |
| approvedcommitmentsamount | double | None |  |
| pendingcommitmentsamount | double | None |  |
| additionalforecastedamount | double | None |  |
| projectedtotalcommitmentsamount | double | None |  |
| anticipatedtocompleteamount | double | None |  |
| varianceofbudgetamount | double | None |  |
| remainingbalanceamount | double | None |  |
| entityowneruseridentifier | string | None |  |
| actionitemstatus | string | None |  |
| commentstext | string | None |  |
| typetext | string | None |  |
| prioritytext | string | None |  |
| parentidentifier | string | None |  |
| internaltasktypetext | string | None |  |
| durationdaysnumber | int | None |  |
| actualstartdate | timestamp | None |  |
| actualenddatetime | timestamp | None |  |
| baselinestartdatetime | timestamp | None |  |
| baselineduedatetime | timestamp | None |  |
| startdate | timestamp | None |  |
| duedatetime | timestamp | None |  |
| completedpercent | int | None |  |
| description | string | None |  |
| entitytypetext | string | None |  |
| manageruseridentifier | string | None |  |
| milestoneidentifier | string | None |  |
| projectidentifier | string | None |  |
| templatetext | string | None |  |
| actionitemsprojectidentifier | string | None |  |
| costlinecontractidentifier | string | None |  |
| costnonlaborresourceidentifier | string | None |  |
| meetingidentifier | string | None |  |
| costitemprojectidentifier | string | None |  |
| meetingminutesworkitemidentifier | string | None |  |
| responsiblecontactidentifier | string | None |  |
| transfercostitemcode | string | None |  |
| vendoridentifier | string | None |  |
| statustrackertext | string | None |  |
| statetext | string | None |  |
| phasetext | string | None |  |
| workitemidentifier | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| costperarea | double | None |  |
| totalpendinginvoices | double | None |  |
| totalapprovedinvoices | double | None |  |
| actualduration | double | None |  |
| baselineduration | double | None |  |
| minutecategorytext | string | None |  |
| orderid | string | None |  |
| importancetext | string | None |  |
| copiedtext | double | None |  |
| taskamilestoneindicator | string | None |  |
| taskisconcurrentindicator | string | None |  |
| requiredtaskindicator | string | None |  |
| shrinkabletaskindicator | string | None |  |
| taskoverduedayscount | int | None |  |
| useemailapprovalsindicator | string | None |  |
| usercompletedate | timestamp | None |  |
| transactionidentifier | string | None |  |
| sourcesystem | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| schedulestatus | string | None |  |
| deliverable | string | None |  |
| vendororiginalcost | double | None |  |
| vendorchangeordercost | double | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| sourcetaskmilestonenumber | double | None |  |
| clientgrouping | string | None |  |
| clientassetvalues | string | None |  |
| clientwbscode | string | None |  |
| financialcomplete | string | None |  |
| packagetype | string | None |  |
| ponumber | string | None |  |
| pendingbudgetamount | double | None |  |
| forecaststartdatetime | timestamp | None |  |
| forecastenddatetime | timestamp | None |  |
| costcodename | string | None |  |
| domainname | string | None |  |
| taskcategory | string | None |  |
| forecastduration | double | None |  |
| budgetidentifier | string | None |  |

#### vw_ingenious_inspection

**Row Count:** 836

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceinspectionuiidentifier | string | None |  |
| sourceinspectionidentifier | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| inspectionname | string | None |  |
| deadlinedatetime | timestamp | None |  |
| completeddatetime | timestamp | None |  |
| statusdescription | string | None |  |
| conductedbypartyidentifier | string | None |  |
| propertyidentifier | string | None |  |
| organizationreferenceidentifier | string | None |  |
| recurringfrequencydescription | string | None |  |
| totalcostamount | double | None |  |
| currencycode | string | None |  |
| closeddatetime | timestamp | None |  |
| accountidentifier | string | None |  |
| frequency | string | None |  |
| nextrundatetime | timestamp | None |  |
| lastrundatetime | timestamp | None |  |
| programstatusdescription | string | None |  |
| programname | string | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_hash | string | None |  |
| sourceupdateddatetime | timestamp | None |  |
| udp_delete_flag | boolean | None |  |
| comments | string | None |  |
| inspectiontemplateidentifier | string | None |  |
| inspectoridentifier | string | None |  |
| originatoridentifier | string | None |  |
| projectidentifier | string | None |  |
| surveyidentifier | string | None |  |
| inspectiontype | string | None |  |
| examination | string | None |  |
| inspectionresult | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_inspectionmembers

**Row Count:** 751

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| memberidentifier | string | None |  |
| inspectionidentifier | string | None |  |
| sourcememberidentifier | string | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | boolean | None |  |
| udp_hash | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_inspectiontemplates

**Row Count:** 55

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceinspectiontemplateidentifier | string | None |  |
| description | string | None |  |
| generatepunchitemsonflag | string | None |  |
| inspectiontype | string | None |  |
| templatename | string | None |  |
| surveytemplateidentifier | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcecreatedby | string | None |  |
| sourceupdateddatetime | timestamp | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_locations

**Row Count:** 1,761

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcelocationid | int | None |  |
| databaseid | bigint | None |  |
| address1 | string | None |  |
| address2 | string | None |  |
| city | string | None |  |
| state | string | None |  |
| zipcode | string | None |  |
| country | string | None |  |
| latitude | double | None |  |
| longitude | double | None |  |
| countryname | string | None |  |
| locationtype | string | None |  |
| lastsyncutcdatetime | timestamp | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| associatename | string | None |  |
| address | string | None |  |
| sourceclientname | string | None |  |
| ovcpid | int | None |  |
| customattribute2text | string | None |  |
| customattribute3text | string | None |  |
| customattribute4text | string | None |  |
| customattribute5text | string | None |  |
| regionname | string | None |  |
| locationname | string | None |  |
| locationreferencenumber | string | None |  |
| companyidentifier | string | None |  |
| officelocationid | string | None |  |
| officelabel | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_milestone

**Row Count:** 22,904

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| originalbudgetamount | double | None |  |
| approvedchangesandtransfersamount | double | None |  |
| totalapprovedbudgetamount | double | None |  |
| pendingchangesandtransfersamount | double | None |  |
| totalprojectedbudgetamount | double | None |  |
| approvedcommitmentsamount | double | None |  |
| pendingcommitmentsamount | double | None |  |
| additionalforecastedamount | double | None |  |
| projectedtotalcommitmentsamount | double | None |  |
| anticipatedtocompleteamount | double | None |  |
| varianceofbudgetamount | double | None |  |
| totalinvoicesamount | double | None |  |
| remainingbalanceamount | double | None |  |
| internaltypetext | string | None |  |
| capitalexpense | string | None |  |
| milestonename | string | None |  |
| costtypetext | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcecreatedby | string | None |  |
| sourcemilestoneidentifier | string | None |  |
| statustrackertext | string | None |  |
| phasetext | string | None |  |
| statetext | string | None |  |
| duedatetime | timestamp | None |  |
| actualstartdatetime | timestamp | None |  |
| actualenddatetime | timestamp | None |  |
| baselinestartdatetime | timestamp | None |  |
| baselineduedatetime | timestamp | None |  |
| projectidentifier | string | None |  |
| workitemidentifier | string | None |  |
| sourcesystem | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| costperarea | double | None |  |
| totalpendinginvoiceamount | double | None |  |
| totalapprovedinvoiceamount | double | None |  |
| durationnumber | int | None |  |
| completedpercent | double | None |  |
| description | string | None |  |
| entityowneruseridentifier | string | None |  |
| vendoridentifier | string | None |  |
| templateidentifier | string | None |  |
| actualduration | double | None |  |
| baselineduration | double | None |  |
| milestonenumber | double | None |  |
| startdate | timestamp | None |  |
| meetingminutesworkitemidentifier | string | None |  |
| udp_hash | string | None |  |
| businesslinehierarchydescription | string | None |  |
| sourcemilestonecompanyidentifier | string | None |  |
| ffrrexpstartdate | timestamp | None |  |
| jllestimatedtimetocompletioncount | double | None |  |
| recognizedtodatecount | double | None |  |
| sourceserviceproductidentifier | string | None |  |
| sourceopportunityproductidentifier | string | None |  |
| wihinvoiceprobability | string | None |  |
| approvedforbillingflag | string | None |  |
| billablehoursrollupcount | double | None |  |
| billingeventinvoicedamount | string | None |  |
| sourcebillingeventitemidentifier | string | None |  |
| billingeventreleasedamount | string | None |  |
| billingeventstatusdescription | string | None |  |
| billingholdflag | string | None |  |
| sourceproductidentifier | string | None |  |
| eligibleforbillingamount | string | None |  |
| estimatedhoursformulacount | double | None |  |
| estimatedhoursvariancecount | double | None |  |
| invoicedescription | string | None |  |
| invoicepaymentstatusdescription | string | None |  |
| sourceinvoicetransactionidentifier | string | None |  |
| milestonelateflag | string | None |  |
| parentmilestoneflag | string | None |  |
| jllmilestonestartdate | timestamp | None |  |
| milestoneamount | double | None |  |
| milestonecompleteflag | string | None |  |
| approvedflag | string | None |  |
| approveruseridentifier | string | None |  |
| billableinfinancialsamount | double | None |  |
| billablesubmittedamount | double | None |  |
| billablefinancialsdayscount | double | None |  |
| billablesubmitteddayscount | double | None |  |
| billableexpensesinfinancialsamount | double | None |  |
| billableexpensessubmittedamount | double | None |  |
| billablehoursinfinancialscount | double | None |  |
| billablehourssubmittedcount | double | None |  |
| billedflag | string | None |  |
| billingeventtext | string | None |  |
| businesslineidentifier | string | None |  |
| milestonecategorydescription | string | None |  |
| closedforexpenseentryflag | string | None |  |
| closedfortimeentryflag | string | None |  |
| currencycode | string | None |  |
| currencyexchangerate | double | None |  |
| estimatedhourscount | double | None |  |
| estimatedtimetocompletioncount | double | None |  |
| estimatedtimetocompletionupdatedate | timestamp | None |  |
| excludefrombillingflag | string | None |  |
| includeinfinancialsflag | string | None |  |
| includeinrevenuereceivedflag | string | None |  |
| invoicedate | timestamp | None |  |
| invoicenumber | string | None |  |
| invoicedflag | string | None |  |
| milestonecost | double | None |  |
| practicename | string | None |  |
| servicelinedescription | string | None |  |
| statuscode | string | None |  |
| recordtypename | string | None |  |
| totalhourssubmittedcount | double | None |  |
| parentmilestoneidentifier | string | None |  |
| revenuereceivedenddate | timestamp | None |  |
| revenuereceivedstartdate | timestamp | None |  |
| servicesproductname | string | None |  |
| projecttargetenddate | string | None |  |
| totalbillamount | double | None |  |
| totalplannedamount | double | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| market | string | None |  |
| schedulestatus | string | None |  |
| deliverable | string | None |  |
| markedupvendorcosts | double | None |  |
| monthlyforecastamount | double | None |  |
| milestonephase | string | None |  |
| approvedforvendorpayment | boolean | None |  |
| targetdate | timestamp | None |  |
| vendoraccount | string | None |  |
| revenuereceivedprofitrate | double | None |  |
| revenuereceivedvendorrevenue | double | None |  |
| forecastduration | double | None |  |
| forecaststartdatetime | timestamp | None |  |
| forecastenddatetime | timestamp | None |  |
| domainname | string | None |  |

#### vw_ingenious_program

**Row Count:** 53

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceprogramidentifier | string | None |  |
| sourceprogramtype | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| defaultintegrationpathtext | string | None |  |
| entityowneruseridentifier | string | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| additionalprogrammanageridentifier | string | None |  |
| programmanageridentifier | string | None |  |
| workitemidentifier | string | None |  |
| ratecardtext | string | None |  |
| templatetext | string | None |  |
| customeridentifier | string | None |  |
| meetingminutesworkitemidentifier | string | None |  |
| vendoridentifier | string | None |  |
| state | string | None |  |
| phase | string | None |  |
| duedate | timestamp | None |  |
| actualstartdate | timestamp | None |  |
| actualenddate | timestamp | None |  |
| trackstatus | string | None |  |
| baselinestartdate | timestamp | None |  |
| baselineduedate | timestamp | None |  |
| description | string | None |  |
| sourceprogramregion | string | None |  |
| overallsummary | string | None |  |
| schedulesummary | string | None |  |
| budgetsummary | string | None |  |
| budgetstatus | string | None |  |
| sourceprogramname | string | None |  |
| percentcompleted | double | None |  |
| startdate | timestamp | None |  |
| originalbudget | double | None |  |
| approvedchangesandtransfers | double | None |  |
| pendingchangesandtransfers | double | None |  |
| totalapprovedbudget | double | None |  |
| totalprojectedbudget | double | None |  |
| approvedcommitments | double | None |  |
| pendingcommitments | double | None |  |
| projectedtotalcommitments | double | None |  |
| additionalforecastedcosts | double | None |  |
| anticipatedcosttocomplete | double | None |  |
| varianceofbudgettocost | double | None |  |
| totalinvoices | double | None |  |
| remainingbalancetoinvoice | double | None |  |
| costperarea | double | None |  |
| costcurrencytype | string | None |  |
| sourcesystem | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| schedulestatus | string | None |  |
| deliverable | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| departmentsponsor | string | None |  |
| category | string | None |  |
| locationidentifier | string | None |  |
| itemidentifier | string | None |  |
| utilitymeasureidentifier | string | None |  |
| utilitytypelinknumber | string | None |  |
| itemtypelinknumber | string | None |  |
| itemlinknumber | string | None |  |
| programcommentstext | string | None |  |
| managedbyusername | string | None |  |
| actionplanname | string | None |  |
| actionplandescription | string | None |  |
| actionplanclasstext | string | None |  |
| actionplansourcetext | string | None |  |
| actionplanstatustext | string | None |  |
| actionplannotestext | string | None |  |
| actionname | string | None |  |
| actiondescription | string | None |  |
| associatename | string | None |  |
| groupname | string | None |  |
| linkeditemtypetext | string | None |  |
| categoryclasstext | string | None |  |
| actionstatus | string | None |  |
| implementationcostamount | double | None |  |
| estimatedcostsavingsamount | double | None |  |
| estimatedunitsavingsamount | double | None |  |
| estimatedunitsavingspercent | string | None |  |
| estimatedenergysavingsamount | double | None |  |
| estimatedcarbondioxidesavingsamount | double | None |  |
| simplepaybackyear | string | None |  |
| depreciateyearcount | double | None |  |
| estimatedothercostsavingsamount | double | None |  |
| rebatesamount | double | None |  |
| internalratereturnvalue | string | None |  |
| othercostsamount | double | None |  |
| actualcostsamount | double | None |  |
| savingseffectivedate | timestamp | None |  |
| fundingsourcetext | string | None |  |
| estimatedaccuracypercent | string | None |  |
| actionprioritytext | string | None |  |
| raisedondate | timestamp | None |  |
| plannedstartdate | timestamp | None |  |
| plannedfinishdate | timestamp | None |  |
| assignedtoname | string | None |  |
| approvedstatus | string | None |  |
| tagname | string | None |  |
| kpiname | string | None |  |
| annualavoidedcostamount | double | None |  |
| notestext | string | None |  |
| sourceclientname | string | None |  |

#### vw_ingenious_project

**Row Count:** 4,498

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceprojectidentifier | string | None |  |
| sourceprojectid | string | None |  |
| projectname | string | None |  |
| weburltext | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcecreatedby | string | None |  |
| sourcemodifiedby | string | None |  |
| description | string | None |  |
| teamleaduseridentifer | string | None |  |
| projectmanageruseridentifer | string | None |  |
| phasetext | string | None |  |
| servicetypeidentifer | string | None |  |
| regionname | string | None |  |
| customerprojectnumber | string | None |  |
| globalcurrencytext | string | None |  |
| currencytype | string | None |  |
| currencyexchangeratetext | string | None |  |
| rentablearea | double | None |  |
| unitofmeasure | string | None |  |
| usablearea | double | None |  |
| grossarea | double | None |  |
| projectjllroletext | string | None |  |
| programidentifier | string | None |  |
| templatetext | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| spendingintegrationtext | string | None |  |
| architectprojectnumber | string | None |  |
| state | string | None |  |
| overallsummary | string | None |  |
| statustrackertext | string | None |  |
| totalestimatedamount | double | None |  |
| risktext | string | None |  |
| projectstatusmanuallysetflag | string | None |  |
| customerregionidentifier | string | None |  |
| customerbusinessunitidentifier | string | None |  |
| customerprojectcategoryidentifier | string | None |  |
| customerworktypeidentifier | string | None |  |
| customerprojecttypeidentifier | string | None |  |
| customerprojectsubtypeidentifier | string | None |  |
| customerprojectstatusidentifier | string | None |  |
| startdatetime | timestamp | None |  |
| stagetext | string | None |  |
| jllprojecttypetext | string | None |  |
| totalapprovedbudgetamount | double | None |  |
| pendingcommitmentsamount | double | None |  |
| projectedtotalcommitmentsamount | double | None |  |
| totalapprovedinvoicesamount | double | None |  |
| varianceofbudgettocostamount | double | None |  |
| migratedprojectid | string | None |  |
| customertyptext | string | None |  |
| driverscorenumber | double | None |  |
| sourcestrategicalignmentidentifier | string | None |  |
| strategicalignmentscorenumber | double | None |  |
| sourcepaybackidentifier | string | None |  |
| paybackscorenumber | double | None |  |
| sourceconditionscoreidentifier | string | None |  |
| conditionscorenumber | double | None |  |
| sourceorganizationalimpactidentifier | string | None |  |
| organizationalimpactscorenumber | double | None |  |
| sourceprobabilityimpactidentifier | string | None |  |
| probabilityimpactscorenumber | double | None |  |
| sourcetimingimpactidentifier | string | None |  |
| timingimpactscorenumber | double | None |  |
| sourcemagnitudeimpactidentifier | string | None |  |
| magnitudeimpactscorenumber | double | None |  |
| sourcelocationcharacteristicidentifier | string | None |  |
| locationcharacteristicscorenumber | double | None |  |
| sourceclassificationidentifier | string | None |  |
| classificationscorenumber | double | None |  |
| sourceelementidentifier | string | None |  |
| elementscorenumber | double | None |  |
| sourceexperienceidentifier | string | None |  |
| experiencescorenumber | double | None |  |
| subtyptext | string | None |  |
| leasedofownedtext | string | None |  |
| projectleaseenddatetime | timestamp | None |  |
| keyleasetermstext | string | None |  |
| plannedyearidentifier | string | None |  |
| scopetext | string | None |  |
| justificationtext | string | None |  |
| budgetdevelopedbyname | string | None |  |
| planningstatustext | string | None |  |
| levelofreviewtext | string | None |  |
| estimatelevelidentifier | string | None |  |
| monthsbeforefinancialstartnumber | int | None |  |
| monthsafterfinancialendnumber | int | None |  |
| constructionstartdatetime | timestamp | None |  |
| constructionenddatetime | timestamp | None |  |
| locationname | string | None |  |
| thirdpartycertificationtext | string | None |  |
| sustainabilitycertificationtext | string | None |  |
| leadershipinenergyandenvironmentaldesignprojecttext | string | None |  |
| leadershipinenergyandenvironmentaldesignbuildingtext | string | None |  |
| leadershipinenergyandenvironmentaldesigncertifiedprojecttext | string | None |  |
| buildingenergycode | string | None |  |
| coordinatornameuseridentifer | string | None |  |
| templateworktypetext | string | None |  |
| projectinitiationdatetime | timestamp | None |  |
| duedatetime | timestamp | None |  |
| actualstartdatetime | timestamp | None |  |
| actualenddatetime | timestamp | None |  |
| baselinestartdatetime | timestamp | None |  |
| baselineduedatetime | timestamp | None |  |
| workitemidentifier | string | None |  |
| projecttypeidentifier | string | None |  |
| sourceprojecttypeidentifier | string | None |  |
| projecttypename | string | None |  |
| sourceprojectservicetypeidentifier | string | None |  |
| projectservicetypename | string | None |  |
| duration | double | None |  |
| actualduration | double | None |  |
| baselineduration | double | None |  |
| approvedcommitments | double | None |  |
| totalprojectedbudget | double | None |  |
| totalpendinginvoices | double | None |  |
| totalinvoices | double | None |  |
| remainingbalancetoinvoice | double | None |  |
| city | string | None |  |
| country | string | None |  |
| fitouttype | string | None |  |
| approvedchangesandtransfers | double | None |  |
| pendingchangesandtransfers | double | None |  |
| additionalforecastedcosts | double | None |  |
| anticipatedcosttocomplete | double | None |  |
| costperarea | double | None |  |
| budgetsummary | string | None |  |
| schedulesummary | string | None |  |
| customerprojectmanagername | string | None |  |
| clarizenprojecturl | string | None |  |
| companyidentifier | string | None |  |
| propertyidentifier | string | None |  |
| sourcejobtemplateidentifier | string | None |  |
| vendoridentifier | string | None |  |
| parentworkitemidentifier | string | None |  |
| sourcetemplateidentifier | string | None |  |
| practiceidentifier | string | None |  |
| contractidentifier | string | None |  |
| psidentifier | string | None |  |
| workinprogressbillablemilestoneamount | double | None |  |
| expensetypedescription | string | None |  |
| projectidentifierchaintext | string | None |  |
| projectnamechaintext | string | None |  |
| projectedenddate | timestamp | None |  |
| currenttimeperiodenddate | timestamp | None |  |
| totaltaskscount | double | None |  |
| propertytypedescription | string | None |  |
| totalassignedhourscount | double | None |  |
| totalbackloghourscount | double | None |  |
| totalbilledtransactionscount | double | None |  |
| totalbookingscount | double | None |  |
| totalhoursapprovedcount | double | None |  |
| totalassignedrevenueamount | double | None |  |
| totalsubmittedhourscount | double | None |  |
| totalworkinprogresscount | double | None |  |
| sourcesystem | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| sourceinternalvalue | string | None |  |
| percentcompleted | double | None |  |
| originalbudgetamount | double | None |  |
| udp_hash | string | None |  |
| projectpriorityscorenumber | double | None |  |
| clientactiveflag | boolean | None |  |
| totalprojectwastetonscount | double | None |  |
| savedwaterlitercount | double | None |  |
| wastetonsdivertedfromlandfillcount | double | None |  |
| schedulestatus | string | None |  |
| deliverable | string | None |  |
| projectcommenttext | string | None |  |
| billableindicator | string | None |  |
| projectbudgetstatus | string | None |  |
| agreementtypecode | string | None |  |
| apacassettypecode | string | None |  |
| apacprojectstagecode | string | None |  |
| jllbusinessline | string | None |  |
| carbonoffsetpurchasedindicator | string | None |  |
| carbonstudyconsultantstext | string | None |  |
| carbonstudyimplementedcode | string | None |  |
| certificationachievedcode | string | None |  |
| certificationservicedeliveredbyname | string | None |  |
| certifyingcompanyifothername | string | None |  |
| projectdocumenturltext | string | None |  |
| energycode | string | None |  |
| energymodeldevelopedindicator | string | None |  |
| projectfinancesubmissioncommenttext | string | None |  |
| wastetonsdivertedfromlandfillindicator | string | None |  |
| majormarketname | string | None |  |
| migratedcapitalplanningprojectidentifier | string | None |  |
| minormarketname | string | None |  |
| ovalid | string | None |  |
| peoplesoftprojectidentifier | string | None |  |
| peoplesoftcountry | string | None |  |
| peoplesofthubtext | string | None |  |
| peoplesoftofficelocationdescription | string | None |  |
| peoplesoftpltext | string | None |  |
| risklevelcode | string | None |  |
| externalruntimeidentifier | string | None |  |
| targetenergyusageperannumcount | string | None |  |
| sustainabilitycertificationcode | string | None |  |
| targetenergyusageperannumunittypecode | string | None |  |
| watergallonssavedduringconstructioncount | string | None |  |
| closingnotestext | string | None |  |
| riskmitigationdescription | string | None |  |
| projectdimsetidentifier | string | None |  |
| projectsetidentifier | string | None |  |
| effectivedatesetidentifier | string | None |  |
| projectlevel2identifier | string | None |  |
| projectlevel2description | string | None |  |
| projectlevel3identifier | string | None |  |
| projectlevel3description | string | None |  |
| projectlevel4identifier | string | None |  |
| projectlevel4description | string | None |  |
| projectlevel5identifier | string | None |  |
| projectlevel5description | string | None |  |
| treename | string | None |  |
| projectdescription | string | None |  |
| projecttype | string | None |  |
| financialsubmissiondatetime | timestamp | None |  |
| billingapprover | string | None |  |
| jllbillinganalyst | string | None |  |
| estimatedtimetocompletion | double | None |  |
| effectiverate | double | None |  |
| evcomplete | double | None |  |
| projectfunction | int | None |  |
| invoicedetails | string | None |  |
| projectmarket | string | None |  |
| ofplannedbillrateweighted | double | None |  |
| owneridentifier | string | None |  |
| parentregion | string | None |  |
| plannedbillrate | double | None |  |
| projectfinancialsindicator | string | None |  |
| projectsize | string | None |  |
| psbillingtype | string | None |  |
| psmarket | string | None |  |
| psebillingtype | string | None |  |
| estimatedmargin | double | None |  |
| externalcosts | double | None |  |
| externaltimecost | double | None |  |
| internalbudget | double | None |  |
| internalcosts | double | None |  |
| internaltimecost | double | None |  |
| psemargin | double | None |  |
| milestonecost | double | None |  |
| oppurtunityowner | string | None |  |
| othercosts | double | None |  |
| percentestimatedmargin | double | None |  |
| percenthourscomplete | double | None |  |
| plannedhours | double | None |  |
| projectstatusnotes | string | None |  |
| pseregion | string | None |  |
| psestage | string | None |  |
| unitofmeasurement | string | None |  |
| vfpmargin | double | None |  |
| wdjll1oppurtunityid | string | None |  |
| worklocationaddress | string | None |  |
| worklocationcity | string | None |  |
| worklocationcitystateprov | string | None |  |
| worklocationcountry | string | None |  |
| worklocationstateprov | string | None |  |
| worklocationzippostalcode | string | None |  |
| projectcountry | string | None |  |
| projectlevel1identifier | string | None |  |
| projectlevel1description | string | None |  |
| projectlevel6identifier | string | None |  |
| projectlevel6description | string | None |  |
| jllmarket | string | None |  |
| projectcustomer | string | None |  |
| corrigocustomernumber | string | None |  |
| corrigoidnumber | string | None |  |
| corrigointegrationstatustext | string | None |  |
| corrigoprojectstartdatetime | timestamp | None |  |
| extractname | string | None |  |
| customattributes | string | None |  |
| customid | string | None |  |
| exclusions | string | None |  |
| health | string | None |  |
| scheduledhealth | string | None |  |
| sector | string | None |  |
| statusid | string | None |  |
| tags | string | None |  |
| projectdriveridentifier | string | None |  |
| sourcedriveridentifier | string | None |  |
| businessunitidentifier | string | None |  |
| contactidentifier | string | None |  |
| locationidentifier | string | None |  |
| totalpaidvalue | double | None |  |
| istestproject | string | None |  |
| officefitoutstyle | string | None |  |
| officefitoutqualityandcomplexity | string | None |  |
| e1integrationprojectid | string | None |  |
| domainname | string | None |  |
| peoplesoftdepartmentid | bigint | None |  |
| locationleasedorowned | string | None |  |
| customdate | timestamp | None |  |
| projectcommencementdatetime | timestamp | None |  |
| projectcompletiondatetime | timestamp | None |  |

#### vw_ingenious_projectadditionalcustomfield

**Row Count:** 4,788

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourcesystem | string | None |  |
| sourceprojectadditionalfieldidentifier | string | None |  |
| clientcustomvaluetext | string | None |  |
| clientcustomValuetypecode | string | None |  |
| projectidentifier | string | None |  |
| udp_hash | string | None |  |

#### vw_ingenious_projectsites

**Row Count:** 1,879

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| propertyidentifier | string | None |  |
| projectidentifier | string | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| isdeleted | string | None |  |
| udp_hash | string | None |  |
| domainname | string | None |  |

#### vw_ingenious_projectstatsindicator

**Row Count:** 2,018

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceprojectstatusidentifier | string | None |  |
| statusindicatortypetext | string | None |  |
| statusnotestext | string | None |  |
| status | string | None |  |
| name | string | None |  |
| statusupdatedate | timestamp | None |  |
| entityowneruseridentifier | string | None |  |
| projectidentifier | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| projectstatusindicatortypeidentifier | string | None |  |
| sourcesystem | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| title | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| domainname | string | None |  |

#### vw_ingenious_punchitemmember

**Row Count:** 922

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| punchlistitemidentifier | string | None |  |
| memberidentifier | string | None |  |
| sourcesystem | string | None |  |
| domainname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| isdeleted | string | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |

#### vw_ingenious_punchlistitem

**Row Count:** 583

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceprojectdefectidentifier | string | None |  |
| defectitemprojectidentifier | string | None |  |
| name | string | None |  |
| defectdescription | string | None |  |
| locationname | string | None |  |
| responsiblepartyuseridentifier | string | None |  |
| startdatetime | timestamp | None |  |
| planneddatetime | timestamp | None |  |
| completeddatetime | timestamp | None |  |
| defectitemnotestext | string | None |  |
| sourcecreatedby | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifiedby | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourcesystem | string | None |  |
| category | string | None |  |
| comment | string | None |  |
| isdeleted | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| priority | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| domainname | string | None |  |
| responsiblepartycompanyidentifier | string | None |  |
| punchlistid | string | None |  |
| status | string | None |  |
| stampid | string | None |  |
| ballincourtidentifier | string | None |  |
| listcreatedat | timestamp | None |  |
| listenddate | date | None |  |
| listname | string | None |  |
| liststartdate | date | None |  |
| listupdatedat | timestamp | None |  |
| liststatus | string | None |  |
| stampcolor | string | None |  |
| stampinitials | string | None |  |
| stamptitle | string | None |  |

#### vw_ingenious_risk

**Row Count:** 519

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceriskidentifier | string | None |  |
| initialriskprobabilitytype | string | None |  |
| initialprobablerisklikelihoodscorenumber | int | None |  |
| initialconsequencescore | string | None |  |
| initialconsequencescorenumber | int | None |  |
| initialriskfactorscorenumber | int | None |  |
| jllorclientriskbearer | string | None |  |
| mitigationtypecode | string | None |  |
| mitigationactiondescription | string | None |  |
| assigneeuseridentifier | string | None |  |
| actionduedate | timestamp | None |  |
| estimatedriskprobabilitytype | string | None |  |
| estimatedrisklikelihoodscorenumber | int | None |  |
| estimatedconsequencescore | string | None |  |
| estimatedconsequencescorenumber | int | None |  |
| estimatedriskfactorscorenumber | int | None |  |
| statuscode | string | None |  |
| riskdescription | string | None |  |
| riskcategory | string | None |  |
| occurrenceimpactdescription | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| workitemidentifier | string | None |  |
| risktitle | string | None |  |
| typeofriskcode | string | None |  |
| closeddate | timestamp | None |  |
| closedbyuseridentifier | string | None |  |
| sourcecreatedby | string | None |  |
| entityowneruseridentifier | string | None |  |
| evaluatedbyuseridentifier | string | None |  |
| sourcemodifiedby | string | None |  |
| openedbyuseridentifier | string | None |  |
| resolvedbyuseridentifier | string | None |  |
| submittedbyuseridentifier | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| jllinternalrisk | boolean | None |  |
| comment | string | None |  |
| evaluationdate | timestamp | None |  |
| responsiblecontactidentifier | string | None |  |
| submissiondate | timestamp | None |  |
| assignmentdate | timestamp | None |  |
| isdeleted | string | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| udp_hash | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| openingdate | timestamp | None |  |
| actualdate | timestamp | None |  |
| anticipateddate | timestamp | None |  |
| baselinedate | timestamp | None |  |
| domainname | string | None |  |
| expectedcost | double | None |  |
| expecteddelayvalue | double | None |  |
| scheduledvariance | double | None |  |
| expecteddelayunit | string | None |  |
| isrisk | string | None |  |
| mitigationstrategy | string | None |  |
| name | string | None |  |
| priority | string | None |  |
| projectidentifier | string | None |  |
| risklevel | string | None |  |
| riskto | string | None |  |

#### vw_ingenious_riskcontact

**Row Count:** 2,109

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| riskidentifier | string | None |  |
| contactidentifier | string | None |  |
| sourcesystem | string | None |  |
| domainname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| isdeleted | string | None |  |
| udp_hash | string | None |  |

#### vw_ingenious_riskmembers

**Row Count:** 4,056

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| riskidentifier | string | None |  |
| memberidentifier | string | None |  |
| sourcesystem | string | None |  |
| domainname | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_delete_flag | string | None |  |
| isdeleted | string | None |  |
| udp_hash | string | None |  |

#### vw_ingenious_users

**Row Count:** 4,037

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| **id** (PK) | string | None |  |
| sourceuseridentifier | string | None |  |
| companyname | string | None |  |
| userid | string | None |  |
| databaseid | string | None |  |
| isremoved | string | None |  |
| firstname | string | None |  |
| lastname | string | None |  |
| displayname | string | None |  |
| userlogin | string | None |  |
| role | string | None |  |
| jobtitle | string | None |  |
| federalidnbr | string | None |  |
| usernumber | string | None |  |
| organization | string | None |  |
| language | string | None |  |
| datetimelastaction | timestamp | None |  |
| lastwoacceptancedate | timestamp | None |  |
| lastwocompletiondate | timestamp | None |  |
| activesuspendedstatus | string | None |  |
| reportstoid | string | None |  |
| address1 | string | None |  |
| address2 | string | None |  |
| city | string | None |  |
| stateprov | string | None |  |
| zippostalcode | string | None |  |
| country | string | None |  |
| officephone | string | None |  |
| mobilephone | string | None |  |
| emergencyphone | string | None |  |
| emailnbr1 | string | None |  |
| emailnbr2 | string | None |  |
| emailnbr3 | string | None |  |
| nocinstanceidentifier | string | None |  |
| sourcecreateddatetime | timestamp | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourcepersonidentifier | string | None |  |
| workemail | string | None |  |
| personlastupdatedatetime | timestamp | None |  |
| personfullname | string | None |  |
| worklocation | string | None |  |
| workertypecode | string | None |  |
| lastlogindate | timestamp | None |  |
| personcreatedby | string | None |  |
| directmanageridentifier | string | None |  |
| jobtitlename | string | None |  |
| personlastupdatedby | string | None |  |
| primarycustomeridentifier | string | None |  |
| referencedcustomeridentifier | string | None |  |
| teamcontactidentifier | string | None |  |
| persongivenname | string | None |  |
| personfamilyname | string | None |  |
| isdeleted | string | None |  |
| worktimezone | string | None |  |
| udp_delete_flag | string | None |  |
| division | string | None |  |
| manageridentifier | string | None |  |
| contactidentifier | string | None |  |
| isactive | string | None |  |
| address | string | None |  |
| casesafeidentifier | string | None |  |
| fax | string | None |  |
| jllid | string | None |  |
| licensetype | string | None |  |
| communitynickname | string | None |  |
| phone | string | None |  |
| practicename | string | None |  |
| recordupdated | string | None |  |
| sourceuserroleidentifier | string | None |  |
| sellerregion | string | None |  |
| sellersegment | string | None |  |
| timezonesidkey | string | None |  |
| aboutme | string | None |  |
| acquisitionidentifier | string | None |  |
| adminusernotes | string | None |  |
| alias | string | None |  |
| bannerphotourl | string | None |  |
| businessline | string | None |  |
| c2gapilicensekey | string | None |  |
| c2gsupportdataaccesskey | string | None |  |
| sourcecallcenteridentifier | string | None |  |
| congalicense | string | None |  |
| contractor | string | None |  |
| corrigouseridentifier | string | None |  |
| currencycode | string | None |  |
| customemailsent | string | None |  |
| defaultcurrencycode | string | None |  |
| defaultgroupnotificationfrequency | string | None |  |
| delegatedapprovedidentifier | string | None |  |
| department | string | None |  |
| digestfrequency | string | None |  |
| emailencodingkey | string | None |  |
| empautonum | string | None |  |
| extension | string | None |  |
| federationidentifier | string | None |  |
| financialforcelicense | string | None |  |
| forecastenabled | string | None |  |
| gridbuddylicense | string | None |  |
| hredittitlepermissions | string | None |  |
| workcalendar | string | None |  |
| isportalenabled | string | None |  |
| isprofilephotoactive | string | None |  |
| isresource | string | None |  |
| languagelocalekey | string | None |  |
| localesidkey | string | None |  |
| mediumbannerphotourl | string | None |  |
| mediumphotourl | string | None |  |
| mytrailheadlicense | string | None |  |
| name | string | None |  |
| oscuser | string | None |  |
| portalrole | string | None |  |
| sourceprofileidentifier | string | None |  |
| psenterpriselicense | string | None |  |
| ptosummaryidentifier | string | None |  |
| receivesadmininfoemails | string | None |  |
| receivesinfoemails | string | None |  |
| salesforcelicense | string | None |  |
| salesforceplatformlicense | string | None |  |
| sellingfunction | string | None |  |
| senderemail | string | None |  |
| sendername | string | None |  |
| signature | string | None |  |
| smallbannerphotourl | string | None |  |
| stayintouchnote | string | None |  |
| stayintouchsignature | string | None |  |
| stayintouchsubject | string | None |  |
| team | string | None |  |
| title | string | None |  |
| tracrtcuserendofday | string | None |  |
| tracrtcuserstartofday | string | None |  |
| updatedcontactinfodate | timestamp | None |  |
| useaudit | string | None |  |
| userlicense | string | None |  |
| usertype | string | None |  |
| username | string | None |  |
| workdaycostcenter | string | None |  |
| workdayprofile | string | None |  |
| budgetedbooking | double | None |  |
| sourcesystem | string | None |  |
| udp_create_ts | timestamp | None |  |
| udp_update_ts | timestamp | None |  |
| udp_hash | string | None |  |
| adminuserindicator | string | None |  |
| useravailailitypercent | string | None |  |
| businessunitidentifier | string | None |  |
| peoplesoftuseridentifier | string | None |  |
| functionidentifier | string | None |  |
| marketidentifier | string | None |  |
| usermarketdescription | string | None |  |
| useremployeetype | string | None |  |
| externaluserindicator | string | None |  |
| financialuserindicator | string | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| userregion | string | None |  |
| superuserindicator | string | None |  |
| companyidentifier | string | None |  |
| primarychatapp | string | None |  |
| contactpreference | string | None |  |
| namepreference | string | None |  |
| ovcid | int | None |  |
| billatzero | boolean | None |  |
| roleid | string | None |  |
| peoplesoftusercode | string | None |  |
| score | int | None |  |
| extractname | string | None |  |
| caseidentifier | string | None |  |
| accessdocumenttrackerlteindicator | string | None |  |
| updatedcontactinfodatetype | string | None |  |
| accounttype | string | None |  |
| locationidentifier | string | None |  |
| terminationdate | timestamp | None |  |
| domainname | string | None |  |

#### vw_ingenious_workitem

**Row Count:** 5,545

**Columns:**

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| systemworkitemidentifier | string | None |  |
| **id** (PK) | string | None |  |
| workitemtype | string | None |  |
| sourcecreatedby | string | None |  |
| completedpercent | double | None |  |
| Workitemdescription | string | None |  |
| sourcemodifieddatetime | timestamp | None |  |
| sourceupdatedby | string | None |  |
| parentworkitemidentifier | string | None |  |
| entityowneruseridentifier | string | None |  |
| schedulestatus | string | None |  |
| deliverable | string | None |  |
| vendororiginalcost | double | None |  |
| vendorchangeordercost | double | None |  |
| sourcelastupdateddatetime | timestamp | None |  |
| sourcesystem | string | None |  |
| udp_hash | string | None |  |
| domainname | string | None |  |

---

## Relationships

| From View | From Column | To View | To Column | Type | Confidence |
|-----------|-------------|---------|-----------|------|------------|
| vw_ingenious_answer | project | vw_ingenious_project | id | foreign_key | medium |

---

## Summary Statistics

- **Total Views:** 25
- **Total Columns:** 1382
- **Total Rows:** 237,989
- **Views with Primary Keys:** 25
- **Identified Relationships:** 1
- **Average Columns per View:** 55.3
