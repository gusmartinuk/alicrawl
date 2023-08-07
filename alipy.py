from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas
import json, re
import time
from config import *

driver = None



def setup():
	# Set up the Selenium headless web driver (browser)
	print('Setting up headless browser...')
	options = Options()
	# pencere on off asagida
	options.headless = True
	#options.headless = False
	options.add_argument("--log-level=3")  # Set logging level to suppress certificate error messages
	# farkli calisiyor bazen test icin user agent set ediyoruz! 08/06/2023 22:41
	# asagidaki ayarlardan sonra headless true iken de ayni calisiyor
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

	print(f'Scraping {product_url}...')
	
	driver.delete_all_cookies()

	driver.get(product_url)

	# Wait for the page to load the necessary element
	wait = WebDriverWait(driver, 10)
	wait.until(EC.presence_of_element_located((By.XPATH, '//script[contains(text(),"window.runParams")]')))
	try:
		button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-accept')]")))
		button.click()
	except:
		pass 

	wait = WebDriverWait(driver, 10)	
	try:
		element = driver.find_element_by_class_name("download_header_close")
		element.click()
	except:
		pass	
	wait = WebDriverWait(driver, 10)	
	
	try:
		element = driver.find_element_by_class_name("Sk1_X _1-SOk")
		element.click()
	except:
		pass	
	wait = WebDriverWait(driver, 10)	

	#time.sleep(60)

	#random_file_name=product_url.split("/item/")[1].split(".html")[0]
	
	#html_content = driver.page_source
	#with open(random_file_name+'.html', 'w', encoding='utf-8') as f:
	#	f.write(html_content)	
	# We use a convenient json object with all the info about the product inside of `window.runParams` variable. This variable is inaccessible from our DOM but the definition of it is inside some `script` tag
	data_text = driver.find_element(By.XPATH, '//script[contains(text(),"window.runParams")]').get_attribute('innerHTML').strip()
	#with open(random_file_name+'.txt', 'w', encoding='utf-8') as f:
	#	f.write(data_text)

	data_match = re.search('data: ({.+?}),\n', data_text)

	if not data_match:
		raise ValueError(f'Failed to parse product data from {product_url}. Are you on a product page?')
	

	data = json.loads(data_match.group(1))	
	shipops=''	

	try:				
		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "product-description")))  
		#element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='product-description' and contains(@class, 'product-description')]")))
		description_html = element.get_attribute("innerHTML")
		print("description Ok. Len=",len(description_html))
	except:
		#html_content = driver.page_source
		#with open(str(data['actionModule']['productId'])+'.html', 'w', encoding='utf-8') as f:
		#	f.write(html_content)	
		#exit()
		description_html=""
		#driver.refresh()  
		#time.sleep(5)
	try:
		button = driver.find_element(By.XPATH, "//button/span[contains(text(), 'More options')]")
		button.click()
		try:			
			button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'comet-btn comet-btn-text _3djqy')]")))
			button.click()
		except:
			pass
	except:
		pass
		#html_content = driver.page_source
		#with open(str(data['actionModule']['productId'])+'_kargo_ops_sorunu.html', 'w', encoding='utf-8') as f:
			#f.write(html_content)	

	wait = WebDriverWait(driver, 20)  # wait for up to 10 seconds
	try:
		modal_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.comet-modal')))
		# get the HTML code of the modal
		shipops = modal_element.get_attribute('outerHTML')		
	except:
		pass  	

	if description_html=='':
		#print("DESC Module=",data["descriptionModule"])
		try:			
			driver.get(data["descriptionModule"]["descriptionUrl"])
			wait = WebDriverWait(driver, 20)  # wait for up to 20 seconds
			description_html=driver.page_source
		except Exception as e:
			print("ERROR: Description download!")
			print("Error details:", str(e))		
	product = {
		'title': data['titleModule']['subject'],
		'itemId': int(data['actionModule']['productId']),			
		'data': str(data_match.group(1)),
		'description': description_html,
		'shipOps': shipops
	}
	return product