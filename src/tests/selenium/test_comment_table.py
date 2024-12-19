import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from comments.models import Comment
from tests.selenium.tools import wait_for_element, wait_for_elements


@pytest.mark.django_db(transaction=True)
class TestCommentTable:
    def test_user_see_empty_table_if_table_has_no_comments(self, selenium: WebDriver, live_server):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the empty table
        wait_for_element(lambda: selenium.find_element(value='comment_table').find_element(value='empty_row'))

    def test_user_see_comments_in_table(self, selenium: WebDriver, live_server, comment_factory, rick):
        comment_factory.create_batch(10, user=rick)
        sorted_comments = Comment.objects.filter(target__isnull=True).order_by('-created')

        # user enters to the site
        selenium.get(live_server.url)

        # user sees the full table
        rows = wait_for_elements(
            lambda: selenium.find_elements(by=By.CSS_SELECTOR, value='table#comment_table tbody > tr:not(#empty_row)'),
            expected_count=10,
        )

        # user sees that comments are sorted by descending column of created date
        for row, comment in zip(rows, sorted_comments):
            assert row.get_attribute('id') == str(comment.uuid)
