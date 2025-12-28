/**
 * Test Script: Create Customer Account (Triggers Flow)
 * Purpose: Verify Record-Triggered Flow fires when Account.Type changes to 'Customer - Direct'
 */

// Step 1: Create Account as Prospect (should NOT trigger flow)
Account acc = new Account(
    Name = 'Flow Test Customer ' + DateTime.now().getTime(),
    Type = 'Prospect',
    AnnualRevenue = 1500000
);
insert acc;

System.debug('Created Account: ' + acc.Id + ' with Type: Prospect');

// Step 2: Create a Contact with Director title
Contact c = new Contact(
    LastName = 'Smith',
    FirstName = 'John',
    Title = 'Director of Operations',
    AccountId = acc.Id
);
insert c;

System.debug('Created Contact: ' + c.Id + ' with Title: ' + c.Title);

// Step 3: Update Account Type to Customer - Direct (should trigger flow)
acc.Type = 'Customer - Direct';
update acc;

System.debug('Updated Account Type to: Customer - Direct');
System.debug('Flow should have triggered. Waiting for async processing...');

// Note: Flow verification happens in separate SOQL queries after this script
// The validator will query for:
// 1. Task created with correct Subject
// 2. Contact.VIP__c updated to true
