import pytest
from fixture.all_methods import StepAndMethod


@pytest.fixture(scope='session')
def environment(request):
    """
    The fixture for test-suit with structure py.test
    :param request:
    :return: fixture for Test Framework.
    """
    fixture = StepAndMethod()
    request.addfinalizer(fixture.cleaning)
    return fixture
