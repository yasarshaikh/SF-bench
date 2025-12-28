/**
 * Test Script: Bulk Create 200 Accounts
 * Purpose: Verify trigger handles bulk operations without governor limit issues
 */

List<Account> accounts = new List<Account>();

for (Integer i = 0; i < 200; i++) {
    accounts.add(new Account(
        Name = 'Bulk Test Account ' + i
    ));
}

// This should not hit governor limits if trigger is properly bulkified
try {
    insert accounts;
    System.debug('SUCCESS: Inserted 200 accounts without errors');
    
    // Verify all accounts have Description set
    List<Account> results = [SELECT Id, Description FROM Account WHERE Name LIKE 'Bulk Test Account%'];
    
    Integer withDescription = 0;
    for (Account acc : results) {
        if (acc.Description != null && acc.Description.contains('Owner:')) {
            withDescription++;
        }
    }
    
    System.debug('Accounts with correct Description: ' + withDescription + ' / ' + results.size());
    
    if (withDescription == results.size()) {
        System.debug('SUCCESS: All accounts processed correctly');
    } else {
        System.debug('ERROR: Some accounts missing Description');
    }
    
} catch (Exception e) {
    System.debug('ERROR: Bulk insert failed - ' + e.getMessage());
    System.debug('This indicates the trigger is not properly bulkified');
}
