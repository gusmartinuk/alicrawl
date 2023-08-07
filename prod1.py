# aliexpress product extraction with python
import sys, alipy
import pyperclip
import time
import pymysql
from config import *

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper

alipy.setup()

cursor = connection.cursor(pymysql.cursors.DictCursor)
query="select itemId from aliexpress_db.crawl where title is null order by lastcrawled"
cursor.execute(query)
result=cursor.fetchall()
for row in result:
	start_time = time.time()
	url="https://www.aliexpress.com/item/"+str(row['itemId'])+".html"
	tries = 0
	## p = alipy.get_json(url) tekrarsiz
	while tries < 2:
		try:
			p = alipy.get_json(url)
		except Exception as e:
			print(type(e).__name__, e)
			print('Retrying...')
		else:
			break
		tries += 1
		time.sleep(2)
	if not p:
		continue
	else:
		query = "INSERT INTO crawl SET itemId=%s, title=%s, description=%s, data=%s, shipops=%s, lastcrawled=CURRENT_TIMESTAMP "
		query += "ON DUPLICATE KEY UPDATE title=VALUES(title), description=VALUES(description), data=VALUES(data), shipops=VALUES(shipops), lastcrawled=CURRENT_TIMESTAMP"
		cursor.execute(query, (p['itemId'], p['title'], p['description'], p['data'], p['shipOps']))
		connection.commit()
	time.sleep(1)	# 1 sec wait between pages
	end_time = time.time()	
	execution_time = end_time - start_time
	query="update crawl set lastexecsecs=%s where itemId=%s"
	cursor.execute(query, (str(execution_time), p['itemId']))
	connection.commit()	

alipy.cleanup()
cursor.close()
connection.close()
print("records:", result)
