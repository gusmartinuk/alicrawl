from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas
import json, re
import json5
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
from bs4 import BeautifulSoup
import pandas as pd
from pandas.tseries.offsets import BDay
from config import *


parser = argparse.ArgumentParser()
parser.add_argument('--offset', type=int, default=0, help='The offset value')
parser.add_argument('--item', type=int, default=0, help='item id for single item')
args = parser.parse_args()
offset = args.offset
singleitem=args.item

# debug
singleitem=1005001571702454 
#singleitem=1005003723875963  plug type ornegi color yerine

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

def busdays(ld, estdate):
    lastdate = pd.to_datetime(ld)
    year = lastdate.year
    estdate_full = pd.to_datetime(f"{estdate} {year}")
    if estdate_full <= lastdate:
        estdate_full = estdate_full + pd.DateOffset(years=1)
    business_days = pd.bdate_range(lastdate, estdate_full)
    business_days_count = len(business_days) - 1  # -1 because the end date is exclusive
    return(business_days_count)

def save_text_to_file(text, filename, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as file:
        file.write(text)
    print(f"Text saved to '{filename}' successfully.")

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
	getcurrentip()  # proxy araciligiyla ip aldik

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
	#options.add_argument('window-size=400x800')	
	options.add_argument('window-size=1051x806')	
	#options.add_argument("start-maximized")
	options.use_chromium = True

	# mobile_emulation = {
    # 	"deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    #	"userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
	# }
	# options.add_experimental_option("mobileEmulation", mobile_emulation)
 

	#driver = webdriver.Chrome(options=options,executable_path=r"C:\mypython\aliexpress\chromedriver.exe")		
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
			element.click()
		wait = WebDriverWait(driver, 5)	    
		time.sleep(5)  
		try:
			element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'address-select-trigger')]")))
			if element:
				element.click()
				try:
					time.sleep(2)  
					element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'filter-input')]")))
					if element:
						#element.click()
						#element.send_keys("United States\n")	
						time.sleep(2)  
						#element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@data-name='United States']")))
						element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@data-code='"+code+"']")))
						if element:
							element.click()
							time.sleep(2)  
							element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ui-button ui-button-primary go-contiune-btn') and @data-role='save']")))
							if element:
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

def shipping_options(shipops,strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3):
    
    soup = BeautifulSoup(shipops, 'html.parser')
    shipping_methods = soup.find_all('div', class_='_3yzHC')

    #print("<table>")
    #for method in shipping_methods:
    #    title = method.find('div', class_='dynamic-shipping-line dynamic-shipping-titleLayout').get_text(strip=True)        
    #    print("<tr><td>",title,"</td>")
    #    content_layouts = method.find_all('div', class_='dynamic-shipping-line dynamic-shipping-contentLayout')        
    #    for content in content_layouts:
    #        print("<td>",content.get_text(strip=False),"</td>")
    #    print("</tr>")    
    #print("</table>")

    #shipflag=2 under processing
    query="update alishipping set shipFlag=2 where shipProId=%s"
    sdata = ( strItemId )
    cursor.execute(query,sdata)
    connection.commit()     

    ships={}
    for option in shipping_methods:
        #print("<hr><hr><pre>",option.prettify().replace("<","&lt;").replace(">","&gt;").replace("\n","<br>"),"</pre>")        
        xfreeship=""
        xfreeshipover=""
        xestdelivery=""
        xshippingcost=""
        xtracking=""
        xcourier=""
        findit = option.find('strong', string=lambda text: text and "Free Shipping" in text)
        if findit:
            xfreeship=findit.get_text(strip=True)  
        else:
           findit = option.find('strong', string=lambda text: text and "Free shipping" in text)          
           if findit:
               xfreeship=findit.get_text(strip=True)              

        findit = option.find('strong', string=lambda text: text and "Shipping:" in text)
        if findit:
            xshippingcost=findit.get_text(strip=True)       

        findit = option.find('span', string=lambda text: text and "Tracking Unavailable" in text)
        if findit:
            xtracking=False

        findit = option.find('span', string=lambda text: text and "Tracking Available" in text)
        if findit:
            xtracking=True
        
        findit = option.find('span', string=lambda text: text and "via" in text)
        if findit:
            xcourier=findit.get_text(strip=True).replace('via ','')
                  
        
        content_layouts = option.find_all('div', class_='dynamic-shipping-line dynamic-shipping-contentLayout')        
        for method in content_layouts:
            xmethod=method.get_text(strip=True)            
            print("<br>====",xmethod,"====")
            if  "Free shipping for orders over" in xmethod:
                xfreeshipover=xmethod            
            elif  "Estimated delivery on" in xmethod or "delivery by" in xmethod:   
                 xestdelivery=xmethod.replace("Estimated delivery on","").replace("delivery by","")           

        
        xcalcdays=busdays(row['lastcrawled'],xestdelivery)
        print("<br>xfreeship=",xfreeship)            
        print("<br>xfreeshipover=",xfreeshipover)    
        print("<br>xestdelivery=",xestdelivery)    
        print("<br>xshippingcost=",xshippingcost)    
        print("<br>xtracking=",xtracking)    
        print("<br>xcourier=",xcourier)    
        print("<br>calculated_delivery: ",xcalcdays)
        print("<hr>")
        xcurrency=""
        if "￡" in xshippingcost or "￡" in xfreeshipover:
            xcurrency="GBP"
        elif "$" in xshippingcost or "$" in xfreeshipover:
            xcurrency="USD"    
        xshipcost=0
        if "Free Shipping" in xfreeship:
            xshipcost=0
        elif "Shipping" in xshippingcost:
            match = re.search(r'(\d+\.\d+)', xshippingcost)
            if match:
                xshipcost = match.group(1)
        
        xshipover=0
        # "Free shipping for orders over ￡4.14"
        if "Free shipping for orders over" in xfreeshipover:
            match = re.search(r'(\d+\.\d+)', xfreeshipover)
            if match:
                xshipover = match.group(1)

        query="""
            INSERT INTO alishipping (
                shipProId, shipName, shipCurrency, shipCost, shipFreeOver,
                shipTracking, shipBusinessDay, shipFlag
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                shipProId=VALUES(shipProId), shipName=VALUES(shipName),
                shipCurrency=VALUES(shipCurrency), shipCost=VALUES(shipCost),
                shipFreeOver=VALUES(shipFreeOver), shipTracking=VALUES(shipTracking),
                shipBusinessDay=VALUES(shipBusinessDay), shipFlag=VALUES(shipFlag)
            """        
        sdata = ( strItemId, xcourier, xcurrency, str(xshipcost),
                xshipover, "Yes" if xtracking else "No", str(xcalcdays),'0' )

        #print("sdata: ", sdata)
        #print("query: ", query)
        cursor.execute(query, sdata)
        connection.commit()     


