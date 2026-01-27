---
name: salesforce-expert
description: Provides Salesforce platform expertise for Apex, LWC, Flow, and declarative development. The agent invokes this skill when working on Salesforce code, discussing platform constraints, or troubleshooting Salesforce-specific issues.
---

# Salesforce Expert

## Overview

This skill provides deep Salesforce platform expertise for development tasks. It covers Apex programming, Lightning Web Components, Flow automation, and declarative configurations.

## When This Skill Applies

- Working on Apex classes, triggers, or tests
- Developing Lightning Web Components
- Creating or modifying Flows
- Configuring page layouts or object definitions
- Discussing governor limits or platform constraints
- Troubleshooting Salesforce-specific errors

## Salesforce Development Patterns

### Apex Best Practices

#### Trigger Handler Pattern
```apex
// Trigger delegates to handler
trigger AccountTrigger on Account (before insert, before update, after insert, after update) {
    AccountTriggerHandler handler = new AccountTriggerHandler();
    handler.run();
}

// Handler implements logic with bulkification
public class AccountTriggerHandler {
    public void run() {
        if (Trigger.isBefore && Trigger.isInsert) {
            handleBeforeInsert(Trigger.new);
        }
    }

    private void handleBeforeInsert(List<Account> accounts) {
        // Process all records in bulk
        for (Account acc : accounts) {
            // Logic here
        }
    }
}
```

#### Bulkification Pattern
```apex
// BAD: SOQL in loop
for (Account acc : accounts) {
    Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id LIMIT 1]; // Governor limit violation
}

// GOOD: Bulkified query
Set<Id> accountIds = new Set<Id>();
for (Account acc : accounts) {
    accountIds.add(acc.Id);
}
Map<Id, Contact> contactsByAccount = new Map<Id, Contact>(
    [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]
);
```

#### Error Handling Pattern
```apex
public class AccountService {
    public static void processAccounts(List<Account> accounts) {
        List<Database.SaveResult> results = Database.update(accounts, false);

        for (Integer i = 0; i < results.size(); i++) {
            if (!results[i].isSuccess()) {
                for (Database.Error err : results[i].getErrors()) {
                    System.debug(LoggingLevel.ERROR,
                        'Error on record ' + accounts[i].Id + ': ' + err.getMessage());
                }
            }
        }
    }
}
```

### Governor Limits Reference

| Limit | Synchronous | Asynchronous |
|-------|-------------|--------------|
| SOQL Queries | 100 | 200 |
| SOQL Rows | 50,000 | 50,000 |
| DML Statements | 150 | 150 |
| DML Rows | 10,000 | 10,000 |
| CPU Time | 10,000 ms | 60,000 ms |
| Heap Size | 6 MB | 12 MB |
| Callouts | 100 | 100 |

### LWC Component Pattern
```javascript
// lwc/accountList/accountList.js
import { LightningElement, wire } from 'lwc';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';

export default class AccountList extends LightningElement {
    accounts;
    error;

    @wire(getAccounts)
    wiredAccounts({ error, data }) {
        if (data) {
            this.accounts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.accounts = undefined;
        }
    }
}
```

### Flow Best Practices

1. **Use Before-Save Flows** for field updates (faster than triggers)
2. **Bulkify Flow Logic** - avoid loops with DML inside
3. **Use Fault Paths** for error handling
4. **Limit Subflows** to reduce complexity

## Security Patterns

### CRUD/FLS Enforcement
```apex
// Check permissions before DML
if (Schema.sObjectType.Account.isUpdateable()) {
    update accounts;
} else {
    throw new SecurityException('Insufficient privileges');
}

// Check field-level security
if (Schema.sObjectType.Account.fields.Name.isAccessible()) {
    String name = acc.Name;
}
```

### SOQL Injection Prevention
```apex
// BAD: String concatenation
String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';

// GOOD: Bind variables
String query = 'SELECT Id FROM Account WHERE Name = :userInput';
List<Account> accounts = Database.query(query);
```

## Scratch Org Management

### Creation
```bash
sf org create scratch -f config/project-scratch-def.json -a my-scratch -d 7
```

### Deployment
```bash
sf project deploy start -o my-scratch
```

### Test Execution
```bash
sf apex run test -o my-scratch -r human -c -w 10
```

### Cleanup
```bash
sf org delete scratch -o my-scratch -p
```

## Common Issues and Solutions

### "CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY"
- Check trigger recursion (use static variable to prevent)
- Verify required fields are populated
- Check validation rules

### "System.LimitException: Too many SOQL queries"
- Move queries outside loops
- Use collections and maps for lookups
- Consider async processing for large datasets

### "FIELD_CUSTOM_VALIDATION_EXCEPTION"
- Check validation rule conditions
- Ensure all required fields meet criteria
- Consider bypassing validation for integration users
