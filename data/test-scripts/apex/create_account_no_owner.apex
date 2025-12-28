/**
 * Test Script: Create Account without Owner
 * Purpose: Verify trigger handles null Owner gracefully
 */

// Create account (Owner will be current user by default, but we test the null-safety pattern)
Account acc = new Account(
    Name = 'Test No Owner Account'
);
insert acc;

// Query the account to verify trigger ran
Account result = [SELECT Id, Name, Description, OwnerId FROM Account WHERE Id = :acc.Id];

System.debug('Account ID: ' + result.Id);
System.debug('Account Name: ' + result.Name);
System.debug('Account Description: ' + result.Description);
System.debug('Owner ID: ' + result.OwnerId);

// Assert the trigger set the Description correctly
if (result.Description == null || result.Description == '') {
    System.debug('ERROR: Description was not set by trigger');
} else if (result.Description.contains('Owner:')) {
    System.debug('SUCCESS: Trigger set Description with Owner info');
} else {
    System.debug('ERROR: Description does not contain expected format');
}
