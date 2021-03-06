import time
import emoji as emoji
import telepot
import requests
import conf
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

authenticate_user_id = 0
search_word_msg_id = 0
all_users_list_keyboard = None
word_search_result = None
your_token = conf.your_token
your_site = conf.your_site


class Bot:
    bot = telepot.Bot(your_token)

    ALLOWED_CHAT_IDs = conf.ALLOWED_CHAT_IDs

    main_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=emoji.emojize('All َUsers:busts_in_silhouette:', use_aliases=True)),
         ],
        [KeyboardButton(text=emoji.emojize('Search Word :mag:', use_aliases=True)),
         ]
    ], one_time_keyboard=False, resize_keyboard=True)

    def send_main_keyboard(self, chat_id):
        self.bot.sendMessage(chat_id, text='Choose action from below keyboard:',
                             reply_markup=self.main_keyboard)

    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        message_id = msg.get('message_id')
        if chat_id in self.ALLOWED_CHAT_IDs:
            if content_type == 'text':
                text = str(msg["text"])
                # Authenticate
                if message_id == authenticate_user_id + 2:
                    username, password = text.split(" ")
                    message_identifier = (chat_id, message_id)
                    self.bot.deleteMessage(message_identifier)
                    message_identifier = (chat_id, message_id - 1)
                    self.bot.deleteMessage(message_identifier)
                    self.bot.sendMessage(chat_id, "Due to security concerns, your entered username & password has "
                                                  "been removed.")
                    r = requests.post(url='%s/api/get_all_users_data/' % your_site,
                                      data={'username': username, 'password': password})
                    result = r.json().get('users_data')
                    if result == 404:
                        self.bot.sendMessage(chat_id, "Your submitted data wasn't true.\nRead the instruction "
                                                      "carefully and try again...")
                    elif result == 403:
                        self.bot.sendMessage(chat_id, "Unfortunately, your access level doesn't provide such a favor.")
                    else:
                        all_users_data = result
                        global all_users_list_keyboard
                        all_users_list_keyboard = self.generate_all_users_keyboard(all_users_data)
                        self.bot.sendMessage(chat_id, emoji.emojize(":large_blue_diamond: Access granted\nAll users:"),
                                             reply_markup=all_users_list_keyboard)

                if text == '/start':
                    self.bot.sendMessage(chat_id, 'Hello')
                    self.send_main_keyboard(chat_id)
                elif text.__contains__("All َUsers"):
                    if all_users_list_keyboard:
                        self.bot.sendMessage(chat_id, emoji.emojize('All َUsers :busts_in_silhouette:'),
                                             reply_markup=all_users_list_keyboard)
                    else:
                        self.authenticate(chat_id)
                elif text.__contains__("Search Word"):
                    if all_users_list_keyboard:
                        self.bot.sendMessage(chat_id, "Enter word:")
                        global search_word_msg_id
                        search_word_msg_id = message_id
                    else:
                        self.authenticate(chat_id)
                else:
                    if message_id == search_word_msg_id + 2:
                        word = text
                        r = requests.post(url='%s/api/search_word/' % your_site, data={'word': word})
                        if r.status_code == 200:
                            global word_search_result
                            word_search_result = r.json().get('search_result')
                            search_menu = self.generate_search_word_keyboard(word_search_result)
                            self.bot.sendMessage(chat_id, "Choose word from menu:", reply_markup=search_menu)
                        else:
                            self.bot.sendMessage(chat_id, f"Entered word '{word}' doesn't exists.")

                    elif len(text.split(". ")) == 2:
                        searched_word_id = text.split('. ')[0]
                        word_explanation = self.generate_word_search_result_msg(searched_word_id)
                        self.bot.sendMessage(chat_id, word_explanation, parse_mode='HTML')
                    elif text.__contains__("Main menu"):
                        self.send_main_keyboard(chat_id)
        else:
            self.bot.sendMessage(chat_id, "You're not allowed to use this bot!\nThanks for your visit.\nBye Bye...")
            self.bot.sendSticker(chat_id,
                                 sticker='CAACAgIAAxkBAAMbXpGKhkeRhX2FZ4nfNSeWMVRJ4YwAAm8AA_cCyA_pM_2bB4KOMhgE')
        return

    def generate_word_search_result_msg(self, word_id):
        for word in word_search_result:
            if str(word.get('id')) == str(word_id):
                text = word.get('word')
                definition = word.get('definition')
                synonyms = word.get('synonyms')
                example = word.get('example')
                s = f"<b>{text}</b>:\n\n<b>Definition</b>:\n{definition}\n\n<b>Synonyms</b>:\n{synonyms}\n\n<b>Example:</b>\n {example}"
                break
        return s

    def generate_search_word_keyboard(self, result_list):
        keyboard = [[KeyboardButton(text=emoji.emojize(":arrow_backward: Main menu", use_aliases=True))]]
        for word in result_list:
            id = word.get('id')
            w = word.get('word')
            keyboard.append([KeyboardButton(text=f"{str(id)}. {w}")])
        menu = ReplyKeyboardMarkup(keyboard=keyboard)
        return menu

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        message_id = msg['message']['message_id']
        chat_id = msg['from']['id']

        if str(query_data) == "authenticate_user":
            # Delete previously used authenticate keyboard
            message_identifier = (chat_id, message_id)
            self.bot.deleteMessage(message_identifier)

            self.bot.sendMessage(chat_id, "Enter your <b><i>Username</i></b> <i>and</i> <b><i>Password</i></b> "
                                          "separated by an space, as followed pattern:\n<i>SampleUserName "
                                          "SamplePassword</i>",
                                 parse_mode='HTML')
            global authenticate_user_id
            authenticate_user_id = message_id

        elif str(query_data).split(":")[0] == "user_detail":
            message_identifier = (chat_id, message_id)
            self.bot.deleteMessage(message_identifier)
            user_id = str(query_data).split(":")[1]
            r = requests.post(url='%s/api/get_user_detail/' % your_site, data={'user_id': user_id})
            user_detail = r.json().get('user_detail')
            user_categories = r.json().get('user_categories')

            new_keyboard = []
            for category in user_categories:
                new_keyboard.append(
                    [InlineKeyboardButton(text="Delete %s" % category.get('name'),
                                          callback_data="Delete %s" % str(category.get('id')))]
                )
            # Back to user's list button
            new_keyboard.append(
                [InlineKeyboardButton(text="Back to users list", callback_data="back_to_users_list")]
            )

            user_detail_keyboard = InlineKeyboardMarkup(inline_keyboard=new_keyboard)
            self.bot.sendMessage(chat_id, emoji.emojize(user_detail), parse_mode='HTML',
                                 reply_markup=user_detail_keyboard)

        elif str(query_data) == "back_to_users_list":
            message_identifier = (chat_id, message_id)
            self.bot.deleteMessage(message_identifier)
            self.bot.sendMessage(chat_id, "All users:\n", reply_markup=all_users_list_keyboard)

        elif str(query_data).split(" ")[0] == "Delete":
            category_id = str(query_data).split(" ")[1]
            r = requests.post(url='%s/api/delete_category/' % your_site, data={'category_id': category_id})
            status = r.json().get('status')
            user_remaining_categories = r.json().get('remaining_categories')
            if status == 200:
                new_keyboard = []

                if len(user_remaining_categories) != 0:
                    for category in user_remaining_categories:
                        new_keyboard.append(
                            [InlineKeyboardButton(text="Delete %s" % category.get('name'),
                                                  callback_data="Delete %s" % str(category.get('id')))]
                        )
                # Back to user's list button
                new_keyboard.append(
                    [InlineKeyboardButton(text="Back to users list", callback_data="back_to_users_list")]
                )

                inline_new_keyboard = InlineKeyboardMarkup(inline_keyboard=new_keyboard)

                message_identifier = (chat_id, message_id)
                self.bot.editMessageReplyMarkup(message_identifier, reply_markup=inline_new_keyboard)
            else:
                self.bot.sendMessage(chat_id, "Selected category couldn't be found!")
        return

    def authenticate(self, chat_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Authenticate me!', callback_data='authenticate_user')],
        ])
        self.bot.sendMessage(chat_id, "You have to be authenticated to proceed:", reply_markup=keyboard)
        return

    def generate_all_users_keyboard(self, all_users_data):
        keyboard_key_list = []

        for idx, user in enumerate(all_users_data):
            keyboard_key_list.append([InlineKeyboardButton(text=str(idx + 1) + ". " + user.get('username'),
                                                           callback_data="user_detail:" + str(user.get('id')))])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_key_list)
        return keyboard


b = Bot()
MessageLoop(b.bot, {'chat': b.handle,
                    'callback_query': b.on_callback_query}).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)
