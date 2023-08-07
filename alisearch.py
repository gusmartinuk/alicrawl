from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *

import pymysql
import pandas
import json, re
import time
from config import *

driver = None

def setup():
	# Set up the Selenium headless web driver (browser)
#	print('Setting up headless browser...')
#	options = Options()
#	#options.headless = True
#	options.headless = False
#	proxy = proxy_host
#	desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
#	desired_capabilities['proxy'] = {
#		"httpProxy": proxy,
#		"ftpProxy": proxy,
#		"sslProxy": proxy,
#		"noProxy": None,
#		"proxyType": "MANUAL",
#		"class": "org.openqa.selenium.Proxy",
#		"autodetect": False
#	}

	# Set up the Selenium headless web driver (browser)
	print('Setting up headless browser...')
	options = Options()
	# pencere on off asagida
	#options.headless = True
	#options.headless = False
	options.add_argument("--log-level=3")  # Set logging level to suppress certificate error messages
	# options.add_argument('--headless')
	options.add_argument('--no-sandbox')	
	options.add_argument('--proxy-server=' + proxy_host)
	options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
	options.add_argument('window-size=1051x806')
	options.add_argument("start-maximized")
	options.use_chromium = True	

	global driver
	#driver = webdriver.Chrome(options=options,executable_path=r"C:\mypython\aliexpress\chromedriver.exe --headless")	
	#driver = webdriver.Chrome(options=options,desired_capabilities=desired_capabilities,executable_path=r"C:\mypython\aliexpress\chromedriver.exe")	
	driver = webdriver.Chrome(options=options,executable_path=r"C:\mypython\aliexpress\chromedriver.exe")		
	driver.get("https://www.iplocation.net/")
	driver.save_screenshot('iplocationnet.png')
	driver.quit()
	exit()



def cleanup():
	print('Cleaning up...')
	driver.quit()
	print('Done!')

def get_json(search_url):
	assert driver

	print(f'Scraping {search_url}...')
	driver.get(search_url)

	# Wait for the page to load the necessary element
	wait = WebDriverWait(driver, 10)

	try:
		button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-accept')]")))
		button.click()
	except:
		print("except 1")

	page=1
	srctxt = "did not match any products. Please try again."   


	while page<100:	
		try:			
			cnt=0
			while cnt<3:
				cnt+=1
				driver.find_element(By.XPATH, f"//span[contains(text(), '{srctxt}')]")
				driver.refresh()				
			break
		except:
			#pass  # The element was not found, do nothing
			anchor_element = driver.find_element(By.XPATH, "//a[@class='manhattan--container--1lP57Ag cards--gallery--2o6yJVt search-card-item']")
			# Find all elements with the same class below the anchor tag
			items = anchor_element.find_elements(By.XPATH, "./following::*[@class='manhattan--container--1lP57Ag cards--gallery--2o6yJVt search-card-item']")

			for item in items:
				url = item.get_attribute("href")  # Extract the target URL
				item_id = url.split('/')[4].split('.')[0]  # Extract the item ID from the URL
				#print("URL:", url)
				print("Item ID:", item_id)
				query="insert ignore into aliexpress_db.crawl set itemId=%s"
				cursor.execute(query,(item_id))
				#result=cursor.fetchall()
			connection.commit()
			page+=1
			print("PAGE=",page)
			time.sleep(3)
			driver.get(search_url+"&page="+str(page))
			wait = WebDriverWait(driver, 10)				
	print("done!")		


cursor = connection.cursor(pymysql.cursors.DictCursor)
#query="select itemId from aliexpress_db.crawl where title is null order by lastcrawled"
#cursor.execute(query)
#result=cursor.fetchall()

keywords="earbuds hook"
url="https://www.aliexpress.com/w/wholesale-"+keywords.replace(" ","-").replace("\\","%5C")+".html?SearchText="+keywords.replace(" ","+")+"&catId=200084017&g=y&sortType=total_tranpro_desc"
setup()
get_json(url)
cleanup()
cursor.close()
connection.close()