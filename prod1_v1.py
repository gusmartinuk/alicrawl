# aliexpress product extraction with python
import sys, alipy
import pyperclip
import time

print('=' * 60)
print('DOUBLE CHECK PRODUCT PRICES!!! THEY MAY BE WRONG!!!')
print('=' * 60)

urlfile='urls.txt'
if len(sys.argv) == 2:
	urlfile=sys.argv[1]

with open(urlfile, 'r') as f:
	urls = [url for url in f.read().splitlines() if url.strip()[0] != '#']

alipy.setup()

excel_table = ""

with open('backup_clipboard.txt', 'w+', encoding='utf-8') as f:
	for url in urls:
		tries = 0
		## p = alipy.get_json(url) tekrarsiz
		while tries < 10:
			try:
				p = alipy.get_json(url)
			except Exception as e:
				print(type(e).__name__, e)
				print('Retrying...' if tries < 9 else 'Proceeding...')
			else:
				break
			tries += 1
			time.sleep(2)
		if not p:
			continue

		line = [
			p['name'],
			f'"=HYPERLINK(""{url}"",""X"")"',
			min(max(p['sku_list'][0]['sku_discount_price'], p['sku_list'][0]['sku_calculated_price']), p['sku_list'][0]['sku_full_price']),
			p['shipping_fee'],
			'#',
			'#',
			'9.99',
			'10',
			'.13'
		]
		linestr = '\t'.join([str(v) for v in line]) + '\n'
		excel_table += linestr
		f.write(linestr)

pyperclip.copy(excel_table)

alipy.cleanup()
