# Aliexpres urun sayfalarini kaydeden modul
# Proxy kullaniyor 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas
import json, re
import time
import pymysql
from selenium.webdriver.common.proxy import *
import requests
#import traceback
#import sys
#import pyperclip
import time
import pymysql
import argparse
from config import *

parser = argparse.ArgumentParser()
parser.add_argument('--offset', type=int, default=0, help='The offset value')
parser.add_argument('--item', type=int, default=0, help='item id for single item')
args = parser.parse_args()
offset = args.offset
singleitem=args.item

# debug
singleitem=1005001571702454; 

cursor = connection.cursor(pymysql.cursors.DictCursor)

driver = None
log=''
logline=0
currentip=''
proxy_host=''

def addlog(txt):
	global log,logline
	if log=='':
		logline=0
	logline+=1   
	print(str(logline),"***",txt,"***")
	log+=txt


# requests.get("https://ipv4.webshare.io/"))  get current ip

def getcurrentip():
	global proxy_host,currentip,log
	proxies = {
   		'http': proxy_host,
   		'https': proxy_host,
	}
	response=requests.get("https://ipv4.webshare.io/", proxies=proxies)
	currentip=response.text
	addlog("\n currentIP="+currentip)

def getproxy():
	global proxy_host,currentip
	query="SELECT proxurl FROM aliexpress_db.proxies where proxstatus=1 ORDER BY RAND() LIMIT 1"
	cursor.execute(query)
	result=cursor.fetchone()
	if result is not None:
		proxy_host = result['proxurl']
	else:
		proxy_host = None
	getcurrentip()  # proxy get ip
 
def countproxy():
	global proxy_host,currentip
	query="update aliexpress_db.proxies set proxcallcount=proxcallcount+1 where proxurl=%s"
	cursor.execute(query,(proxy_host))
	connection.commit()

def proxycountry(code):
	global proxy_host,currentip
	query="update aliexpress_db.proxies set proxlastcountry=%s where proxurl=%s"
	cursor.execute(query,(code,proxy_host))
	connection.commit()


def setup():
	global log,proxy_host,driver,currentip
	# proxy webshare.io  
	print('Setting up headless browser...')
	# debug icin getproxy()
	options = Options()
	options.add_argument("--log-level=3")  # Set logging level to suppress certificate error messages
	# debug icin options.add_argument('--headless')
	options.add_argument('--no-sandbox')	
	# debug icin options.add_argument('--proxy-server=' + proxy_host)
	options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
	options.add_argument('window-size=1051x806')
	options.add_argument("start-maximized")
	options.use_chromium = True

	# for windows driver = webdriver.Chrome(options=options,executable_path=r"C:\mypython\aliexpress\chromedriver.exe")		
	driver = webdriver.Chrome(options=options)		
	
	#driver.get("https://www.iplocation.net/")   # check ip 
	#driver.save_screenshot('iplocationnet.png')
	#driver.quit()
	#exit()


def cleanup():
	global log
	print('Cleaning up...')
	driver.quit()
	print('Done!')

def clicknotif():
	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'Sk1_X _1-SOk')]")))
		if element:
			print("Don't allow notification popped") 
			element.click()
	except:
		pass
	time.sleep(2)
	try:
		button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-accept')]")))
		button.click()
	except:
		pass 



def setcountry(code):
	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ship-to')]")))
		if element:
			print("ship to clicked") 
			element.click()
		wait = WebDriverWait(driver, 5)	    
		time.sleep(5)  
		try:
			element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'address-select-trigger')]")))
			if element:
				print("address select clicked") 
				element.click()
				try:
					time.sleep(2)  
					element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'filter-input')]")))
					if element:
						print("country name") 
						#element.click()
						#element.send_keys("United States\n")	
						time.sleep(2)  
						#element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@data-name='United States']")))
						element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@data-code='"+code+"']")))
						if element:
							print("country found and clicked") 
							element.click()
							time.sleep(2)  
							element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ui-button ui-button-primary go-contiune-btn') and @data-role='save']")))
							if element:
									print("save found and clicked") 
									element.click()				
				except:
					pass   
		except:
			pass   
	except:
		pass

