import pytest
from django.contrib.auth import get_user_model
from selenium.webdriver.firefox.webdriver import WebDriver

from tests.selenium.tools import submit_form, wait_for_element, login_user, wait_to_get_model_instance

GeneralUser = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserRegister:
    test_email = 'shurup@test.com'
    test_username = 'shurup1234'
    test_password = 'shuruppassword1234'

    def test_user_registers(self, selenium: WebDriver, live_server):
        # user enters to the site
        selenium.get(live_server.url)

        # user opens modal of register form and inputs his credentials in the form and submits it
        selenium.find_element(value='nav_register').click()
        form = selenium.find_element(value='register_form')
        submit_form(
            form,
            {
                'email_field': self.test_email,
                'username_field': self.test_username,
                'password_field': self.test_password,
                'confirming_password_field': self.test_password,
            },
        )

        # user is dreaming
        wait_to_get_model_instance(GeneralUser, email=self.test_email)

        # user opens modal of login form and inputs his credentials in the form and submits it
        login_user(selenium, self.test_email, self.test_password)

        # user sees his email into the navbar
        wait_for_element(lambda: selenium.find_element(value='nav_user_menu'), expected_text=self.test_email)


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
