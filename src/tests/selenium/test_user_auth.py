import pytest
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from tests.selenium.tools import submit_form, login_user, wait_to_get_model_instance

GeneralUser = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserRegister:
    test_email = 'shurup@test.com'
    test_username = 'shurup1234'
    test_password = 'shuruppassword1234'

    def test_user_registers(self, selenium: WebDriver, wait_driver, live_server):
        # user enters to the site
        selenium.get(live_server.url)
        selenium.fullscreen_window()

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
        login_user(wait_driver, self.test_email, self.test_password)

        # user sees his email into the navbar
        wait_driver.until(ec.text_to_be_present_in_element((By.ID, 'nav_user_menu'), self.test_email))


@pytest.mark.django_db(transaction=True)
class TestUserLogout:
    def test_user_logs_out(self, selenium: WebDriver, wait_driver, live_server, rick):
        # user enters to the site
        selenium.get(live_server.url)

        # user opens modal of login form and inputs his credentials in the form and submits it
        login_user(wait_driver, rick.email, rick.raw_password)

        # user doesn't see his email into the navbar
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'nav_user_menu')))
        wait_driver.until(ec.visibility_of_element_located((By.ID, 'nav_login')))


@pytest.mark.django_db(transaction=True)
class TestUserLogin:
    def test_user_logs_in(self, selenium: WebDriver, wait_driver, live_server, rick):
        # user enters to the site
        selenium.get(live_server.url)

        # user opens modal of login form
        selenium.find_element(value='nav_login').click()

        # user inputs his credentials in the form and submits it
        form = wait_driver.until(ec.visibility_of_element_located((By.ID, 'login_form')))
        submit_form(form, {'email_field': rick.email, 'password_field': rick.raw_password})

        # user sees his email into the navbar
        wait_driver.until(ec.text_to_be_present_in_element((By.ID, 'nav_user_menu'), rick.email))
