import pytest
from selenium.webdriver.firefox.webdriver import WebDriver

from tests.selenium.tools import submit_form, wait_for_element, login_user


@pytest.mark.django_db(transaction=True)
class TestUserLogout:
    def test_user_logs_out(self, selenium: WebDriver, live_server, rick):
        # user enters to the site
        selenium.get(live_server.url)

        # user opens modal of login form and inputs his credentials in the form and submits it
        login_user(selenium, rick.email, rick.raw_password)

        # user sees his email into the navbar
        wait_for_element(lambda: selenium.find_element(value='nav_login'))


@pytest.mark.django_db(transaction=True)
class TestUserLogin:
    def test_user_logs_in(self, selenium: WebDriver, live_server, rick):
        # user enters to the site
        selenium.get(live_server.url)

        # user opens modal of login form
        selenium.find_element(value='nav_login').click()

        # user inputs his credentials in the form and submits it
        form = wait_for_element(lambda: selenium.find_element(value='login_form'))
        submit_form(form, {'email_field': rick.email, 'password_field': rick.raw_password})

        # user sees his email into the navbar
        wait_for_element(lambda: selenium.find_element(value='nav_user_menu'), expected_text=rick.email)
