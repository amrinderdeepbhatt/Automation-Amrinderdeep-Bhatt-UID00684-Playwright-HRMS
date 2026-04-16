@regression
Feature: Filter and Action - Leave filter by keyword

    Background:
        Given user opens the HRMS login page
        When user logs in with valid credentials from test data

    Scenario: Leave filter result when searching by specific keywords
        When user opens My Leave page
        And user opens leave filter search
        And user enters keyword in Leave Type filter
        Then leave data should be filtered as per the entered keyword
        