from functools import wraps
from time import time, sleep
from typing import Callable, TypeVar, Iterable, Type, Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from selenium.common import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

WebObj = WebElement | WebDriver
T = TypeVar('T')
TModel = TypeVar('TModel', bound=Model)


def explicit_wait(extra_errors: Iterable[Type[Exception]] = (), timeout=3):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrap(*args, **kwargs):
            start = time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (AssertionError, *extra_errors) as e:
                    end = time()
                    if end - start >= timeout:
                        raise e
                    sleep(0.5)
                except Exception as e:
                    raise e

        return wrap

    return decorator


@explicit_wait([ElementClickInterceptedException, ElementNotInteractableException])
def wait_to_click(element: WebElement):
    element.click()


@explicit_wait([ObjectDoesNotExist])
def wait_to_get_model_instance(model: Type[TModel], **kwargs) -> TModel:
    return model.objects.get(**kwargs)


@explicit_wait()
def wait_to_count_model_instance(model: Type[TModel], expected_count: int, **kwargs) -> bool:
    qs = model.objects.filter(**kwargs)
    assert qs.count() == expected_count
    return qs


def call_delay(fn: Callable[..., T], delay=0.5) -> T:
    sleep(delay)
    return fn()


@explicit_wait([ElementNotInteractableException, MoveTargetOutOfBoundsException])
def wait_to_scroll(driver: WebDriver, element: WebElement):
    driver.execute_script(f'window.scrollTo(0, {element.location['y']});')


def submit_form(form: WebElement, data: dict[str, Any]):
    for field, value in data.items():
        form.find_element(value=field).send_keys(value)
    call_delay(form.submit)


def login_user(wait_driver: WebDriverWait, email: str, password: str):
    login_link = wait_driver.until(ec.element_to_be_clickable((By.ID, 'nav_login')))
    wait_to_click(login_link)
    form = wait_driver.until(ec.visibility_of_element_located((By.ID, 'login_form')))
    submit_form(form, {'email_field': email, 'password_field': password})


def send_comment(wait_driver, text: str):
    editor_form = wait_driver.until(ec.visibility_of_element_located((By.ID, 'editor_form')))
    div_text = editor_form.find_element(By.CSS_SELECTOR, '#text_editor div[contenteditable="true"]')
    div_text.send_keys(text)
    call_delay(editor_form.submit)
