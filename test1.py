from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas
import json, re
import time

driver = None



def setup():
	# Set up the Selenium headless web driver (browser)
	print('Setting up headless browser...')
	options = Options()	
	#options.headless = True
	options.headless = False
	options.add_argument("--log-level=3")  # Set logging level to suppress certificate error messages
	options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
	options.add_argument('window-size=1051x806')
	options.add_argument("start-maximized")
	options.use_chromium = True	

	global driver
	driver = webdriver.Chrome(options=options,executable_path=r"C:\mypython\aliexpress\chromedriver.exe")	

def cleanup():
	print('Cleaning up...')
	driver.quit()
	print('Done!')

def get_json(product_url):
	assert driver

	#driver.delete_all_cookies()  # farkli sayfa gelislerini onlemek icin deniyoruz!

	driver.set_page_load_timeout(15)
	driver.get(product_url)
	
	element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'currency')]")))
	print("\n currency="+element.text)
	wait = WebDriverWait(driver, 5)	    
	time.sleep(5)  
	try:
		element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'Sk1_X _1-SOk')]")))
		if element:
			element.click()
	except:
		pass

	try:
		button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-accept')]")))
		button.click()
	except:
		pass 

	wait = WebDriverWait(driver, 5)	    
	time.sleep(5)  
	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ship-to')]")))
		if element:
			element.click()
		wait = WebDriverWait(driver, 5)	    
		time.sleep(5)  	
		element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@data-code='us']")))
		if element:
			element.click()
			time.sleep(5)  
			element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ui-button ui-button-primary go-contiune-btn') and @data-role='save']")))
			if element:
					element.click()				
	except:
		pass


	time.sleep(120)
	wait = WebDriverWait(driver, 10)
	wait.until(EC.presence_of_element_located((By.XPATH, '//script[contains(text(),"window.runParams")]')))
    

setup()
url="https://www.aliexpress.com/item/"+str(1005002996364718)+".html"
p = get_json(url)
print(p)
cleanup()
