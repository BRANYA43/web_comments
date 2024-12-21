import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from comments.models import Comment
from tests.comments.conftest import get_uploaded_file, get_uploaded_image
from tests.selenium.tools import wait_to_click, wait_to_scroll, login_user, call_delay, wait_to_get_model_instance


@pytest.mark.django_db(transaction=True)
class TestCommentCreate:
    def test_user_create_new_main_comment(self, selenium, wait_driver, live_server, rick):
        # user enters to the site
        selenium.get(live_server.url)

        # user logs in
        login_user(wait_driver, rick.email, rick.raw_password)

        # user opens editor modal form and creates comment
        create_link = wait_driver.until(ec.element_to_be_clickable((By.ID, 'nav_create_comment')))
        wait_to_click(create_link)
        editor_form = wait_driver.until(ec.visibility_of_element_located((By.ID, 'editor_form')))
        div_text = editor_form.find_element(By.CSS_SELECTOR, '#text_editor div[contenteditable="true"]')
        div_text.send_keys('Some Text from Rick')
        call_delay(editor_form.submit)

        # wait created comment
        wait_to_get_model_instance(Comment, user=rick)
        selenium.refresh()

        # user sees his comment in the table
        comment = wait_driver.until(ec.visibility_of_element_located((By.CSS_SELECTOR, '#comment_table tbody tr')))
        comment_text = comment.find_element(By.CSS_SELECTOR, 'td.w-100 div.text-truncate-multiline').text
        rick.refresh_from_db()
        comment_instance = rick.comment_set.first()
        assert comment_text in comment_instance.text


@pytest.mark.django_db(transaction=True)
class TestCommentsAndAnswers:
    @pytest.fixture()
    def simple_comment(self, comment_factory, rick):
        return comment_factory(user=rick)

    @pytest.fixture()
    def comment_with_media(self, comment_factory, rick):
        return comment_factory(user=rick, image=get_uploaded_file(), file=get_uploaded_image())

    @pytest.fixture()
    def main_comment_with_answers(self, comment_factory, rick, morty):
        main_comment = comment_factory.create(user=rick)
        answers = comment_factory.create_batch(30, user=morty, target=main_comment)
        return main_comment, answers

    @pytest.fixture()
    def main_comment_with_cascade_answers(self, comment_factory, rick, morty):
        main_comment = comment_factory.create(user=rick)
        answer_1_of_main_comment = comment_factory.create(user=morty, target=main_comment)
        answer_2_of_answer_1 = comment_factory.create_batch(30, user=rick, target=answer_1_of_main_comment)
        return main_comment, answer_1_of_main_comment, answer_2_of_answer_1

    def test_user_reads_simple_comment(self, selenium, wait_driver, live_server, simple_comment):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the comment and click on the read icon
        read_link = wait_driver.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#comment_table a[name="read"]')))
        wait_to_click(read_link)

        # user doesnt sees table
        wait_driver.until(ec.invisibility_of_element_located((By.ID, 'table_block')))

        # user can't look at image and file
        comment = wait_driver.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, '[data-comment-type="main_comment"]'))
        )
        wait_comment = WebDriverWait(comment, timeout=3)
        wait_comment.until(ec.invisibility_of_element_located((By.ID, 'image')))
        wait_comment.until(ec.invisibility_of_element_located((By.ID, 'file')))

        # user returns to table
        return_link = wait_driver.until(ec.element_to_be_clickable((By.ID, 'return')))
        wait_to_click(return_link)
        wait_driver.until(ec.visibility_of_element_located((By.ID, 'table_block')))

    def test_user_reads_comment_with_image_and_file(
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

    def test_user_reads_answers_of_main_comment(self, selenium, wait_driver, live_server, main_comment_with_answers):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the comment and click on the read icon
        read_link = wait_driver.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#comment_table a[name="read"]')))
        wait_to_click(read_link)

        # user sees 25 answers of the main comment
        comment_element = wait_driver.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-comment-type="main_comment"]'))
        )
        wait_comment = WebDriverWait(comment_element, timeout=3)
        answer_elements = wait_comment.until(
            ec.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="answer_block"] div[data-comment-type="answer"]')
            )
        )
        assert len(answer_elements) == 25

        # user scrolls to down and click on show comments yet link
        show_comments_yet_link = wait_comment.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, '[id^="show_comments_yet"]'))
        )
        wait_to_scroll(selenium, show_comments_yet_link)
        wait_to_click(show_comments_yet_link)

        # user sees that answers count have become 30
        answer_elements = wait_comment.until(
            ec.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="answer_block"] div[data-comment-type="answer"]')
            )
        )
        assert len(answer_elements) == 30

    def test_user_reads_answers_of_other_answers_of_main_comment(
        self, selenium, wait_driver, live_server, main_comment_with_cascade_answers
    ):
        # user enters to the site
        selenium.get(live_server.url)

        # user sees the comment and click on the read icon
        read_link = wait_driver.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#comment_table a[name="read"]')))
        wait_to_click(read_link)

        # user sees the answer of the main comment
        comment_element = wait_driver.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-comment-type="main_comment"]'))
        )
        wait_main_comment = WebDriverWait(comment_element, timeout=3)
        answer_elements = wait_main_comment.until(
            ec.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="answer_block"] div[data-comment-type="answer"]')
            )
        )
        assert len(answer_elements) == 1

        # user clicks on show answer link of answer of main comment
        answer = answer_elements[0]
        wait_answer_1 = WebDriverWait(answer, timeout=3)
        show_answer_link = wait_answer_1.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '[name="show_answers"]')))
        wait_to_click(show_answer_link)

        # user sees appeared answers of first answers
        answer_elements = wait_answer_1.until(
            ec.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="answer_block"] div[data-comment-type="answer"]')
            )
        )
        assert len(answer_elements) == 25

        # user scrolls to down and click on show comments yet link
        show_comments_yet_link = wait_main_comment.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, '[id^="show_comments_yet"]'))
        )
        wait_to_scroll(selenium, show_comments_yet_link)
        wait_to_click(show_comments_yet_link)

        # user sees that answers count have become 30
        answer_elements = wait_answer_1.until(
            ec.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="answer_block"] div[data-comment-type="answer"]')
            )
        )
        assert len(answer_elements) == 30
