from time import sleep

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from comments.models import Comment
from tests.selenium.tools import wait_to_scroll, wait_to_click


@pytest.mark.django_db(transaction=True)
class TestCommentTable:
    comments_10 = 10
    comments_200 = 200

    def check_active_paginate_link(self, driver: WebDriverWait, id, *, expect=True):
        if expect:
            fn = driver.until
        else:
            fn = driver.until_not
        fn(ec.text_to_be_present_in_element_attribute((By.ID, id), 'class', 'active'))

    def check_disabled_paginate_link(self, driver: WebDriverWait, id, *, expect=True):
        if expect:
            fn = driver.until
        else:
            fn = driver.until_not
        fn(ec.text_to_be_present_in_element_attribute((By.ID, id), 'class', 'disabled'))

    def get_wait_paginator(self, wait_driver: WebDriverWait, selenium) -> WebDriverWait:
        paginator = wait_driver.until(ec.visibility_of_element_located((By.ID, 'table_paginator')))
        wait_to_scroll(selenium, paginator)
        return WebDriverWait(paginator, timeout=3)

    @pytest.fixture()
    def test_10_comments(self, comment_factory, rick):
        return comment_factory.create_batch(self.comments_10, user=rick)

    @pytest.fixture()
    def test_200_comments(self, comment_factory, rick):
        return comment_factory.create_batch(self.comments_200, user=rick)

    def test_user_sees_empty_table_if_table_has_no_comments(self, selenium: WebDriver, wait_driver, live_server):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the empty table
        wait_driver.until(ec.visibility_of_element_located((By.ID, 'empty_row')))

        # user doesnt see paginator
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'table_paginator')))

    def test_user_sees_comments_in_table(self, selenium: WebDriver, wait_driver, live_server, test_10_comments):
        sorted_comments = Comment.objects.filter(target__isnull=True).order_by('-created')
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the full table
        rows = wait_driver.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'table#comment_table tbody > tr:not(#empty_row)'))
        )

        # user sees that comments are sorted by descending column of created date
        for row, comment in zip(rows, sorted_comments):
            assert row.get_attribute('id') == str(comment.uuid)

        # user doesnt see paginator
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'table_paginator')))

    def test_user_uses_first_and_last_buttons_of_paginator(
        self, selenium: WebDriver, wait_driver, live_server, test_200_comments
    ):
        # user enters to the site
        selenium.get(live_server.url)

        # user scrolls to down and sees paginator
        wait_paginator = self.get_wait_paginator(wait_driver, selenium)
        self.check_active_paginate_link(wait_paginator, 'page_1')
        self.check_disabled_paginate_link(wait_paginator, 'first_page')
        self.check_disabled_paginate_link(wait_paginator, 'previous_page')
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

        # user switches to the last page
        last_link = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'last_page')))
        wait_to_click(last_link)
        wait_paginator.until(ec.invisibility_of_element_located((By.ID, 'page_1')))
        self.check_active_paginate_link(wait_paginator, 'page_8')
        self.check_disabled_paginate_link(wait_paginator, 'first_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'previous_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'next_page')
        self.check_disabled_paginate_link(wait_paginator, 'last_page')

        # user switches back to the first page
        first_link = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'first_page')))
        wait_to_click(first_link)
        wait_paginator.until(ec.invisibility_of_element_located((By.ID, 'page_8')))
        self.check_active_paginate_link(wait_paginator, 'page_1')
        self.check_disabled_paginate_link(wait_paginator, 'first_page')
        self.check_disabled_paginate_link(wait_paginator, 'previous_page')
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

    def test_user_uses_previous_and_next_buttons_of_paginator(
        self, selenium: WebDriver, wait_driver, live_server, test_200_comments
    ):
        # user enters to the site
        selenium.get(live_server.url)

        # user scrolls to down and sees paginator
        wait_paginator = self.get_wait_paginator(wait_driver, selenium)
        self.check_active_paginate_link(wait_paginator, 'page_1')
        self.check_disabled_paginate_link(wait_paginator, 'first_page')
        self.check_disabled_paginate_link(wait_paginator, 'previous_page')
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

        # user switches to the next page
        next_link = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'next_page')))
        wait_to_click(next_link)
        self.check_active_paginate_link(wait_paginator, 'page_1', expect=False)
        self.check_active_paginate_link(wait_paginator, 'page_2')
        self.check_disabled_paginate_link(wait_paginator, 'first_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'previous_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

        # user switches to the previous page
        previous_link = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'previous_page')))
        wait_to_click(previous_link)
        self.check_active_paginate_link(wait_paginator, 'page_2', expect=False)
        self.check_active_paginate_link(wait_paginator, 'page_1')
        self.check_disabled_paginate_link(wait_paginator, 'first_page')
        self.check_disabled_paginate_link(wait_paginator, 'previous_page')
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

    def test_user_uses_page_buttons_of_paginator(
        self, selenium: WebDriver, wait_driver, live_server, test_200_comments
    ):
        # user enters to the site
        selenium.get(live_server.url)

        # user scrolls to down and sees paginator
        wait_paginator = self.get_wait_paginator(wait_driver, selenium)
        self.check_active_paginate_link(wait_paginator, 'page_1')
        self.check_disabled_paginate_link(wait_paginator, 'first_page')
        self.check_disabled_paginate_link(wait_paginator, 'previous_page')
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)

        # user switches to page 3
        page_3 = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'page_3')))
        wait_to_click(page_3)
        self.check_active_paginate_link(wait_paginator, 'page_1', expect=False)
        self.check_active_paginate_link(wait_paginator, 'page_3')
        self.check_disabled_paginate_link(wait_paginator, 'first_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'previous_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)
        visible_page_links = wait_paginator.until(
            ec.visibility_of_all_elements_located((By.CSS_SELECTOR, '[id^="page_"]'))
        )
        assert len(visible_page_links) == 5
        for i, link in enumerate(visible_page_links, start=1):
            assert f'page_{i}' == link.get_attribute('id')

        # user switches to page 5
        sleep(10)
        page_5 = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'page_5')))
        wait_to_click(page_5)
        self.check_active_paginate_link(wait_paginator, 'page_3', expect=False)
        self.check_active_paginate_link(wait_paginator, 'page_5')
        self.check_disabled_paginate_link(wait_paginator, 'first_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'previous_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)
        visible_page_links = wait_paginator.until(
            ec.visibility_of_all_elements_located((By.CSS_SELECTOR, '[id^="page_"]'))
        )
        assert len(visible_page_links) == 5
        for i, link in enumerate(visible_page_links, start=3):
            assert f'page_{i}' == link.get_attribute('id')

        # user switches to page 7
        page_7 = wait_paginator.until(ec.element_to_be_clickable((By.ID, 'page_7')))
        wait_to_click(page_7)
        self.check_active_paginate_link(wait_paginator, 'page_5', expect=False)
        self.check_active_paginate_link(wait_paginator, 'page_7')
        self.check_disabled_paginate_link(wait_paginator, 'first_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'previous_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'next_page', expect=False)
        self.check_disabled_paginate_link(wait_paginator, 'last_page', expect=False)
        visible_page_links = wait_paginator.until(
            ec.visibility_of_all_elements_located((By.CSS_SELECTOR, '[id^="page_"]'))
        )
        assert len(visible_page_links) == 5
        for i, link in enumerate(visible_page_links, start=4):
            assert f'page_{i}' == link.get_attribute('id')
