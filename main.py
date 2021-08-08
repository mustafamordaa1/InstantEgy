import telebot
import requests
from telebot import types
from bs4 import BeautifulSoup 
import sqlite3


API_KEY = "1886396394:AAFp1NJDpxpFbiPOgfhWKVtLP_DEVue-HDc"
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start','help'])
def start(message):
	bot.send_message(message.chat.id, "Enter (/watch serie season ep)  \n Do not entre spaces between serie name words instead use ' - ' dash markup \n eg : /watch game-of-thrones 3 4")
@bot.message_handler(commands=['watch'])
def info(message):
	chat_id = message.chat.id
	conn = sqlite3.connect('shows.db')
	c = conn.cursor()
	s1 = message.text
	info = s1.split(" ")
	
	try:
		serie = info[1]
		season = info[2]
		ep = info[3]
	except Exception as p :
		bot.send_message(message.chat.id,"Your input is wrong")
		return p
		
	bot.send_message(message.chat.id, f"You choosed { serie } season { season } episode { ep } \n PLEASE WAIT ... ")
	c.execute("SELECT * FROM series WHERE name=? AND id=?",(serie,chat_id))
	check = c.fetchone()
	if check == None :
		c.execute("INSERT INTO series VALUES (?,?,?,?)",(serie, season, ep, chat_id))
	else :
		c.execute("UPDATE series SET season = ? ,ep = ?  WHERE name = ? AND id = ?",(season,ep,serie, chat_id))
	URL = f"https://egy.best/episode/{ serie  }-season-{ season }-ep-{ ep }/"
	r = requests.get(URL) 
	soup = BeautifulSoup(r.content, 'html5lib')
	div = soup.find('iframe', attrs={'class':'auto-size'})
	if div == None :
		markup = types.ReplyKeyboardMarkup(row_width=1)
		itembtn = types.KeyboardButton('/help')
		markup.add(itembtn)
		bot.send_message(chat_id,"There is no result", reply_markup=markup)
		return 'INPUT ERROR'
		
	link="https://ello.egybest.bid"+ div['src']
	photo = soup.find('img')
	photo_URL = photo['src']
	response = requests.get(photo_URL)
	file = open("sample_image.png", "wb")
	file.write(response.content)
	PHOTO = open('sample_image.png', 'rb')
	bot.send_photo(chat_id, PHOTO)
	file.close()
	PHOTO.close()
	bot.send_message(chat_id,link )
	conn.commit()
	conn.close()

@bot.message_handler(commands=['my'])
def my(message):
	chat_id = message.chat.id
	conn = sqlite3.connect('shows.db')
	c = conn.cursor()
	s1 = message.text
	info = s1.split(" ")
	serie = info[1]
	c.execute("SELECT * FROM series WHERE name=? AND id = ?",(serie,chat_id))
	check = c.fetchone()
	markup = types.ReplyKeyboardMarkup(row_width=2)
	if check == None :
		itembtn1 = types.KeyboardButton('/my_series')
		markup.add(itembtn1)
		bot.send_message(chat_id, "You didn't wathced that show", reply_markup=markup)
	else :
		itembtn2 = types.KeyboardButton(f'/watch { serie } { check[1] } { check[2]+1 }')
		markup.add(itembtn2)
		bot.send_message(chat_id, "watch the next episode", reply_markup=markup)
	print(chat_id)
	conn.commit()
	conn.close()	
		
@bot.message_handler(commands=['my_series'])
def my_series(message):
	chat_id = message.chat.id
	conn = sqlite3.connect('shows.db')
	c = conn.cursor()
	c.execute("SELECT * FROM series WHERE id =?",(chat_id,))
	inf = c.fetchall()
	info = inf
	for i in info :
		bot.send_message(chat_id, i[0] + " , season : "+ str(i[1]) +" , episode : "+str(i[2]))
	conn.commit()
	conn.close()

bot.polling()