def getcountry():    
	currency=''
	cocode='' 
	try:
		element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'currency')]")))
		currency=element.text
	except:
		pass
	try:
		element = driver.find_element(By.XPATH, "//input[@id='userCountryCode']")
		cocode = element.get_attribute("value")
	except:
		pass
	return (cocode,currency)





def get_json(product_url,strItemId):
	assert driver

	addlog("\n URL="+product_url)
	#driver.delete_all_cookies()  # farkli sayfa gelislerini onlemek icin deniyoruz!

	driver.set_page_load_timeout(25)
	driver.get(product_url)
	countproxy()

	cocode,cocur=getcountry()
	print("country=",cocode)
	print("currency=",cocur)
	wait = WebDriverWait(driver, 5)	    
	proxycountry(cocode)
	if cocode!="UK":
		addlog("\n 0) Country changed to UK = old="+cocode)
		time.sleep(2)  
		clicknotif()
		time.sleep(2)  
		setcountry("uk")	  
		wait = WebDriverWait(driver, 10)
		time.sleep(2)  
		clicknotif()

	srctxt='Sorry, the page you requested can not be found:('
	try:
		elements=driver.find_element(By.XPATH, f"//span[contains(text(), '{srctxt}')]")  
		if elements:
			print("\n SAYFA YOK. Noscan Set edildi: ",strItemId)
			# page not found, wrong item vs.
			query = "update crawl SET noscan=1, lastcrawled=CURRENT_TIMESTAMP where itemId=%s"
			cursor.execute(query, (strItemId))
			connection.commit()
			return(None)
	except:
		pass
		
	addlog("\n 1) OK Url Downloaded")
	# Wait for the page to load the necessary element
	wait = WebDriverWait(driver, 10)
	#driver.save_screenshot(strItemId+'_1.png')	
	element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//script[contains(text(),"window.runParams")]')))

	try:
		button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-accept')]")))
		if button:
			button.click()
			addlog("\n 2) OK Cookies accept clicked")
	except:
		pass
	wait = WebDriverWait(driver, 10)
	#driver.save_screenshot(strItemId+'_2.png')
	# barkodlu download ekrani geldiyse
	try:
		element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'download_header_close')]")))
		element.click()
	except:
		pass
	wait = WebDriverWait(driver, 10)	
	try:
		element = driver.find_element(By.XPATH, "//*[contains(@class, 'Sk1_X _1-SOk')]")
		element.click()
	except:
		pass
	wait = WebDriverWait(driver, 10)	

	data_text = driver.find_element(By.XPATH, '//script[contains(text(),"window.runParams")]').get_attribute('innerHTML').strip()	

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
		print("Sayfa ici Description yok!")
		#driver.refresh()  
		#time.sleep(5)
	# product-sku div for all variations
	skurows={}		
	skutitles={}
	try:				
		skusdiv=driver.find_element(By.XPATH, "//div[contains(@class, 'product-sku')]")
		print("skusdiv found")
		sku_properties = skusdiv.find_elements(By.CLASS_NAME, 'sku-property')
		cntx=0
		for sku_property in sku_properties:
			cntx+=1
			sku_title = sku_property.find_element(By.CLASS_NAME, 'sku-title').text
			print("sku_title:",sku_title)
			sku_property_list = sku_property.find_element(By.CLASS_NAME, 'sku-property-list')
			clickable_links = sku_property_list.find_elements(By.TAG_NAME, 'li')
			skurows[cntx]=clickable_links
			skutitles[cntx]=sku_title
			#print('SKU Title:', sku_title)
			#print('Clickable Links:')
			#for link in clickable_links:
			#	img=link.find_element(By.TAG_NAME, 'img')
			#	print(img.get_attribute('alt'))
			#	img.click()
			#	wait = WebDriverWait(driver, 2)
	except:
		pass
	wait = WebDriverWait(driver, 30)	
	#print(skurows)
	print("total row count=",len(skurows))
	cntx=0
 
	for indis, srow in skurows.items():  # Fixed: Added ".items()" to iterate over dictionary items
		cntx += 1
		print("indis =", indis, "--", cntx, ". total sku count =", len(srow), "title:", skutitles[indis])
		cnty=0
		for option in srow:
			cnty+=1			
			try:
				option.click()  
				print("clicked=", cntx,cnty)
				wait = WebDriverWait(driver, 2)
			except Exception as e:
				print("Error=", cntx,cnty," : ",str(e))
			time.sleep(5)	
	cleanup()
	exit()
	
	try:
		button = driver.find_element(By.XPATH, "//button/span[contains(text(), 'More options')]")
		button.click()
		try:
			#view more ic ekranda
			button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'comet-btn comet-btn-text _3djqy')]")))
			button.click()
		except:
			print("Shipping View More doesn't exist!")   
	except:
		print("Shipping View More doesn't exist!")   
		#html_content = driver.page_source
		#with open(str(data['actionModule']['productId'])+'_kargo_ops_sorunu.html', 'w', encoding='utf-8') as f:
			#f.write(html_content)	

	wait = WebDriverWait(driver, 20)  # wait for up to 10 seconds

	try:
		modal_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.comet-modal')))
		# get the HTML code of the modal
		shipops = modal_element.get_attribute('outerHTML')		
	except:
		print("Shipping window not opened ")    	

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


