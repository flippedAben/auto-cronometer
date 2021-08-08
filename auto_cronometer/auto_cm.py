from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
)
import os
import logging
from tqdm import tqdm

_logger = logging.getLogger(__name__)


class AutoCronometer():
    def __init__(self):
        self.driver = webdriver.Firefox(
            executable_path=os.environ.get('geckodriver_path'),
            log_path=os.environ.get('geckodriver_log_path'))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def login(self):
        self.driver.get('https://cronometer.com/login/')
        user_ele = self.driver.find_element_by_name('username')
        pass_ele = self.driver.find_element_by_name('password')
        user_ele.send_keys(os.environ.get('cronometer_user'))
        pass_ele.send_keys(os.environ.get('cronometer_pass'))

        submit_button = self.driver.find_element_by_id('login-button')
        submit_button.click()

        # Wait for login to bring us to the main website
        self.wait_on_ele_id('navArea')
        _logger.info('Logged in')

    def wait_on_ele_id(self, id_name):
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((
                By.ID,
                id_name)))

    def wait_on_ele_class(self, class_name):
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((
                By.CLASS_NAME,
                class_name)))

    def robust_click(self, element):
        """
        Sometimes the "Subscribe to Cronometer Gold" dialog pops up, which can
        block a Selenium mouse click. This will close that dialog before trying
        to click the given element.
        """
        try:
            log_attrs(element, 'Clicking element')
            element.click()
        except ElementClickInterceptedException:
            # Close the dialog
            dialog = self.driver.find_element_by_class_name('popupContent')
            cancel_button = dialog.find_element_by_tag_name('button')
            cancel_button.click()
            _logger.info('Closed subscription popup dialog!')

            # Retry
            element.click()

    def go_to_recipes_tab(self):
        self.driver.get('https://cronometer.com/#foods')
        self.wait_on_ele_class('gwt-DecoratedTabPanel')

        tabs = self.driver.find_elements_by_class_name(
            'gwt-TabBarItem-wrapper')
        for tab in tabs:
            tab_label = tab.find_element_by_class_name('gwt-Label')
            if tab_label.text.endswith('Recipes'):
                self.robust_click(tab_label)
                break

    def get_recipes_tab_page(self):
        # This should get the entire page under "Custom Recipes"
        custom_recipes_h = self.driver.find_element_by_tag_name('h2')
        log_attrs(custom_recipes_h, 'custom_recipes_h')
        parent = custom_recipes_h.find_element_by_xpath('..')
        log_attrs(parent, 'parent')
        grand_parent = parent.find_element_by_xpath('..')
        log_attrs(grand_parent, 'grand_parent')
        return grand_parent

    def get_recipe_page_sources(self):
        recipes = self.get_recipes_list_items()
        htmls = []
        for recipe in tqdm(recipes):
            self.robust_click(recipe)
            # Wait for page to fully load
            self.wait_on_ele_class('admin-food-editor-content-area')
            htmls.append(self.driver.page_source)
        return htmls

    def get_recipe_details_pane(self, recipe_list_item):
        # Click on the recipe list item to show the pane
        self.robust_click(recipe_list_item)
        self.wait_on_ele_class('admin-food-name')

        # Get the details
        parent = self.get_recipes_tab_page()
        recipe_details_pane = parent.find_element_by_class_name(
            'admin-food-editor-content-area')
        return recipe_details_pane

    def get_recipe_title(self, recipe_details_pane):
        admin_food_name = recipe_details_pane.find_element_by_class_name(
            'admin-food-name')
        recipe_title_div = admin_food_name.find_element_by_xpath('..')
        return recipe_title_div

    def get_recipes_list_items(self):
        parent = self.get_recipes_tab_page()
        temp = parent.find_element_by_class_name('inline')
        temp = temp.find_element_by_tag_name('div')
        temp = temp.find_element_by_tag_name('div')
        recipes_list = temp.find_element_by_tag_name('tbody')
        log_attrs(recipes_list, 'recipes_list')
        recipes_list_items = recipes_list.find_elements_by_tag_name('a')
        return recipes_list_items


def log_attrs(ele, name):
    cls = ele.get_attribute('class')
    style = ele.get_attribute('style')
    _logger.info(f'{name}: {cls} | {style}')
