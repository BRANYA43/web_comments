import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from tests.comments.conftest import get_uploaded_file, get_uploaded_image
from tests.selenium.tools import wait_to_click


@pytest.mark.django_db(transaction=True)
class TestCommentsAndAnswers:
    @pytest.fixture()
    def simple_comment(self, comment_factory, rick):
        return comment_factory(user=rick)

    @pytest.fixture()
    def comment_with_media(self, comment_factory, rick):
        return comment_factory(user=rick, image=get_uploaded_file(), file=get_uploaded_image())

    def test_user_read_simple_comment(self, selenium, wait_driver, live_server, simple_comment):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the comment and click on the read icon
        read_link = wait_driver.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#comment_table a[name="read"]')))
        wait_to_click(read_link)

        # user doesnt sees table
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'table_block')))

        # user checks text
        comment = wait_driver.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, '[data-comment-type="main_comment"]'))
        )
        text = comment.find_element(By.CLASS_NAME, 'card-text').text
        assert text == simple_comment.text

        # user can't look at image and file
        wait_comment = WebDriverWait(comment, timeout=3)
        wait_comment.until(ec.invisibility_of_element_located((By.ID, 'image')))
        wait_comment.until(ec.invisibility_of_element_located((By.ID, 'file')))

        # user returns to table
        return_link = wait_driver.until(ec.element_to_be_clickable((By.ID, 'return')))
        wait_to_click(return_link)
        wait_driver.until(ec.visibility_of_element_located((By.ID, 'table_block')))

    def test_user_read_comment_with_image_and_file(
        self, selenium, wait_driver, live_server, test_media_root, comment_with_media
    ):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the comment and click on the read icon
        read_link = wait_driver.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#comment_table a[name="read"]')))
        wait_to_click(read_link)

        # user doesnt sees table
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'table')))

        # user checks text
        comment = wait_driver.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, '[data-comment-type="main_comment"]'))
        )
        comment.find_element(By.CLASS_NAME, 'card-text')

        # user look at image and file
        comment.find_element(value='image')
        comment.find_element(value='file')

        # user returns to table
        return_link = wait_driver.until(ec.element_to_be_clickable((By.ID, 'return')))
        wait_to_click(return_link)
        wait_driver.until(ec.visibility_of_element_located((By.ID, 'table_block')))
