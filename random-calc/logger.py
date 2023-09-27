import logging
import datetime as dt

# ANSI 이스케이프 코드를 사용하여 색상 정의
COLORS = {
    'RESET': '\033[0m',
    'INFO': '\033[97m',  # 흰색
}

# 색상을 적용하는 커스텀 로깅 핸들러 정의
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_message = super(ColoredFormatter, self).format(record)
        if record.levelname == 'INFO':
            return COLORS['INFO'] + log_message + COLORS['RESET']
        return log_message


# 로거 설정
def Logger(type):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 로그 메시지에 색상을 적용한 포매터 설정
    formatter = ColoredFormatter('>> %(message)s')
    console_handler.setFormatter(formatter)


    log_file_name = "log_{}".format(dt.datetime.now())

    file_handler = logging.FileHandler('./{}_log/{}.txt'.format(type, log_file_name), mode='w') ## 파일 핸들러 생성
    file_formatter = logging.Formatter(">> %(message)s")
    file_handler.setFormatter(file_formatter) ## 텍스트 포맷 설정
    logger.addHandler(file_handler) ## 핸들러 등록

    # 핸들러를 로거에 추가
    logger.addHandler(console_handler)
    return logger