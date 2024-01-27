from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, urljoin
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import InvalidSessionIdException, ElementClickInterceptedException
import time
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urljoin, urlparse


def get_hrefs_html(response, follow_foreign_hosts=False):
    urls = set()
    output = []
    soup = BeautifulSoup(response.text, "lxml")
    parsed_response_url = urlparse(response.url)
    urls_on_page = [link.attrs.get("href") for link in soup.find_all('a')]

    for url in urls_on_page:

        if url not in urls:

            follow = True
            parsed_url = urlparse(url)

            if not parsed_url.path:
                continue

            if not parsed_url.netloc:
                url = urljoin(response.url, parsed_url.path)
                parsed_url = urlparse(url)

            if parsed_response_url.netloc != parsed_url.netloc and not follow_foreign_hosts:
                follow = False

            urls.add(url)
            output.append({"url": url, "follow": follow})

    return output


def handle_url_list_js(output_list, new_urls, parsed_response_url, follow_foreign_hosts):
    urls_present = [x['url'] for x in output_list]
    new_output = []

    for url in new_urls:

        if url not in urls_present:

            follow = True
            parsed_url = urlparse(url)

            if parsed_response_url.netloc != parsed_url.netloc and not follow_foreign_hosts:
                follow = False

            urls_present.append(url)
            new_output.append({"url": url, "follow": follow})

    return new_output


def get_hrefs_js_simple(response, follow_foreign_hosts=False):
    parsed_response_url = urlparse(response.url)
    try:
        response.html.render(reload=False)
        urls_on_page = response.html.absolute_links
    except Exception:
        return get_hrefs_html(response, follow_foreign_hosts)

    return handle_url_list_js([], urls_on_page, parsed_response_url, follow_foreign_hosts)


def is_valid_link(link):
    if not link or link == "#" or link == "":
        return False
    return True


def make_element_id(element):
    id_str = ""

    css_properties = ["font-size", "font-weight", "margin", "padding", "color", "position", "display"]

    try:
        id_str += "text=" + str(element.text) + ";"

        for k, s in element.size.items():
            id_str += str(k) + "=" + str(s) + ";"

        for k, s in element.location_once_scrolled_into_view.items():
            id_str += str(k) + "=" + str(s) + ";"

        for k in css_properties:
            id_str += str(k) + "=" + str(element.value_of_css_property(k)) + ";"

    except Exception:
        return None

    return id_str