def get_shipping(strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3):
	try:
		#button = driver.find_element(By.XPATH, "//button/span[contains(text(), 'More options')]")
		button = driver.find_element(By.CLASS_NAME, 'product-dynamic-shipping-moreOptions')
		button.click()
		try:
			#view more ic ekranda
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
		shipping_options(shipops,strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3)
	except:
		pass
	# burada alicompile kismindaki shipping ayiklayan fonksiyonu cagiralim.
	# bu versiyon compile isini de cozsun tamamen aslinda
	

def get_skutitle(skux):
	img_src = ''
	img_title=''
	try:
		img_element = skux.find_element(By.TAG_NAME, 'img')
		img_src = img_element.get_attribute('src')
		img_title = img_element.get_attribute('title')
	except:
		pass
	if img_title=='': 
		try:
			img_element = skux.find_element(By.CLASS_NAME, 'sku-property-text')
			img_title = img_element.text
		except:
			pass
	print("src=",img_src)		
	print("title=",img_title)		
	return(img_title,img_src)		


def get_json(product_url,strItemId):    
	assert driver
	global	img_title1,img_src1,img_title2,img_src2,img_title3,img_src3


	addlog("\n URL="+product_url)
	#driver.delete_all_cookies() 

	driver.set_page_load_timeout(25)
	driver.get(product_url)
	#countproxy()

	"""
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
	"""
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
	#save_text_to_file(data_text, 'data_text.log')
    
	#data_match = re.search('data: ({.+?}),\n', data_text)
	data_match = re.search('window.runParams\s*=\s*({.*?})\s*;', data_text, re.DOTALL)
	#save_text_to_file(str(data_match), 'data_match.log')

	if not data_match:
		raise ValueError(f'Failed to parse product data from {product_url}. Are you on a product page?')

	#data = json.loads(data_match.group(1))	
	data = json5.loads(data_match.group(1))	
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
	# product-sku div tum varyasyonlari tutuyor onun tek tek tiklatip ayiklatmamiz lazim.

	# sku-title hersey olabiliyor, color, size, plug type vs.  bu etiketlere gore YENIDEN DUZENLEYELIM ALTTAKI MANTIGI
	skuline1={}
	skuline2={}
	skuline3={}
	try:				
		skusdiv=driver.find_element(By.XPATH, "//div[contains(@class, 'product-sku')]")
		sku_properties = skusdiv.find_elements(By.CLASS_NAME, 'sku-property')
		cntx=0
		for sku_property in sku_properties:
			cntx+=1			
			sku_title = sku_property.find_element(By.CLASS_NAME, 'sku-title').text
			sku_property_list = sku_property.find_element(By.CLASS_NAME, 'sku-property-list')
			clickable_links = sku_property_list.find_elements(By.TAG_NAME, 'li')
			label=sku_title.split(":")[0].strip()
			if cntx==1:
				skuline1=clickable_links
				skutitle1=label
				print("skutitle1=",skutitle1)
			elif cntx==2:
				skuline2=clickable_links
				skutitle2=label
				print("skutitle2=",skutitle2)
			elif cntx==3:
				skuline3=clickable_links
				skutitle3=label
				print("skutitle3=",skutitle3)    
		maxskulines=cntx
	except:
		pass
	wait = WebDriverWait(driver, 30)	

	if len(skuline1)>0:
		for sku1 in skuline1:
			img_title1,img_src1,img_title2,img_src2,img_title3,img_src3='','','','','',''
			try:
				if sku1.is_enabled():
					sku1.click()
					wait = WebDriverWait(driver, 10)
					img_title1,img_src1=get_skutitle(sku1)	
					print("sku1=",img_title1," ",img_src1)
				#	image-view-magnifier-wrap for images
				#	product-quantity-tip  for stock
					if len(skuline2)>0:
						for sku2 in skuline2:
							img_title2,img_src2,img_title3,img_src3='','','',''
							try:
								if sku2.is_enabled():
									sku2.click()   			
									wait = WebDriverWait(driver, 20)
									img_title2,img_src2=get_skutitle(sku2)	
									print("sku2=",img_title2," ",img_src2)
									if len(skuline3)>0:
										for sku3 in skuline3:
											img_title3,img_src3='',''
											if sku3.is_enabled():
												try:
													sku3.click()   			
													wait = WebDriverWait(driver, 20)
													img_title3,img_src3=get_skutitle(sku3)	
													print("sku3=",img_title3," ",img_src3)
													currentprice=driver.find_element(By.XPATH, "//div[contains(@class, 'product-price-current')]")
													print("price=",currentprice.text)
													get_shipping(strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3)
												except Exception as e: 
													print("skuclick3 Error=",str(e))
								else:
									currentprice=driver.find_element(By.XPATH, "//div[contains(@class, 'product-price-current')]")
									print("price=",currentprice.text)
									get_shipping(strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3)
							except Exception as e: 
								print("skuclick2 Error=",str(e))
				else:
					currentprice=driver.find_element(By.XPATH, "//div[contains(@class, 'product-price-current')]")
					print("price=",currentprice.text)
					get_shipping(strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3)
			except Exception as e: 
				print("skuclick1 Error=",str(e))
	else:
		currentprice=driver.find_element(By.XPATH, "//div[contains(@class, 'product-price-current')]")
		print("price=",currentprice.text)
		get_shipping(strItemId,img_title1,img_src1,img_title2,img_src2,img_title3,img_src3)

	time.sleep(120)
		
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
		print("Kargo penceresi acilmadi! ")    	

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
	query="select itemId from aliexpress_db.crawl where ifnull(title,'')='' and noscan=0 and trycount<5 and date_add(lastcrawled,interval 7 day)<current_timestamp order by lastcrawled limit %s,15"
	cursor.execute(query,(offset))
	result=cursor.fetchall()
else:
	result=[{'itemId':singleitem}]

global img_title1,img_src1,img_title2,img_src2,img_title3,img_src3
 
for row in result:
	setup()
	start_time = time.time()
	#url="https://www.aliexpress.com/item/"+str(row['itemId'])+".html"
	url="https://www.aliexpress.com/item/"+str(row['itemId'])+".html?pdp_npi=3%40dis%21GBP%2114.66%215.68%21%21%21%21%21%40211b444016881688029043856e6d96%2112000016371070548%21rec%21UK%212632283968"
	tries = 0
	p=None
	## p = alipy.get_json(url) tekrarsiz
	while tries < 1:  # bir kere donsun
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
	execution_time = end_time - start_time
	query="update crawl set lastexecsecs=%s, lastcrawled=CURRENT_TIMESTAMP where itemId=%s"
	cursor.execute(query, (str(execution_time), row['itemId']))
	connection.commit()	
	cleanup()

cursor.close()
connection.close()
print("processed records:", result)
