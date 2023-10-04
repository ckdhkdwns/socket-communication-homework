import datetime as dt


class Logger:
    def __init__(self, type):
        date = str(dt.datetime.now().replace(microsecond=0)).replace(" ", "-")
        self.file_path = './{}_log/log_{}.txt'.format(type, date)
        self.formatter = '>> {}'
    def log(self, message, p=True):
        if p:
            print(self.formatter.format(message))
        with open(self.file_path, 'a') as l:
            l.write(self.formatter.format(message) + "\n")