class ClickCrawler:

    def __init__(self, process_handler, executable_path, response, follow_foreign_hosts=False):

        self.process_handler = process_handler
        self.executable_path = executable_path
        self.driver = None
        self.handled = []
        self.main_url = response.url
        self.follow_foreign_hosts = follow_foreign_hosts

        self.iterations_limit = 10

    def load_driver(self):

        # kill all other spawned processes in case they are not terminated yet
        self.process_handler.kill_all()

        driver_options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        driver_options.set_preference("general.useragent.override", user_agent)
        driver_options.headless = True
        gecko_path = self.executable_path  # path to your geckodriver
        service = Service(gecko_path)
        self.driver = webdriver.Firefox(service=service, options=driver_options)
        #self.driver = webdriver.Firefox(executable_path=self.executable_path, options=driver_options)

        self.process_handler.register_new_process(self.driver.service.process.pid)

        # Open url
        self.driver.get(self.main_url)
        try:
            time.sleep(3)
            consent_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/a[1]')
            consent_button.click()
            ok_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/button/span/span')
            ok_button.click()
            print("Clicked cookie consent button")
        except NoSuchElementException:
            print("No cookie consent button found")
        except Exception as e:
            print(f"Error clicking cookie consent button: {e}")
        print("Opened url")
    def refresh_page(self):
        try:
            self.driver.refresh()
        except Exception:
            self.load_driver()

    def is_clickable(self, element):
        return element.is_displayed() and element.is_enabled()
    #Versao mais antiga
    # def find_next_clickable_element(self, tried_refresh=False):
    #     try:
    #         #elements = self.driver.find_elements_by_css_selector("*")
    #         elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
    #         # Go through all elements on page and look where the cursor is a pointer
    #         for k, element in enumerate(elements):
    #             if element.size['height'] > 0 and element.size['width'] > 0 and not is_valid_link(element.get_attribute("href")) and element.value_of_css_property(
    #                     "cursor") == "pointer" and element.value_of_css_property("display") != "none":
    #                 el_id = make_element_id(element)
    #                 if el_id not in self.handled and el_id is not None:
    #                     print(f"Clickable element found: {el_id}")
    #                     logging.debug(f"Found clickable element: ID={el_id}, size={element.size}, href={element.get_attribute('href')}")
    #                     return element, el_id
    #         logging.debug("No clickable element found.")
    #     except Exception as e:
    #         print(f"Error in find_next_clickable_element: {e}")
    #         logging.error(f"Error in find_next_clickable_element: {e}")
    #         if not tried_refresh:
    #             self.load_driver()
    #             return self.find_next_clickable_element(True)

    #    return None, None
    #Versao mais recente
    # def find_next_clickable_element(self, tried_refresh=False):
    #     try:
    #         elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, input[type='button']")
    #         #elements = self.driver.find_elements(By.CSS_SELECTOR, "")
    #         for element in elements:
    #             if element.is_displayed() and self.is_clickable(element) and not is_valid_link(element.get_attribute("href")):
    #                 el_id = make_element_id(element)
    #                 print(f"Clickable element found: {el_id}")
    #                 if el_id in self.handled:
    #                     print("continue")
    #                     continue
    #                 if el_id not in self.handled and el_id is not None:
    #                     print(f"Clickableeeeeeeeee element found: {el_id}")
    #                     if self.is_clickable(element) and not is_valid_link(element.get_attribute("href")) and \
    #                             element.value_of_css_property("cursor") == "pointer":
    #                         print(f"Clickable element found: {el_id}")
    #                         logging.debug(f"Found clickable element: ID={el_id}, size={element.size}, href={element.get_attribute('href')}")
    #                         return element, el_id
    #             print("No clickable element found.")
    #             logging.debug("No clickable element found.")
    #     except Exception as e:
    #         logging.error(f"Error in find_next_clickable_element: {e}")
    #         if not tried_refresh:
    #             self.load_driver()
    #             return self.find_next_clickable_element(True)

    #     return None, None
    def contains_pdf(self, element):
        # Check href attribute for 'pdf' keyword in any position
        href = element.get_attribute("href")
       # print(f"href: {href}")
        if href and "pdf" in href.lower():
            return True
        # Check other attributes for 'pdf' keyword
        # for attribute in ['id']:
        #     attr_value = element.get_attribute(attribute)
        #     if attr_value and "pdf" in attr_value.lower():
        #         return True
        return False
    
    def find_next_clickable_element(self, tried_refresh=False):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "*")  # Search all elements
            for element in elements:
                href = element.get_attribute("href")
                if element.is_displayed() and self.is_clickable(element) and (self.contains_pdf(href) or href is not None):
                    el_id = make_element_id(element)
                    if el_id in self.handled:
                        continue
                    if el_id not in self.handled and el_id is not None:
                        print(f"PDF element found: {el_id}")
                      #  logging.debug(f"PDF element found: ID={el_id}, size={element.size}, href={element.get_attribute('href')}")
                        return element, el_id
            #logging.debug("No PDF element found.")
        except Exception as e:
           # logging.error(f"Error in find_next_clickable_element: {e}")
            if not tried_refresh:
                self.load_driver()
                return self.find_next_clickable_element(True)

        return None, None

    def find_element_by_id(self, element_id):
        #elements = self.driver.find_elements_by_css_selector("*")
        #elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, input[type='button']")
        elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
        for el in elements:
            el_id = make_element_id(el)
            if el_id == element_id:
                return el
        return None

    def get_new_urls_with_click(self, click_next_element, next_element_id, tried_refresh=False):

        new_urls_on_page = []

        if click_next_element is None:
            click_next_element = self.find_element_by_id(next_element_id)
            if click_next_element is None:
                return new_urls_on_page

        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(click_next_element).perform()
            #WebDriverWait(self.driver, 0.5).until(EC.element_to_be_clickable((By.ID, next_element_id)))
            #click_next_element.click()
            click_next_element.click()

            if self.driver.current_url != self.main_url:
                # reload the page if the url changed
                self.driver.get(self.main_url)
                print(f"Clicked on element ID={next_element_id}, url changed, reloading page.")
            else:
                # sleep to allow for eventual ajax to load
                #time.sleep(0.5)

                new_urls_on_page = [link.get_attribute("href") for link in \
                                    self.driver.find_elements(By.CSS_SELECTOR, "a") \
                                    if is_valid_link(link.get_attribute("href"))]
                print(f"Clicked on element ID={next_element_id}, new URLs found: {new_urls_on_page}")
               # logging.debug(f"Clicked on element ID={next_element_id}, new URLs found: {new_urls_on_page}")
        except Exception as e:
          #  logging.error(f"Error in get_new_urls_with_click: {e}")
            print(f"Error in get_new_urls_with_click: {e}")
            if not tried_refresh:
                # couldn't click on element, try once again with page refresh
                self.refresh_page()
                return self.get_new_urls_with_click(None, next_element_id, True)

        return new_urls_on_page

    # def get_hrefs_js_complex(self):
    #     urls = []
    #     parsed_response_url = urlparse(self.main_url)

    #     # get driver
    #     self.load_driver()

    #     self.main_url = self.driver.current_url

    #     urls_on_page = [link.get_attribute("href") for link in \
    #                     self.driver.find_elements(By.CSS_SELECTOR, "a") \
    #                     if is_valid_link(link.get_attribute("href"))]

    #     urls += handle_url_list_js(urls, urls_on_page, parsed_response_url, self.follow_foreign_hosts)

    #     # get clickable elements
    #     self.handled = []
    #     iterations = 0
    #     while iterations < self.iterations_limit:
            
    #         iterations += 1
    #         print(f"Iteration {iterations}")
    #         click_next_element, next_id = self.find_next_clickable_element()

    #         if click_next_element is None:
    #             break

    #         self.handled.append(next_id)

    #         new_urls_on_page = self.get_new_urls_with_click(click_next_element, next_id)
    #         print(f"New urls on page: {new_urls_on_page}")
    #         urls += handle_url_list_js(urls, new_urls_on_page, parsed_response_url, self.follow_foreign_hosts)

    #     self.driver.close()
    #     self.process_handler.kill_all()

    #     return urls
    def get_hrefs_js_complex(self):
        urls = []
        parsed_response_url = urlparse(self.main_url)

        # get driver
        self.load_driver()

        self.main_url = self.driver.current_url

        # Extract initial set of URLs
        # urls_on_page = [link.get_attribute("href") for link in \
        #                 self.driver.find_elements(By.CSS_SELECTOR, "a") \
        #                 if is_valid_link(link.get_attribute("href")) and "pdf" in link.get_attribute("href").lower()]

        # urls += handle_url_list_js(urls, urls_on_page, parsed_response_url, self.follow_foreign_hosts)

        urls_on_page = [link.get_attribute("href") for link in \
                        self.driver.find_elements(By.CSS_SELECTOR, "a") \
                        if is_valid_link(link.get_attribute("href"))]

        urls += handle_url_list_js(urls, urls_on_page, parsed_response_url, self.follow_foreign_hosts)

        # get clickable elements
        self.handled = []
        iterations = 0
        while iterations < self.iterations_limit:
            iterations += 1
            print(f"Iteration {iterations}")
            click_next_element, next_id = self.find_next_clickable_element()

            if click_next_element is None or next_id in self.handled:
            #if click_next_element is None:
                print("break")
                break
            
            self.handled.append(next_id)
            new_urls_on_page = self.get_new_urls_with_click(click_next_element, next_id)
            new_pdf_urls = [url for url in new_urls_on_page if "pdf" in url.lower()]
            urls += handle_url_list_js(urls, new_pdf_urls, parsed_response_url, self.follow_foreign_hosts)
            print("urls: ", urls)
        self.driver.close()
        self.process_handler.kill_all()

        return urls
