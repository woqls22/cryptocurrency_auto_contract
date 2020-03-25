from selenium import webdriver
from pyvirtualdisplay import Display
import time

maximum = 10000  # 최대 거래 금액
sellcode = "SELL_NOW"
buycode = "BUY_NOW"


def non_comma(price):
	if(len(price)<2):
		return '0'
	result = ""
	for i in price:
		if (i == ","):
			continue
		else:
			result = result + i
	return (result)


def login():
	display = Display(visible=0, size=(1024, 768))
	display.start()
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	URL = "https://coinone.co.kr/"
	driver = webdriver.Chrome("executable_path='/root/chromedriver', chrome_options = chrome_options")
	driver.implicitly_wait(10)
	driver.get(URL)
	id = "아이디입력"
	password = "비밀번호입력"
	driver.find_element_by_css_selector('span.txt-close').click()  # 팝업창 닫기
	driver.get('https://coinone.co.kr/account/login/?next=/')
	driver.find_element_by_xpath('//*[@id="coinone_recaptcha"]/input[2]').send_keys(id)
	driver.find_element_by_xpath('//*[@id="coinone_recaptcha"]/input[3]').send_keys(password)
	driver.find_element_by_xpath('//*[@id="coinone_recaptcha"]/button').click()  # 아이디 패스워드 전송
	driver.find_element_by_css_selector('#btn_skip').click()  # 팝업창 닫기
	driver.find_element_by_css_selector('span.txt-close').click()  # 팝업창 닫기
	return driver


def account(driver):
	driver.get('https://coinone.co.kr/balance/investment')
	balance = str(driver.find_element_by_xpath(
		'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[1]/trade-chart-info-summary/div/div[2]/common-flip-number/div[1]/div[1]').text)
	before_balance = str(driver.find_element_by_xpath(
		'//*[@id="body_inner"]/div/div[2]/balance-investment/balance-investment-summary/div/div[3]/div[1]/p[2]').text)
	profit = str(driver.find_element_by_xpath(
		'//*[@id="body_inner"]/div/div[2]/balance-investment/balance-investment-summary/div/div[3]/div[2]/p[2]').text)
	profit_rate = str(driver.find_element_by_xpath(
		'//*[@id="body_inner"]/div/div[2]/balance-investment/balance-investment-summary/div/div[3]/div[3]/b').text)
	print_account_info(balance, before_balance, profit, profit_rate)
	return driver


def print_account_info(balance, before_balance, profit, profit_rate):
	print("=====코인원 현재 자산 정보=====")
	print("현재 자산 : " + balance)
	print("매수 금액 : " + before_balance)
	print("평가 손익 : " + profit)
	print("손익률 : " + profit_rate)
	print("===========================")


def downLoad_history(driver):
	# body_inner > div > div.lnb-wrap > ul > li:nth-child(3) > a
	driver.find_element_by_xpath('//*[@id="body_inner"]/div/div[1]/ul/li[3]/a').click()
	driver.find_element_by_xpath(
		'//*[@id="body_inner"]/div/div[2]/balance-transaction-history/balance-export-to-file/div/button[2]').click()
	time.sleep(10)
	print('DOWNLOAD_COMPLETE')


def detect(driver, name):
	URL = "https://coinone.co.kr/exchange/trade/" + name + "/krw"
	driver.get(URL)
	before_rate = -999.0
	buy_flag = 1
	sell_flag = 1
	ratelist = []
	desc = 0
	while (1):
		try:
			rate = str(driver.find_element_by_xpath(
				'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[1]/trade-chart-info-summary/div/div[2]/span/span[1]').text)
			highest = str(driver.find_element_by_xpath(
				'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[2]/trade-chart-info-detail/div/ul/li[1]/dl/dd').text)
			lowest = str(driver.find_element_by_xpath(
				'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[2]/trade-chart-info-detail/div/ul/li[2]/dl/dd').text)
			price = str(driver.find_element_by_xpath(
				'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[1]/trade-chart-info-summary/div/div[2]/common-flip-number/div[1]/div[1]').text)
			yesterday = str(driver.find_element_by_xpath(
				'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[2]/trade-chart-info-detail/div/ul/li[3]/dl/dd').text)
		#	print("=========================================")
		#	print("[고가 "+highest+" / "+"저가 "+lowest+"], [전일가 : "+yesterday+"]")
		except:
			pass

		try:
			driver.find_element_by_xpath('//*[@id="bid_order_form_price"]').clear()
			driver.find_element_by_xpath('//*[@id="bid_order_form_price"]').send_keys((non_comma(price)))
		except:
			pass
		if (before_rate is not -999.0 and before_rate != rate):
			print("[현재 가격 : " + price + " / " + rate + "]")
			if (rate[0] == '-'):
				ratelist.append(-float(rate[1:len(rate) - 1]))
			else:
				ratelist.append(float(rate[1:len(rate) - 1]))
			try:
				if (ratelist[0] == 0.0):
					ratelist.pop(0)
			except:
				pass
			print(ratelist)
		if (make_decision(driver, ratelist, 'sell') == sellcode and sell_flag == 1):
			make_sell(driver, 0.01, price)
			time.sleep(3)
			buy_flag = 1
			sell_flag = 0
			ratelist = []
			before_rate = -999.0
			if (rate[0] == '-'):
				ratelist.append(-float(rate[1:len(rate) - 1]))
			else:
				ratelist.append(float(rate[1:len(rate) - 1]))

		elif (make_decision(driver, ratelist, 'buy') == buycode and buy_flag == 1):
			try:
				make_buy(driver, 0.01, price)
				time.sleep(3)
				sell_flag = 1
				buy_flag = 0
				ratelist = []
				before_rate = -999.0
				if (rate[0] == '-'):
					ratelist.append(-float(rate[1:len(rate) - 1]))
				else:
					ratelist.append(float(rate[1:len(rate) - 1]))
			except:
				pass
		else:
			desc = cnt_down(ratelist)
			if (desc > 5 and sell_flag == 0):  # 가격이 너무 많이 하락함. 매도
				print("가격 떡락으로 팔게요... ㅠㅠ")
				try:
					make_sell(driver, 0.003, price)
					time.sleep(3)
					buy_flag = 1
					sell_flag = 0
					ratelist = []
					before_rate = -999.0
					desc = 2
				except:
					pass
		if (len(ratelist) > 15):
			ratelist = []
		time.sleep(1)
		before_rate = rate


