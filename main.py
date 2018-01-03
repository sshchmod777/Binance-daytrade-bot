from binance.client import Client
from private import api_key, api_secret
import time, os

def set_run_time():
	print("Welcome!")
	message = "For how long should the bot work (in hours)?\n"
	run_time = time.time() + 3600 * int(input(message))
	return run_time

def get_low_price(currency): # returns 24hr low price
	price_info = client.get_ticker(symbol = currency)
	low_price = price_info.get("lowPrice")
	return float(low_price)

def get_last_price(currency): # returns the most recent price
	price_info = client.get_ticker(symbol = currency)
	last_price = price_info.get("lastPrice")
	return float(last_price)

def get_coefficient(): # returns float of something like 1.02
	last_price = get_last_price(currency)
	low_price = get_low_price(currency)
	return float(last_price/low_price)

def get_free_currency_balance(currency):
	for item in client.get_account().get('balances'):
		if item.get('asset') == currency:
			return int(float(item.get('free')))

def get_locked_currency_balance(currency):
	for item in client.get_account().get('balances'):
		if item.get('asset') == currency:
			return int(float(item.get('locked')))

def get_last_15_min_price_data(currency):
	prices = []
	timestamp = int(round(time.time() * 1000)) - 930000
	data = client.get_klines(symbol = currency, interval = "1m",
	startTime = timestamp)
	for entry in data:
		prices.append(float(entry[1]))
	return sorted(prices)

def count_price_frequency(price_list):
	result = {}
	for price in price_list:
		if price not in result:
			result.update({price:price_list.count(price)})
	return result

def place_buy_order(currency, quantity):
	buy_price = determine_buy_price(currency)
	price = '{:.8f}'.format(buy_price)
	client.order_limit_buy(symbol=currency,
	quantity=quantity, price=price)
	return buy_price

def place_sell_order(currency, quantity, buy_price):
	sell_price = determine_sell_price(currency, buy_price)
	price = '{:.8f}'.format(sell_price)
	try:
		client.order_limit_sell(symbol=currency,
		 quantity=quantity, price=price)
	except:
		client.order_limit_sell(symbol=currency,
		 quantity=quantity-1, price=price)
	return sell_price

def determine_buy_price(currency):
	while get_coefficient() > 2: # 1 = 100% 24hr lowest price modify value to limit buy price
		os.system('clear')
		print("Waiting for price to change.")
		time.sleep(0.5)
	last_price = get_last_price(currency)
	prices = get_last_15_min_price_data(currency)
	frequencies = count_price_frequency(prices)
	buy_price = prices[0]
	max_found_freq = frequencies.get(buy_price)
	for price in prices:
		if price < last_price:
			if frequencies.get(price) > max_found_freq:
				buy_price = price
				max_found_freq = frequencies.get(price)
		else:
			break
	return buy_price

def determine_sell_price(currency, buy_price):
	last_price = get_last_price(currency)
	min_profit = 0.00000010 #Modify value to set minimum profit
	if buy_price + min_profit <= last_price:
		return last_price
	else:
		prices = get_last_15_min_price_data(currency)[::-1]
		frequencies = count_price_frequency(prices)
		sell_price = buy_price + min_profit
		max_found_freq = frequencies.get(sell_price)
		if max_found_freq is None:
			max_found_freq = 0
		for price in prices:
			if price > buy_price + min_profit:
				if frequencies.get(price) > max_found_freq:
					sell_price = price
					max_found_freq = frequencies.get(price)
			else:
				break
		return sell_price

def time_window(currency, minutes):
	waiting_time = time.time() + 60 * minutes
	while time.time() < waiting_time:
		if len(get_open_orders(currency)) != 0:
			os.system('clear')
			print("Waiting for an order to finish.")
		else:
			print("Success!.")
			break
		time.sleep(0.5)

def reopen_buy_order(currency, quantity, buy_price):
	if determine_buy_price(currency) != buy_price:
		if cancel_order(currency):
			return place_buy_order(currency, quantity)
	return buy_price

def reopen_sell_order(currency, quantity, buy_price, sell_price):
	if determine_sell_price(currency, buy_price) != sell_price:
		if cancel_order(currency):
			return place_sell_order(currency, quantity, buy_price)
	return sell_price

def cancel_order(currency): #Cancels orders if filled is zero and returns true if that is the case
	orders = get_open_orders(currency)
	if len(orders) != 0:
		for order in orders:
			order_id = order.get('orderId')
			order_filled = int(float(order.get('executedQty')))
			if order_filled == 0:
				client.cancel_order(symbol=currency, orderId=order_id)
				return True
	return False

def get_open_orders(currency): #Unnecessary but makes code shorter
	return client.get_open_orders(symbol=currency)

def buying_state(currency, quantity):
	buy_price = place_buy_order(currency, quantity)
	while len(get_open_orders(currency)) != 0:
		time_window(currency, 0.125)
		buy_price = reopen_buy_order(currency, quantity, buy_price)
	return buy_price

def selling_state(currency, quantity, buy_price):
	sell_price = place_sell_order(currency, quantity, buy_price)
	while len(get_open_orders(currency)) != 0:
		time_window(currency, 0.125)
		sell_price = reopen_sell_order(currency, quantity, buy_price, sell_price)

if __name__ == "__main__":
	run_time = set_run_time()
	print("Connecting...")
	client = Client(api_key, api_secret)
	currency = "FUNBTC" #Modify value to change currency
	quantity = 500 #Modify value to change quantity
	while time.time() < run_time:
		try:
			os.system('clear')
			buy_price = buying_state(currency, quantity)
			selling_state(currency, quantity, buy_price)
			time.sleep(0.5)
		except:
			client = Client(api_key, api_secret)
