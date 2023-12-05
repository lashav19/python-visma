from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functools import cache
from bs4 import BeautifulSoup
import time
import os



class Visma:
    """
    A method to scrape Visma.
    Usage: 
    visma = Visma()
    Visma.Username = username 
    Visma.Password = password

    dump = Visma.scrape()

    """
    Username: str
    Password: str

    def __init__(self, *args: str) -> None:
        
        """
        param --headless:  getting json data
        param start-maximized: Initializing the headless
        Put these as empty to see what is going on for testing purposes  
        """

        __chrome_driver_path = ChromeDriverManager().install()
        self.service = Service(__chrome_driver_path)
        self.options = Options()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.get("https://romsdal-vgs.inschool.visma.no/")



    def __waitUntil(self, byType: By, item: str): #Make the program wait for an element to appear to stop crashing

        wait = WebDriverWait(self.driver, timeout=10)
        wait.until(EC.visibility_of_element_located((byType, item)))

        waited_for = self.driver.find_element(byType, item)

        print(f"Waited for {item}")
        return waited_for


    def scrape(self) -> dict:
        Username = Visma.Username
        Password = Visma.Password

        print("started") #Debug

        # Visit the desired URL
        self.driver.get("https://romsdal-vgs.inschool.visma.no/")

        # Locate the login button by its name and click it
        time.sleep(.5)

        button = self.__waitUntil(By.ID, "onetrust-accept-btn-handler")
        if button: button.click()

        login = self.__waitUntil(By.ID, "login-with-feide-button")
        login.click()

        print("logging in")

        username = self.driver.find_element(By.ID, "username")
        username.send_keys(Username)

        password = self.driver.find_element(By.ID, "password")
        password.send_keys(Password)

        self.driver.find_element(By.CLASS_NAME, "button-primary").click()
        self.driver.implicitly_wait(2.5)
        print("parsing html")

        Visma.__waitUntil(By.CLASS_NAME, "Timetable-TimetableDays_day")

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Replace with the actual class of the parent div

        parent_div = soup.find('div', class_='active Timetable-TimetableDays_day', recursive=True)

        if not parent_div:
            parent_div = soup.find('div', class_='Timetable-TimetableDays_day', recursive=True)

        if parent_div:
                    
            # Find all <h4> elements within the parent <div>
            h4_tags = parent_div.find_all('h4')

            teacher_item = parent_div.find('div', class_="Timetable-Items", recursive=True)
            teachers = []

            for teacher in teacher_item:
                items=teacher.find("div", {"teachername": True})
                teacher_name = items['teachername']
                teachers.append(teacher_name)
            
            lessons = [h4tag.get_text().split()[0] for h4tag in h4_tags]

            timestart = [h4tag.get_text().split('klokken')[1].split()[0] for h4tag in h4_tags]
            
        self.driver.close()

        return {i:[j,k] for i,j,k in zip(timestart, lessons, teachers)} # i:[j,k] gjør tid til en key i dictionariet


if __name__ == "__main__":
    visma = Visma()

