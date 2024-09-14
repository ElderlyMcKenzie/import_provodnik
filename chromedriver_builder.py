from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from os import path
from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass
from typing import Tuple, NamedTuple, Union, Literal, List, Callable
import string
import random
import undetected_chromedriver as uc
import logging
from pyvirtualdisplay import Display
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
from bs4 import BeautifulSoup
import uuid

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import seleniumwire.undetected_chromedriver as uc_sw
import os
import zipfile
import time
import requests
import json
import tkinter as tk
    # chrome_options.add_argument("--mute-audio")
    # caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "none"
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument('--disable-gpu')

class ChromeUserProfile:
    def __init__(self, home_dir: str, proxy: str='', proxy_uuid: str='',
                 visited_websites_without_registration: List[str]=[],
                 visited_websites_registration_in_progress: List[str]=[],
                 visited_websites_registration_completed: List[str]=[],
                 file_name: str='profiles_settings.json',
                 google_search_query_tail: str='',
                 geo_coordinates: Tuple[float, float]=tuple(),
                 all_google_queries: List[str]=[
                     'lofi hiphop', 'lotr music yt', 'bbc news yt', 'Simone Giertz youtube',
                     'FunForLouis', 'Marques Brownlee you tube', 'Binging With Babish channel',
                     'Thomas Heaton', 'Apartment Therapy', 'The Try Guys', 'The Slow Mo Guys',
                 ],
                 used_google_queries: List[str]=[],
                 google_acc_email: str='',
                 google_acc_password: str='',
                 google_acc_phone_number: str='',
                 google_acc_birthdate: str='',
                 fb_acc_email: str='',
                 fb_acc_password: str='',
                 ig_acc_email: str='',
                 ig_acc_password: str='',
                 profile_name: str=''):
        self.profile_name = profile_name
        self.home_dir = home_dir
        self.proxy = proxy
        self.proxy_uuid = proxy_uuid
        self.visited_websites_without_registration = visited_websites_without_registration
        self.visited_websites_registration_in_progress = visited_websites_registration_in_progress
        self.visited_websites_registration_completed = visited_websites_registration_completed
        self.file_name = file_name
        self.google_search_query_tail = google_search_query_tail
        self.geo_coordinates = geo_coordinates
        self.used_google_queries = used_google_queries
        self.all_google_queries = all_google_queries
        self.google_acc_email = google_acc_email
        self.google_acc_password = google_acc_password
        self.google_acc_phone_number = google_acc_phone_number
        self.google_acc_birthdate = google_acc_birthdate
        self.fb_acc_email = fb_acc_email
        self.fb_acc_password = fb_acc_password
        self.ig_acc_email = ig_acc_email
        self.ig_acc_password = ig_acc_password
        self._sync_profile_with_dump_file()

    def _sync_profile_with_dump_file(self):
        with open(self.file_name, 'r') as f:
            settings = json.load(f)
        self.is_first_run = self.home_dir not in settings
        if self.is_first_run:
            if not self.proxy_uuid:
                self.proxy_uuid = str(uuid.uuid4())
            self.dump_profile_settings_to_file()
        else:
            self.load_profile_settings_from_file()
            self.dump_profile_settings_to_file()    

    def dump_profile_settings_to_file(self):
        with open(self.file_name, 'r') as f:
            settings = json.load(f)
        profile = self.__dict__.copy()
        profile.pop("file_name")
        profile.pop("is_first_run")
        settings[self.home_dir] = profile
        with open(self.file_name, 'w') as f:
            json.dump(settings, f)

    def load_profile_settings_from_file(self):
        with open(self.file_name, 'r') as f:
            settings = json.load(f)
        profile = settings.get(self.home_dir, {})
        for k in profile:
            if not self.__getattribute__(k):
                self.__setattr__(k, profile[k])

