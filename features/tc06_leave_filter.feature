@regression
Feature: Filter and Action - Leave filter by keyword

    Scenario: Leave filter result when searching by specific keywords
        Given user logs into HRMS and opens My Leave page
        When user clicks on searches a keyword in Leave Type or Reason Filter
        Then leave data should be filtered as per the entered keyword