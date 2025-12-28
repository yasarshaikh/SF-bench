/**
 * Test Script: Bulk Create 200 Customer Accounts
 * Purpose: Verify Flow handles bulk operations without CPU timeout
 */

// Create 200 accounts as Prospects
List<Account> accounts = new List<Account>();

for (Integer i = 0; i < 200; i++) {
    accounts.add(new Account(
        Name = 'Bulk Customer ' + i + ' ' + DateTime.now().getTime(),
        Type = 'Prospect',
        AnnualRevenue = 2000000
    ));
}

insert accounts;
System.debug('Inserted 200 Prospect accounts');

// Create Contacts for each account
List<Contact> contacts = new List<Contact>();
for (Account acc : accounts) {
    contacts.add(new Contact(
        LastName = 'Director ' + acc.Name,
        Title = 'Sales Director',
        AccountId = acc.Id
    ));
}
insert contacts;
System.debug('Inserted 200 Contacts');

// Now update all accounts to Customer - Direct (should trigger flow 200 times)
try {
    for (Account acc : accounts) {
        acc.Type = 'Customer - Direct';
    }
    
    Long startTime = DateTime.now().getTime();
    update accounts;
    Long endTime = DateTime.now().getTime();
    
    System.debug('SUCCESS: Updated 200 accounts in ' + (endTime - startTime) + 'ms');
    
    // Verify Tasks were created
    List<Task> tasks = [SELECT Id FROM Task WHERE WhatId IN :accounts];
    System.debug('Tasks created: ' + tasks.size());
    
    if (tasks.size() == 200) {
        System.debug('SUCCESS: Flow created all 200 Tasks');
    } else if (tasks.size() > 0) {
        System.debug('PARTIAL: Flow created ' + tasks.size() + ' out of 200 Tasks');
    } else {
        System.debug('ERROR: No Tasks created - Flow may not have fired');
    }
    
} catch (Exception e) {
    System.debug('ERROR: Bulk update failed - ' + e.getMessage());
    if (e.getMessage().contains('CPU') || e.getMessage().contains('timeout')) {
        System.debug('Flow is not properly optimized for bulk operations');
    }
}
