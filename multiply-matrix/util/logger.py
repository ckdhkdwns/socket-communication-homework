import datetime as dt


class Logger:
    def __init__(self, host_type):
        date = str(dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        self.file_path = './{}_log/log_{}.txt'.format(host_type, date)
        self.formatter = '>> {}'

    def log(self, message, p=True):
        if p:
            print(self.formatter.format(message))
        with open(self.file_path, 'a') as l:
            l.write(self.formatter.format(message) + "\n")
