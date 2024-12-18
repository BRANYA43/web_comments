from functools import wraps
from time import time, sleep
from typing import Callable, TypeVar, Iterable, Type, Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from selenium.common import (
    ElementClickInterceptedException,
    ElementNotVisibleException,
    ElementNotInteractableException,
    ElementNotSelectableException,
    NoSuchElementException,
    InvalidElementStateException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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
                    sleep(0.25)
                except Exception as e:
                    raise e

        return wrap

    return decorator


@explicit_wait(
    [
        ElementNotVisibleException,
        ElementNotInteractableException,
        ElementNotSelectableException,
        NoSuchElementException,
        InvalidElementStateException,
        StaleElementReferenceException,
    ]
)
def wait_for_element(
    fn: Callable[..., WebElement], is_disabled=True, is_enabled=True, expected_text: Any = None
) -> WebElement:
    element = fn()
    assert element.is_displayed() is is_disabled
    assert element.is_enabled() is is_enabled
    if expected_text is not None:
        assert element.text == expected_text
    return element


@explicit_wait([ElementClickInterceptedException])
def wait_to_click(fn: Callable[..., WebElement]):
    wait_for_element(fn).click()


@explicit_wait([ObjectDoesNotExist])
def wait_to_get_model_instance(model: Type[TModel], **kwargs) -> TModel:
    return model.objects.get(**kwargs)


def call_delay(fn: Callable[..., T], delay=0.25) -> T:
    sleep(delay)
    return fn()


def submit_form(form: WebElement, data: dict[str, Any]):
    for field, value in data.items():
        form.find_element(value=field).send_keys(value)
    call_delay(form.submit)


def login_user(webdriver: WebDriver, email: str, password: str):
    wait_to_click(lambda: webdriver.find_element(value='nav_login'))
    form = wait_for_element(lambda: webdriver.find_element(value='login_form'))
    submit_form(form, {'email_field': email, 'password_field': password})
