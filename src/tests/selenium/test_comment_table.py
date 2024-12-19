import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from comments.models import Comment


@pytest.mark.django_db(transaction=True)
class TestCommentTable:
    comments_10 = 10

    @pytest.fixture()
    def test_10_comments(self, comment_factory, rick):
        return comment_factory.create_batch(self.comments_10, user=rick)

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
