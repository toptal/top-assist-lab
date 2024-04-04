Feature: Sample feature testing pytest-bdd integration

  Scenario: Integration works properly
    Given python-bdd is installed
    When I run this scenario
    Then it should not raise errors
