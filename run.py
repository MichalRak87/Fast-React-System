"""
FastReactSystem

This module contains a class, FastReactSystem, which implements a system to process and
send reports based on screenshots taken from a website.
The processing includes checking if there are any reports
on the website, reading the report text using optical character recognition (OCR),
and storing the report text in a file. The file is then sent to an FTP server.

The class uses the following external packages:
- re
- ftplib
- os
- time
- pyautogui
- pytesseract
- credentials(optional)

It has the following methods:
- get_screenshot
Takes a screenshot of the website and returns the image.
- check_and_click_if_buttons
Check if buttons with the specified image are present on the website and clicks on them if they are.
- check_report
Check for reports on the website and sets the name of the report file if found.
- write_report_in_to_file
Reads the text from the screenshot of the report using OCR and writes the text to a file.
- send_to_ftp
Sends the report file to an FTP server.
- play
The main process of the system. It calls the above methods to process and send the report.

If the script is run as the main program, an instance of the FastReactSystem is created,
 a website is opened and brought to the foreground, and the play method is called three times.
"""
import re
import sys
from ftplib import FTP
from ftplib import error_perm
from os import walk, path
from time import sleep

import keyboard
import pyautogui
import pytesseract
from selenium import webdriver
from selenium.common import exceptions

from credentials import credentials

# FTP login credentials
HOST = credentials["HOST"]
USERNAME = credentials["USERNAME"]
PASSWORD = credentials["PASSWORD"]

# Pattern to match the report text
PATTERN = re.compile(r"\w{3}\s\w{3}\s\d{2}\s\d{4}\s\d{2}:\d{2}:\d{2}$")
# Set the tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"D:\Programy\Tesseract\tesseract.exe"


class FastReactSystem:
    """
    Class to interact with the game and create reports
    """

    def __init__(
        self,
        screenshot_file_name,
    ):
        """
        Initializes the FastReactSystem class
        :param screenshot_file_name: str: The name of the screenshot file
        """
        self.screenshot_file_name = screenshot_file_name
        self.penguin_file_name = None

    def get_screenshot(self):
        """
        Takes a screenshot using PyAutoGUI

        :return: Image object: Image object of the screenshot
        """
        return pyautogui.screenshot(self.screenshot_file_name)

    @staticmethod
    def check_and_click_if_buttons(button_img):
        """
        Check if the button image is present on the screen and click it if found

        :param button_img: str: The path of the button image to look for
        :return: bool: True if the button is found and clicked, False otherwise
        """
        action_buttons = (
            pyautogui.click(pyautogui.center(button))
            for button in pyautogui.locateAllOnScreen(button_img, confidence=0.6)
        )
        try:
            next(action_buttons)
            return True
        except StopIteration:
            return False

    def check_report(self, penguins_folder):
        """
        Check for the report image in the given folder

        :param penguins_folder: str: The path of the folder to search for report images
        :return: str: The name of the report image if found, None otherwise
        """
        source = path.join("web", "img", penguins_folder)
        for *_, file_names in walk(source):
            for file in file_names:
                if pyautogui.locateOnScreen(path.join(source, file), confidence=0.6) is not None:
                    self.penguin_file_name = file
        return self.penguin_file_name

    def write_report_in_to_file(self, reports_filename):
        """
        Writes the extracted text from the penguin screenshot to the specified report file.
        :param reports_filename: the name of the report file to write to
        """
        with open(reports_filename, "a", encoding="utf-8") as file:
            img_text = pytesseract.image_to_string(self.get_screenshot()).split("\n")
            for text in img_text:
                if PATTERN.search(text):
                    print(text)
                    file.write(f'Raport od: {self.penguin_file_name.removesuffix(".png")}\n')
                    file.write(str(text + "\n"))

    @staticmethod
    def send_to_ftp():
        """
        This method connects to an FTP server using the given
         host, username, and password,
        and then uploads the file 'penguins_report.txt' to the directory
         'pycamp' on the FTP server.
        """
        with FTP(HOST, user=USERNAME, passwd=PASSWORD) as ftp, open(
            "penguins_report.txt", "rb"
        ) as file:
            ftp.cwd("pycamp")
            ftp.storbinary("STOR penguins_report.txt", file)

    def play(self):
        """
        Play game by checking and clicking buttons and write report to file
        """
        sleep(0.1)
        self.check_and_click_if_buttons("buttons\\zamknij_zgloszenie.png")
        if self.check_and_click_if_buttons("buttons\\sprawdz.png"):
            sleep(0.1)
        if self.check_report("penguins_check") not in (None, "no_report.png"):
            print(f"Raport z pliku: {self.penguin_file_name}")
            self.write_report_in_to_file("penguins_report.txt")
            self.check_and_click_if_buttons("buttons\\zamknij_zgloszenie.png")
            print("Wysylam raport...")
        else:
            print(f"Raport z pliku: {self.penguin_file_name}")
            print("Fałszywy raport")
            self.check_and_click_if_buttons("buttons\\zamknij_zgloszenie.png")

    @staticmethod
    def run():
        """
        The function checks the number of 'sprawdz.png' buttons present on the screen
          and performs the following actions:
        - If there are more than 0 buttons, the `fast_react_system.play()`
          method is called and a report is sent to the FTP server.
        - If there is an error sending the report to the FTP server,
          a message "FTP server is not running" is printed.
        - If the 'esc' key is pressed, a `NoSuchWindowException` is raised.
        """
        # check the number of 'sprawdz.png' buttons present on the screen
        if len(list(pyautogui.locateAllOnScreen("buttons\\sprawdz.png", confidence=0.7))) > 0:
            fast_react_system.play()
            # send the report to FTP server
            try:
                fast_react_system.send_to_ftp()
            except error_perm:
                print("FTP server is not running")
        if keyboard.is_pressed("esc"):
            raise exceptions.NoSuchWindowException

    @staticmethod
    def open_web_doc(file_path):
        """
        Opens a local HTML file using the Selenium library
        """
        file_path = path.abspath(file_path)
        url = f"file://{file_path}"
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)
        while not keyboard.is_pressed("esc"):
            if driver.current_url:
                sleep(0.01)
                fast_react_system.run()
            if keyboard.is_pressed("esc"):
                raise exceptions.NoSuchWindowException
        driver.close()


if __name__ == "__main__":
    # create instance of FastReactSystem class and pass the screenshot file name
    fast_react_system = FastReactSystem("screenshot.png")
    try:
        # open local HTML file
        fast_react_system.open_web_doc(path.join("web", "strona.html"))
    except exceptions.NoSuchWindowException:
        sys.exit()
