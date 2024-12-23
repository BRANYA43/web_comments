import pytest
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def rick(user_factory):
    password = 'rickpassword1234'
    user = user_factory.create(email='rick@test.com', username='rick1234', password=password)
    user.raw_password = password
    return user


@pytest.fixture()
def morty(user_factory):
    password = 'mortypassword1234'
    user = user_factory.create(email='morty@test.com', username='morty1234', password=password)
    user.raw_password = password
    return user


@pytest.fixture()
def wait_driver(selenium) -> WebDriverWait:
    return WebDriverWait(
        selenium,
        timeout=3,
    )
