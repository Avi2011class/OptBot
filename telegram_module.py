import enum
import getpass
import telegram.ext
import aes
import hashlib
import os
import image_processing


class AsciiBot:

    @staticmethod
    def text_message_echo(bot: telegram.bot.Bot, update: telegram.update.Update):
        response = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=response)

    @staticmethod
    def start_command(bot: telegram.bot.Bot, update: telegram.update.Update):
        bot.send_message(chat_id=update.message.chat_id, text='To start, send me a picture')

    def photo_message(self, bot: telegram.bot.Bot, update: telegram.update.Update, *args, **kwargs):
        try:
            file_id = update.message.photo[-1]
            new_file = bot.get_file(file_id)

            hash = '{}:::{}'.format(update.message.chat_id, file_id)
            hash = str(hashlib.md5(hash.encode()).hexdigest())

            filename = 'images/downloaded_{}.jpg'.format(hash)

            print('file_id:', file_id)
            print(update.message.from_user.__dict__)
            print('-' * 50)

            bot.send_message(chat_id=update.message.chat_id, text='подождите...')

            new_file.download(filename)
            s = self.converter.Process(filename)
            s = self.converter.upload_ascii(s)

            bot.send_message(chat_id=update.message.chat_id, text=s)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    @staticmethod
    class AuthMode(enum.IntEnum):
        TOKEN = 1
        CRYPTO_TOKEN = 2
        INTERACTIVE = 3
        TOKEN_FILE = 4

    def __init__(self, mode: AuthMode, **kwargs):

        self.token = None

        print(mode)
        if mode == AsciiBot.AuthMode.TOKEN:
            self.token = kwargs['token']

        elif mode == AsciiBot.AuthMode.CRYPTO_TOKEN:
            cipher = aes.AESCipher(key=kwargs['key'])
            self.token = cipher.decrypt(kwargs['token'])

        elif mode == AsciiBot.AuthMode.INTERACTIVE:
            token = input('EncryptedToken: ')
            key = getpass.getpass(prompt='Password: ', stream=None)
            cipher = aes.AESCipher(key=key)
            self.token = cipher.decrypt(token)

        elif mode == AsciiBot.AuthMode.TOKEN_FILE:
            filename = input('Filename: ') \
                if 'filename' not in kwargs else kwargs['filename']
            key = getpass.getpass(prompt='Password: ', stream=None) \
                if 'key' not in kwargs else kwargs['key']

            cipher = aes.AESCipher(key=key)
            self.token = cipher.decrypt(open(filename, 'r').read())

        else:
            raise Exception('Mode', 'UnknownMode')

        self.updater = telegram.ext.Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher

        font_size = int(input("Font size: ")) \
            if 'font_size' not in kwargs else kwargs['font_size']

        default_width = int(input("Default width: ")) \
            if 'default_width' not in kwargs else kwargs['default_width']

        # The main picture converter
        self.converter = image_processing.AsciiImageProcessing(font_size, default_size=(default_width, default_width))

        # Handlers registration
        start_command_handler = telegram.ext.CommandHandler('start', self.start_command)
        self.dispatcher.add_handler(start_command_handler)

        text_message_handler = telegram.ext.MessageHandler(telegram.ext.Filters.text, self.text_message_echo)
        self.dispatcher.add_handler(text_message_handler)

        photo_handler = telegram.ext.MessageHandler(telegram.ext.Filters.photo, self.photo_message, pass_chat_data=True, pass_user_data=True)
        self.dispatcher.add_handler(photo_handler)

    def start(self):
        print('Running...')
        self.updater.start_polling(clean=True)
        self.updater.idle()

    def stop(self):
        self.updater.stop()


a = AsciiBot(AsciiBot.AuthMode.TOKEN_FILE)
a.start()
