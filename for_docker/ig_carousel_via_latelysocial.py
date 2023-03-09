import time

from PIL import Image, ImageFont, ImageDraw
import textwrap

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import requests
import os
from PIL import Image
from io import BytesIO

import credentials

def text_to_image(base_image, text_to_add, save_location, save_name):

    BASE_IMAGE = Image.open(base_image)
    TEXT_TO_ADD = text_to_add
    FONT_TO_USE = 'Uchen-Regular.ttf' # path to .ttf file
    IMG_MARGIN_TOP = 300
    IMG_MARGIN_BOTTOM = 120
    MAX_FONT_SIZE = 150
    initial_row_length = 17
    image_editable = ImageDraw.Draw(BASE_IMAGE)

    # Find char length of longest row
    def get_longest_str(lst):
        # Testing length using given font and font size 20
        font_for_test = ImageFont.truetype(FONT_TO_USE, 20)
        
        return max(enumerate(lst), key=lambda x: font_for_test.getsize(x[1])[0])

    # Determine font size for which given text fits to width
    def max_font_for_x(word_list):

        fontsize = 1  # starting font size
        img_fraction = 0.8 # portion of image width you want text width to be
        font = ImageFont.truetype(FONT_TO_USE, fontsize)
        
        # Get longest string in given list to use for calculation
        longest_string = get_longest_str(word_list)[1]
        
        while font.getsize(longest_string)[0] < img_fraction*BASE_IMAGE.size[0] and fontsize <= MAX_FONT_SIZE:
            # iterate until the text size is just larger than the criteria
            fontsize += 1
            font = ImageFont.truetype(FONT_TO_USE, fontsize)
        
        # reduce font size by one to ensure it is below max
        fontsize -= 1
        font = ImageFont.truetype(FONT_TO_USE, fontsize)

        return font

    def calc_text_height(word_list, font):
        first_row_height = font.getsize(word_list[0])[1]
        return first_row_height * len(word_list)

    # Get correct coordinates for positioning text in x-axis middle
    def get_x_coordinate(image, text, font):
        img_width = image.size[0]
        text_width = font.getsize(text)[0]
        return (img_width-text_width)/2

    # Get correct coordinates for positioning text in y-axis middle
    def get_y_coordinate(image, text_height, row, total_rows):
        img_height = image.size[1]
        target_center = IMG_MARGIN_TOP + ((img_height - IMG_MARGIN_TOP - IMG_MARGIN_BOTTOM)/2)
        y_coordinate = target_center + ( text_height * ( row - (total_rows / 2) ) )
        return y_coordinate

    def text_wrap_to_spec(max_row_chars, text):
        wrapper = textwrap.TextWrapper(width = max_row_chars)
        return wrapper.wrap(text = text)

    # Find optimal text size. Start with max row lenght of 25 characters and maximize font.
    # If text block is too high, increase max row length (and thus decrease font size).
    if text_to_add == "":
        return base_image
    
    max_text_height = BASE_IMAGE.size[0] - IMG_MARGIN_TOP - IMG_MARGIN_BOTTOM
    text_ready = False
    while text_ready == False:
        # Perform text wrap to specified character length
        word_list = text_wrap_to_spec(initial_row_length, TEXT_TO_ADD)
        # Find optimal font size
        text_font = max_font_for_x(word_list)
        if calc_text_height(word_list, text_font) > max_text_height:
            initial_row_length += 1
        else:
            text_ready = True
        
    # Add text to image
    font_height = text_font.getsize(word_list[0])[1]
    i = 0
    for element in word_list:
        x_coordinate = get_x_coordinate(BASE_IMAGE, element, text_font)
        y_coordinate = get_y_coordinate(BASE_IMAGE, font_height, i, len(word_list))
        image_editable.text((x_coordinate, y_coordinate), word_list[i], (255, 255, 255), font=text_font)
        i += 1

    BASE_IMAGE.save(save_location + "./" + save_name + ".jpg")
    # print("Image created: " + save_name + ".jpg")
    return save_location + "./" + save_name + ".jpg"



def post_to_ig(image_content_to_post, caption_to_post):

    base_image_path = "./base_images/" + image_content_to_post[0] + ".jpg"
    question = image_content_to_post[1]
    answer = image_content_to_post[2]
    caption = caption_to_post

    LS_EMAIL = credentials.LS_EMAIL
    LS_PASSWORD = credentials.LS_PASSWORD

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage") # Added for docker case
    options.add_argument("--no-sandbox") # Added for docker case
    
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get("https://latelysocial.com/auth/login")
    print("--- Starting ig post script, logging in.")


    # Enter account details
    driver.find_element(By.NAME, "email").click()
    driver.find_element(By.NAME, "email").send_keys(LS_EMAIL)
    driver.find_element(By.NAME, "password").click()
    driver.find_element(By.NAME, "password").send_keys(LS_PASSWORD)
        
    # Press login button
    driver.find_element(By.CSS_SELECTOR, ".btn").click()
    time.sleep(15)

    print("--- Entering post info.")
    driver.get("https://latelysocial.com/instagram/post")
    time.sleep(15)

    # Select ig account
    driver.find_element(By.CSS_SELECTOR, ".mr15:nth-child(2) > .p0").click()
        
    # Select carousel post
    driver.find_element(By.LINK_TEXT, "Carousel").click()
        
    # Add caption text
    driver.find_element(By.CSS_SELECTOR, ".caption-editor > .emojionearea-editor").click()
    element = driver.find_element(By.CSS_SELECTOR, ".caption-editor > .emojionearea-editor")
    caption_argument = "if(arguments[0].contentEditable === 'true') {arguments[0].innerText = '" + caption + "'}"
    driver.execute_script(caption_argument, element) # Set to variable
    
    print("--- Uploading images.")
    # Upload images. Images must be added in correct order.

    # Create question and answer images and retrieve paths
    post_img_location_q = text_to_image(base_image = base_image_path, text_to_add = question, save_location = "", save_name = "Q")
    post_img_location_a = text_to_image(base_image = base_image_path, text_to_add = answer, save_location = "", save_name = "A")

    # Upload question and remove temporary file
    # driver.find_element(By.ID, "fileupload").send_keys(os.path(post_img_location_q))
    driver.find_element(By.ID, "fileupload").send_keys(os.path.abspath(post_img_location_q))
    time.sleep(15)
    os.remove(post_img_location_q)

    # Upload answer and remove temporary file
    driver.find_element(By.ID, "fileupload").send_keys(os.path.abspath(post_img_location_a))
    time.sleep(15)
    os.remove(post_img_location_a)

    # Upload img3
    driver.find_element(By.ID, "fileupload").send_keys(os.path.abspath("./base_images/img3.jpg"))
    time.sleep(15)

   
    print("--- Posting...")
    # Publish post
    driver.find_element(By.CSS_SELECTOR, ".btnGoNow").click()
    time.sleep(60)

    # DELETE IMAGES FROM FILE MANAGER
    print("--- Deleting images from file manager.")
    driver.get("https://latelysocial.com/file_manager")
    time.sleep(15)

    driver.find_element(By.XPATH, "//span[contains(.,\'Select all\')]").click()
    driver.find_element(By.CSS_SELECTOR, ".conf_delete_multi_files > span").click()
    time.sleep(15)

    driver.find_element(By.CSS_SELECTOR, ".btn-danger > span").click()
    time.sleep(15)


    # Log out
    print("--- Logging out.")
    driver.find_element(By.LINK_TEXT, "Triviadeck").click()
    driver.find_element(By.LINK_TEXT, "Logout").click()
        
    # Close window
    driver.close()
    print("--- post_to_ig() done!")

