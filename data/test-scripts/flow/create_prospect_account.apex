/**
 * Test Script: Create Prospect Account (Should NOT Trigger Flow)
 * Purpose: Verify Flow entry conditions are correct - should NOT fire for non-Customer accounts
 */

// Create Account as Prospect and keep it as Prospect
Account acc = new Account(
    Name = 'Flow Test Prospect ' + DateTime.now().getTime(),
    Type = 'Prospect',
    AnnualRevenue = 500000
);
insert acc;

System.debug('Created Prospect Account: ' + acc.Id);

// Wait a moment for any async processing
// (In real test, we'd use Test.startTest()/stopTest())

// Check if any Tasks were created (should be 0)
List<Task> tasks = [SELECT Id, Subject FROM Task WHERE WhatId = :acc.Id];

if (tasks.size() == 0) {
    System.debug('SUCCESS: No Tasks created for Prospect account (correct behavior)');
} else {
    System.debug('ERROR: ' + tasks.size() + ' Task(s) created for Prospect account');
    System.debug('Flow entry conditions are not correct - it should only fire for Customer - Direct');
    for (Task t : tasks) {
        System.debug('  - Task: ' + t.Subject);
    }
}
