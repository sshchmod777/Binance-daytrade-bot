# Binance-daytrade-bot
Basically a binance bot that buys and sells currency.
Buy/sell algorithm - The bot takes price data of the last 15 minutes, finds a price that is lower
than the most recent and is the most frequent within those 15 minutes and places a buy order with that price.
Sell orders work the same way except that the bot finds a price that is higher than the most recent price.
If currency is not bought or sold the bot reevaluates the price and if there are changes cancels and reopens the order.
There can't be any other orders with currency that the bot is trading with.
The user can modify the max buy price, minimum profit, currency and quantity in the code.
USE AT YOUR OWN RISK.
Only use money you can afford to lose or none at all.