def createproxy_extension(proxy_host, proxy_port, proxy_user, proxy_password):
    
    manifest_json = """
    {
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy (""" + f'{proxy_host}:{proxy_port})"' + """,
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
            username: "%s",
            password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_password )

    return manifest_json, background_js
    

def build_proxy_extension(proxy: str, proxy_uuid: str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pluginfile = os.path.join(dir_path, 'proxy_auth_plugins', 'proxy_auth_plugin'+proxy_uuid)
    if os.path.exists(pluginfile):
        return pluginfile
    proxy = proxy.replace("https://", "").replace("http://", "").strip()
    proxy_host, proxy_port = proxy.split("@")[-1].split(":")
    proxy_login, proxy_password = proxy.split("@")[0].split(":")
    manifest_json, background_js = createproxy_extension(proxy_host, proxy_port, proxy_login, proxy_password )
    if not proxy_uuid:
        proxy_uuid = str(uuid.uuid4())
    if os.path.exists(pluginfile):
        for i in os.listdir(pluginfile):
            os.remove(os.path.join(pluginfile, i))
    else:
        os.makedirs(pluginfile)
    with open(os.path.join(pluginfile, "manifest.json"), 'w') as file:
        file.write(manifest_json)
    with open(os.path.join(pluginfile, "background.js"), 'w') as file:
        file.write(background_js)
    return pluginfile

def set_geolocation(coords: Tuple[float, float], driver: webdriver.Chrome):
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": coords[0],
        "longitude": coords[1],
        "accuracy": 100
    })

def set_timezone(timezone_id: str, driver: webdriver.Chrome):
    # works only for current page (in yandex and google, other websites ok)
    # Script to check location in JS: 
    #   navigator.geolocation.getCurrentPosition(function(e) {console.log(e.coords)})
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {
        "timezoneId": timezone_id
    })

class UndetectableChromeCoordinatesAware(uc.Chrome):
    def __init__(self, coordinates: Tuple[float, float], timezone_id: str=None, *args, **kwargs):
        self.coordinates = coordinates
        self.timezone_id = timezone_id
        self._saved_init_args = {'coordinates': coordinates, 'timezone_id': timezone_id}
        self._saved_init_args_args = args
        self._saved_init_args_kwargs = kwargs
        super().__init__(*args, **kwargs)
    
    def update_timezone_and_geolocation(self):
        if self.coordinates:
            set_geolocation(self.coordinates, self)
        if  self.timezone_id:
            set_timezone(self.timezone_id, self)
    
    def get(self, *args, **kwargs):
        self.update_timezone_and_geolocation()
        super().get(*args, **kwargs)
        self.update_timezone_and_geolocation()

def driverInitializeUC(headless:bool=True, proxy:str=None, executable_path: str=None, 
                        home_dir: str=None, use_logs: bool=False, use_binary_location:bool=False,
                        custom_download_location: str=None, proxy_uuid: str=None,
                        custom_ua: str='',
                        locale: str='en-US',
                        extensions: List[str]=None,
                        coordinates: Tuple[float, float]=None,
                        timezone_id: str=None,
                        disable_images: bool=False,
                        user_data_dir: str=None,
                        mute_audio: bool=True):
    options = uc.ChromeOptions()
    if use_binary_location:
        options.binary_location = "/usr/bin/google-chrome"
    if headless:
        options.headless=True
        options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    if locale:
        options.add_argument("--lang="+locale)
    if home_dir:
        options.add_argument('--allow-profiles-outside-user-dir')
        options.add_argument('--enable-profile-shortcut-manager')
        if not user_data_dir:
            user_data_dir = Path(__file__).resolve().parent / 'User'
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--profile-directory='+home_dir)
    if use_logs and home_dir:
        service_log_path = f"{home_dir}/chromedriver.log"
        service_args = ['--verbose']
    if custom_download_location:
        options.add_experimental_option("prefs", {
                    "profile.default_content_settings.popups": 0,
                    "download.default_directory" : custom_download_location,
                    "directory_upgrade": True,
                    })
        options.add_experimental_option("prefs", {
            'profile.default_content_setting_values.automatic_downloads': 1
            })
    if custom_ua:
        options.add_argument(f'--user-agent={custom_ua}')
    extensions_strs = []
    if extensions:
        extensions_strs += extensions
    if proxy:
        extensions_strs += [build_proxy_extension(proxy, proxy_uuid)]
    if extensions_strs:
        extensions_strs = ",".join(extensions_strs)
        options.add_argument(f'--load-extension={extensions_strs}')
    if disable_images:
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    if mute_audio:
        options.add_argument("--mute-audio")
    chrome_class_init_options = {
        'use_subprocess': True, 'headless': headless, 'options': options
    }    
    if executable_path:
        chrome_class_init_options['driver_executable_path'] = executable_path
    else:
        chrome_class_init_options['service'] = Service(ChromeDriverManager().install())
    if use_logs and home_dir:
        chrome_class_init_options['service_args'] = service_args
        chrome_class_init_options['service_log_path'] = service_log_path
    if coordinates:
        chrome_class_init_options['coordinates'] = coordinates
    if timezone_id:
        chrome_class_init_options['timezone_id'] = timezone_id
    return UndetectableChromeCoordinatesAware(**chrome_class_init_options)

def extract_links_from_the_page(driver):
    inner_links = driver.find_elements(By.XPATH, "//a[not(contains(@href, 'http'))]")
    outer_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'http')]")
    return {
        'inner_links': inner_links,
        'outer_links': outer_links,
        'all_links': inner_links + outer_links,
    }

def is_link_will_open_in_new_tab(element):
    return element.get_attribute('target') == '_blank'

def is_element_in_viewport(driver: webdriver.Chrome, element):
    return driver.execute_script('''
        var elem = arguments[0];
        box = elem.getBoundingClientRect();
        cx = box.left + box.width / 2;
        cy = box.top + box.height / 2;
        e = document.elementFromPoint(cx, cy);
        for (; e; e = e.parentElement) {
            if (e === elem) 
                return true;
            } 
        return false
    ''', element)

def get_links_from_viewport(driver: webdriver.Chrome):
    links = extract_links_from_the_page(driver)
    inner_links=[link for link in links['inner_links'] if is_element_in_viewport(driver, link)]
    outer_links=[link for link in links['outer_links'] if is_element_in_viewport(driver, link)]
    return {
        'inner_links':inner_links,
        'outer_links':outer_links,
        'all_links':inner_links+outer_links,
    }

def hover_random_links(driver: webdriver.Chrome):
    links = get_links_from_viewport(driver)['all_links']
    if links:
        print(f'hover - {links[0].get_attribute("href")} - {links[0].get_attribute("innerText")}')
        for num in range(3):
            try:
                link = links[num]
                ActionChains(driver).move_to_element(link).perform()
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as err:
                print(err)
                print('hover failed')

def random_scroll(driver, times: int=30, steps_per_scroll: int=10, 
                  between_steps_sleep_min: float=1, between_steps_sleep_max: float=7,
                  func_to_do_between_steps: Callable=None, func_to_do_between_steps_args: Tuple=tuple(),
                  func_to_do_between_steps_execution_probability: float=0.5):
    scroll_height_max = int(driver.execute_script(f"return document.body.scrollHeight"))
    if scroll_height_max > 1:
        steps = 0
        multiplicator = 1
        for _ in range(times):
            steps += 1
            if steps > steps_per_scroll*random.uniform(0.75, 2):
                steps = 0
                multiplicator = -multiplicator
                time.sleep(random.uniform(between_steps_sleep_min, between_steps_sleep_max))
                if func_to_do_between_steps:
                    if random.choices([True, False], 
                                    [func_to_do_between_steps_execution_probability, 
                                    1-func_to_do_between_steps_execution_probability], k=1)[0]:
                        func_to_do_between_steps(*func_to_do_between_steps_args)
            scroll_value = multiplicator*random.randint(25, int(scroll_height_max*0.15))
            driver.execute_script(f"window.scrollBy(0, {scroll_value});")
            time.sleep(random.uniform(0.05, 0.15))

def move_and_click(driver: UndetectableChromeCoordinatesAware, element, 
                   time_to_sleep_before_click: float=0.01, smooth: bool=False,
                   auto_switch_to_new_tab: bool=True):
    if smooth:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", element)
    else:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
    time.sleep(time_to_sleep_before_click)
    new_tab_will_be_opened = is_link_will_open_in_new_tab(element)
    driver.update_timezone_and_geolocation()
    element.click()
    driver.update_timezone_and_geolocation()
    if auto_switch_to_new_tab:
        if new_tab_will_be_opened:
            driver.update_timezone_and_geolocation()
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            driver.update_timezone_and_geolocation()


random_sleep = lambda: time.sleep(random.randint(3, 6))
random_small_sleep = lambda: time.sleep(random.uniform(1.2, 2))
send_keys_to_elem = lambda driver, elem, keys_to_send: ActionChains(driver) \
                                                    .send_keys_to_element(elem, keys_to_send) \
                                                        .perform()


def create_driver(headless:bool=True, proxy:str=None, executable_path: str=None, home_dir: str=None, 
                    use_logs: bool=False, use_binary_location:bool=False, need_display: bool=False, proxy_uuid: str=None) \
                        -> Tuple[webdriver.Chrome, Union[Display, None]]:
    driver = driverInitializeUC(headless=headless, proxy=proxy, executable_path=executable_path,
                                home_dir=home_dir, use_logs=use_logs, use_binary_location=use_binary_location,
                                proxy_uuid=proxy_uuid)
    display = None
    if need_display:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    return driver, display

def close_all_tabs_after_refresh(driver: webdriver.Chrome, tabs_num: int=0):
    if tabs_num != 0:
        for _ in range(3):
            time.sleep(1)
            if len(driver.window_handles) == tabs_num:
                break
    for _ in range(len(driver.window_handles)-1):
        driver.switch_to.window(driver.window_handles[-1])
        driver.refresh()
        time.sleep(random.randint(1, 3))
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

def get_location_coordinates_by_ip(proxy: str=None):
    if proxy:
        loc = requests.get("http://ipinfo.io/json", 
                            proxies={'http': proxy, 'https': proxy}).json()['loc'].split(',')
    else:
        loc = requests.get("http://ipinfo.io/json").json()['loc'].split(',')
    return tuple(float(i) for i in loc)

def get_current_ip(proxy: str=None):
    if proxy:
        ip = requests.get("http://ipinfo.io/json", 
                            proxies={'http': proxy, 'https': proxy}).json()['ip']
    else:
        ip = requests.get("http://ipinfo.io/json").json()['ip']
    return ip

def driverInitializeUC__dolphin_like_selenium(proxy:str=None, proxy_uuid: str=None,
                                              timezone_id: str='Etc/UTC', 
                                              custom_ua: str='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
                                              coords: Tuple[float, float]=(53.3439862, -6.2676779),
                                              define_coords_by_ip: bool=False,
                                              locale: str="en-US",
                                              extensions: List[str]=None,
                                              home_dir: str='Profile 5',
                                              disable_images: bool=False,
                                              executable_path='',
                                              user_data_dir: str= Path("./").resolve().parent / 'User'):
    '''
    https://amiunique.org/fp
    '''
    driver = None
    try:
        if define_coords_by_ip:
            coords = get_location_coordinates_by_ip(proxy)
        driver = driverInitializeUC(headless=False, proxy=proxy, 
                                    executable_path=executable_path, 
                                    proxy_uuid=proxy_uuid,
                                    custom_ua=custom_ua,
                                    locale=locale,
                                    extensions=extensions,
                                    home_dir=home_dir,
                                    coordinates=coords,
                                    timezone_id=timezone_id,
                                    disable_images=disable_images,
                                    use_logs=False,
                                    user_data_dir=user_data_dir)
        for _ in range(10):
            if len(driver.window_handles) > 1:
                driver.maximize_window()
                break
            else:
                time.sleep(1)
                continue
        driver.update_timezone_and_geolocation()
        return driver
    except Exception as err:
        if driver:
            driver.quit()
        raise err

def recreate_chromedriver(driver: UndetectableChromeCoordinatesAware,
                          additional_arguments: List['str']=[],
                          additional_kwargs: List[dict]=[],
                          change_images_visibility: bool=False,
                          disable_images: bool=False):
    driver.quit()
    options_obj = driver._saved_init_args_kwargs.pop('options', None)
    if options_obj:
        options = uc.ChromeOptions()
        for i in options_obj.__dict__['_arguments']+additional_arguments:
            options.add_argument(i)
        for i in options_obj.__dict__['_experimental_options']:
            options.add_experimental_option(i, options_obj.__dict__['_experimental_options'][i])
        if additional_kwargs:
            for i in additional_kwargs:
                options.add_experimental_option(i, additional_kwargs[i])
        driver._saved_init_args_kwargs['options'] = options
        if change_images_visibility:
            if disable_images:
                options.add_argument('--blink-settings=imagesEnabled=false')
                options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            else:
                options.add_argument("--blink-settings=imagesEnabled=true")
                options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})
    driver = UndetectableChromeCoordinatesAware(*driver._saved_init_args_args, 
                                                **driver._saved_init_args_kwargs,
                                                **driver._saved_init_args)
    for _ in range(10):
        if len(driver.window_handles) > 1:
            driver.maximize_window()
            close_all_tabs_after_refresh(driver, 
                                len([i for i in driver._saved_init_args_kwargs['options'].__dict__['_arguments'] 
                                        if '--load-extension' in i][0].split(",")))
            break
        else:
            time.sleep(1)
            continue
    driver.update_timezone_and_geolocation()
    return driver


def _is_recaptcha_detected(driver) -> bool:
    try:
        driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge']")
        return True
    except:
        return False

def _is_captcha_detected(driver) -> bool:
    try:
        driver.find_element(By.XPATH, "//iframe[@title='captcha challenge']")
        return True
    except:
        return False

def _is_captcha_detected_by_keywords(driver) -> bool:
    for i in ['unusual activity', 'detected', 'captcha', 'robot']:
        if i in driver.page_source:
            return True
    return False


def is_captcha_detected(driver) -> bool:
    return _is_recaptcha_detected(driver) or _is_captcha_detected(driver) or _is_captcha_detected_by_keywords(driver)

def captcha_solver(driver, reserve_url: str) -> UndetectableChromeCoordinatesAware:
    try:
        need_to_resolve_captcha_or_to_reload_driver = is_captcha_detected(driver)
    except:
        need_to_resolve_captcha_or_to_reload_driver = True
    if need_to_resolve_captcha_or_to_reload_driver:
        try:
            url = driver.current_url
        except:
            url = reserve_url
        driver=recreate_chromedriver(driver, change_images_visibility=True, disable_images=False)
        if url:
            driver.get(url)
        input('solve captcha and then press enter')
        random_sleep()
        url = driver.current_url
        driver=recreate_chromedriver(driver, change_images_visibility=True, disable_images=True)
        driver.get(url)
        random_sleep()
    return driver

def update_messages_in_gui(gui_window, messages, max_messages_count, new_message):
    '''
    Depreciated. There is a problem with Threads and tkinter.
    '''
    if False:
        new_message = tk.Label(gui_window, text=new_message)
        messages.append(new_message)
        for msg in enumerate(messages[-max_messages_count:]):
            msg[1].grid(row=msg[0], column=0)
        gui_window.update()