# python -m unittest discover -s integration_tests
import subprocess
import time
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_FILE = "main.py"


# class TestStreamlitApp(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         # Démarrer le serveur Streamlit
#         cls.process = subprocess.Popen(
#             ["streamlit", "run", APP_FILE], stdout=subprocess.PIPE
#         )
#         time.sleep(3)  # Attendre que l'application démarre

#         # Initialiser le navigateur
#         options = webdriver.ChromeOptions()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")

#         # Utiliser le gestionnaire de pilotes pour installer le pilote Chrome
#         cls.driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()), options=options
#         )

#     @classmethod
#     def tearDownClass(cls):
#         cls.driver.quit()
#         cls.process.terminate()

#     def test_login_functionality(self):
#         self.driver.get("http://localhost:8501")

#         # Attendre que les éléments soient visibles
#         email_input = WebDriverWait(self.driver, 10).until(
#             EC.visibility_of_element_located((By.XPATH, "//input[@type='text']"))
#         )
#         password_input = WebDriverWait(self.driver, 10).until(
#             EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
#         )
#         login_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable(
#                 (By.XPATH, "//button[contains(text(),'Se connecter')]")
#             )
#         )

#         email_input.send_keys("test@example.com")
#         password_input.send_keys("pwd_example")
#         login_button.click()

#         time.sleep(2)
#         self.assertIn("Bienvenue", self.driver.page_source)


# Pour exécuter les tests
if __name__ == "__main__":
    unittest.main()
