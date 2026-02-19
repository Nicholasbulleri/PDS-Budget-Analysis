# Ingenious Curated Consumption Views ER Diagram (Mermaid)

This diagram shows the entity relationships between curated consumption views.

```mermaid
erDiagram
    answer {
        id PK
        sourceansweridentifier
        incidentidentifier
        auditquestionidentifier
        auditansweridentifier
        sourceincidentidentifier
        answervalue
    }
    budgetchange {
        id PK
        approvedamount
        approvedprojectamount
        workitemidentifier
        currencytypecode
        declinedamount
        declinedprojectamount
    }
    budgetdetail {
        id PK
        sourcebudgetdetailidentifier
        workitemidentifier
        budgetitemname
        unitcount
        unitofmeasurecode
        perunitcostamount
    }
    businessunit {
        id PK
        sourcebusinessunitidentifier
        companyidentifier
        addressidentifier
        addressjobarnumber
        businessunittypecode
        accountlevelnumber
    }
    commitment {
        id PK
        sourcecommitmentidentifier
        commitmentname
        adjustedcontractamount
        approvedamount
        approvedprojectamount
        approvedsaveamount
    }
    commitmentchanges {
        id PK
        commitmentchangename
        totalamount
        customid
        commitmentchangedescription
        costcodename
        costcodeamount
    }
    directorycontactprojectlnk {
        id PK
        spendroleidentifer
        sourcecreatedby
        sourcecreateddatetime
        externaltext
        sourcemodifiedby
        sourcemodifieddatetime
    }
    generictask {
        id PK
        sourcetaskidentifer
        totalinvoicesamount
        costcode
        taskname
        capitalexpense
        costcodetype
    }
    inspection {
        id PK
        sourceinspectionuiidentifier
        sourceinspectionidentifier
        sourcecreateddatetime
        inspectionname
        deadlinedatetime
        completeddatetime
    }
    inspectionmembers {
        id PK
        memberidentifier
        inspectionidentifier
        sourcememberidentifier
    }
    inspectiontemplates {
        id PK
        sourceinspectiontemplateidentifier
        description
        generatepunchitemsonflag
        inspectiontype
        templatename
        surveytemplateidentifier
    }
    locations {
        id PK
        sourcelocationid
        databaseid
        address1
        address2
        city
        state
    }
    milestone {
        id PK
        originalbudgetamount
        approvedchangesandtransfersamount
        totalapprovedbudgetamount
        pendingchangesandtransfersamount
        totalprojectedbudgetamount
        approvedcommitmentsamount
    }
    program {
        id PK
        sourceprogramidentifier
        sourceprogramtype
        sourcecreatedby
        sourcecreateddatetime
        defaultintegrationpathtext
        entityowneruseridentifier
    }
    project {
        id PK
        sourceprojectidentifier
        sourceprojectid
        projectname
        weburltext
        sourcecreateddatetime
        sourcecreatedby
    }
    projectadditionalcustomfield {
        id PK
        sourceprojectadditionalfieldidentifier
        clientcustomvaluetext
        clientcustomValuetypecode
        projectidentifier
    }
    projectsites {
        id PK
        propertyidentifier
        projectidentifier
        isdeleted
    }
    projectstatsindicator {
        id PK
        sourceprojectstatusidentifier
        statusindicatortypetext
        statusnotestext
        status
        name
        statusupdatedate
    }
    punchitemmember {
        id PK
        punchlistitemidentifier
        memberidentifier
        isdeleted
    }
    punchlistitem {
        id PK
        sourceprojectdefectidentifier
        defectitemprojectidentifier
        name
        defectdescription
        locationname
        responsiblepartyuseridentifier
    }
    risk {
        id PK
        sourceriskidentifier
        initialriskprobabilitytype
        initialprobablerisklikelihoodscorenumber
        initialconsequencescore
        initialconsequencescorenumber
        initialriskfactorscorenumber
    }
    riskcontact {
        id PK
        riskidentifier
        contactidentifier
    }
    riskmembers {
        id PK
        riskidentifier
        memberidentifier
    }
    users {
        id PK
        sourceuseridentifier
        companyname
        userid
        databaseid
        isremoved
        firstname
    }
    workitem {
        id PK
        systemworkitemidentifier
        workitemtype
        sourcecreatedby
        completedpercent
        Workitemdescription
        sourcemodifieddatetime
    }

    answer ||--o{ project : "project"
    budgetdetail ||--o{ project : "projectidentifier"
    commitmentchanges ||--o{ project : "projectid"
    directorycontactprojectlnk ||--o{ project : "projectidentifier"
    generictask ||--o{ project : "projectidentifier"
    inspection ||--o{ project : "projectidentifier"
    milestone ||--o{ project : "projectidentifier"
    projectadditionalcustomfield ||--o{ project : "projectidentifier"
    projectsites ||--o{ project : "projectidentifier"
    projectstatsindicator ||--o{ project : "projectidentifier"
    punchlistitem ||--o{ project : "defectitemprojectidentifier"
    risk ||--o{ project : "projectidentifier"

```