def measure_execution_time(func):
	def wrapper(*args, **kwargs):
		start_time = time.time()
		result = func(*args, **kwargs)
		end_time = time.time()
		execution_time = end_time - start_time
		print(f"Execution time of {func.__name__}: {execution_time} seconds")
		return result
	return wrapper

if singleitem==0:
	# TODO: dikkat urun yuklemesi yapilirsa, 7 gun yerine gunluk update dusunelim
	query="select itemId from aliexpress_db.crawl where ifnull(title,'')='' and noscan=0 and trycount<5 and date_add(lastcrawled,interval 7 day)<current_timestamp order by lastcrawled limit %s,15"
	cursor.execute(query,(offset))
	result=cursor.fetchall()
else:
	result=[{'itemId':singleitem}]
 
for row in result:
	setup()
	start_time = time.time()
	url="https://www.aliexpress.com/item/"+str(row['itemId'])+".html"
	tries = 0
	p=None
	## p = alipy.get_json(url) not repetitive
	while tries < 1:  # loop once
		query="update aliexpress_db.crawl set trycount=trycount+1, lastcrawled=CURRENT_TIMESTAMP  where itemId=%s"
		cursor.execute(query,(row['itemId']))
		connection.commit()
		try:
			print("OFFSET=",offset,"   itemid=",row['itemId'])
			p = get_json(url,str(row['itemId']))
		except Exception as e:
			print(type(e).__name__, e)			
			print('Retrying...')
			query="update aliexpress_db.crawl set lasterror=%s, lastcrawled=CURRENT_TIMESTAMP where itemId=%s"
			cursor.execute(query,(str(e),row['itemId']))
			connection.commit()
		else:
			break
		tries += 1
		time.sleep(2)
	if not p is None:
		query = "INSERT INTO crawl SET itemId=%s, title=%s, description=%s, data=%s, shipops=%s, lastcrawled=CURRENT_TIMESTAMP "
		query += "ON DUPLICATE KEY UPDATE title=VALUES(title), description=VALUES(description), data=VALUES(data), shipops=VALUES(shipops), lastcrawled=CURRENT_TIMESTAMP"
		cursor.execute(query, (p['itemId'], p['title'], p['description'], p['data'], p['shipOps']))
		connection.commit()
	time.sleep(1)	# 1 sec wait between pages
	end_time = time.time()
	# speed check
	execution_time = end_time - start_time
	query="update crawl set lastexecsecs=%s, lastcrawled=CURRENT_TIMESTAMP where itemId=%s"
	cursor.execute(query, (str(execution_time), row['itemId']))
	connection.commit()	
	cleanup()

cursor.close()
connection.close()
print("processed records:", result)