def make_sell(driver, quantity, price):  # 매도
	prices = int(non_comma(price))  # 최종 거래 금액
	total = prices * quantity
	if (total > 500 and total < maximum):
		driver.find_element_by_xpath(
			'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[7]/trade-order-form/div/ui-tabset/ul/li[2]/a/span').click()  # 매도 탭 클릭
		price = str(driver.find_element_by_xpath(
			'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[3]/trade-chart-info/div[1]/div[1]/trade-chart-info-summary/div/div[2]/common-flip-number/div[1]/div[1]').text)
		driver.find_element_by_xpath('//*[@id="ask_order_form_price"]').clear()
		driver.find_element_by_xpath('//*[@id="ask_order_form_price"]').send_keys((non_comma(price)))  # 가격입력
		driver.find_element_by_xpath('//*[@id="ask_order_form_amount"]').clear()
		driver.find_element_by_xpath('//*[@id="ask_order_form_amount"]').send_keys(str(quantity))  # 거래량 기입
		driver.find_element_by_xpath(
			'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[7]/trade-order-form/div/ui-tabset/div/uitab[2]/trade-order-content/div/div[4]/button').click()
		print("매도 주문 체결 [단위가격 : " + str(price) + ", 총가격 : " + str(total) + "]")
		print("다음 매수 타이밍 까지 기다릴게요... ")
	else:
		print("total : " + str(total))


# 매도 체결


def make_buy(driver, quantity, price):  # 매수
	prices = int(non_comma(price))  # 최종 거래 금액
	quantity = float(quantity)
	total = prices * quantity  # 최종 거래 금액
	if (total > 500 and total < maximum):
		driver.find_element_by_xpath(
			'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[7]/trade-order-form/div/ui-tabset/ul/li[1]/a/span').click()  # 매수탭클릭
		driver.find_element_by_xpath('//*[@id="bid_order_form_price"]').clear()
		driver.find_element_by_xpath('//*[@id="bid_order_form_price"]').send_keys((non_comma(price)))  # 가격입력
		driver.find_element_by_xpath('//*[@id="bid_order_form_amount"]').clear()
		driver.find_element_by_xpath('//*[@id="bid_order_form_amount"]').send_keys(str(quantity))  # 거래량 기입
		driver.find_element_by_xpath(
			'//*[@id="style-root"]/trading-root/trade-root/div/trade-pair/article/gridster/gridster-item[7]/trade-order-form/div/ui-tabset/div/uitab[1]/trade-order-content/div/div[4]/button').click()
		print("매수 주문 체결 [단위가격 : " + str(prices) + ", 총가격 : " + str(total) + "]")
		print("다음 매도 타이밍 까지 기다릴게요... ")
	else:
		print("total : " + str(total))


def make_decision(driver, ratelist, turn):
	incr = 0
	desc = 0
	if (len(ratelist) > 2):
		for i in range(0, len(ratelist) - 1):
			if (ratelist[i] < ratelist[i + 1] and turn == 'sell'):
				if (ratelist[i + 1] - ratelist[i] >= 0.5):
					return sellcode
				incr = incr + 1
				if (incr >= 2):
					return sellcode
			if (ratelist[i] > ratelist[i + 1] and turn == 'buy'):
				desc = desc + 1
				if (desc >= 2):
					return buycode
	return 'none'


def cnt_down(ratelist):
	desc = 0
	if (len(ratelist) < 5):
		return 0
	for i in range(0, len(ratelist) - 1):
		if (ratelist[i] > ratelist[i + 1]):
			desc = desc + 1
	return desc


driver = login()
# 최초 8500원 // 2020-03-24-22:25
print("이더리움 자동매매 : 단위수량 0.004ETH")
detect(driver, "eth")
