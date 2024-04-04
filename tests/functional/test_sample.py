from pytest_bdd import scenario, given, when, then

@scenario('../../features/sample.feature', 'Integration works properly')
def test_sample():
  pass

@given("python-bdd is installed")
def sample_given():
  pass

@when("I run this scenario")
def sample_when():
  pass

@then("it should not raise errors")
def sample_then():
  pass
