멀티 쓰레드 행렬 곱셈 연산 구현
=============
1개의 메인 서버와 4개의 클라이언트간의 멀티 쓰레드 행렬 연산 프로그램입니다. 

## 실행 방법
### 서버
프로젝트 폴더 내의 `server.py`를 실행합니다.
```bash
python server.py
```
### 서버
프로젝트 폴더 내의 `client.py`를 실행합니다.
```bash
python client.py
```

## 세부 과정
- 서버에 4개의 클라이언트가 접속합니다.
- 접속이 완료되면 서버는 `RoundHandler`의 `run()` 메서드를 통해 라운드를 시작합니다.
- `run()` 메서드는 내부의 `round()`를 100번 실행합니다.
- `round()`는 6개의 `round_thread()`스레드를 생성합니다.
- `round_thread()`에서는 행렬을 제공할 클라이언트 `input clients`와 행렬을 계산할 클라이언트 `output_clients`를 나눕니다.
- 반복문을 통해 `input_clients`에서 행과 열을 제공받고 제공받은 값을 `output_clients`에게 보내 계산된 값을 가져옵니다. 
    - `output_clients`에게 공정하게 분배하기 위해 `fair_num`이라는 상수를 사용합니다.
- 받아온 값을 업데이트합니다.


## 프로젝트 구조
```bash
├── client.py
├── config.ini
├── handler
│   ├── client
│   │   ├── _client.py
│   │   └── _client_message.py
│   └── server
│       ├── _round.py
│       ├── _server.py
│       └── _server_message.py
├── readme.md
├── server.py
└── util
    └── logger.py

```
### MessageHandler
메세지와 관련된 클래스입니다.  
- `_client_message.py` 의 `ClientMessageHandler` : 클라이언트가 송신, 수신하는 메서드들이 있습니다.
- `_server_message.py` 의 `ServerMessageHandler` : 서버가 송신, 수신하는 메서드들이 있습니다. 

### ClientHander
클라이언트를 제어합니다.
> `ClientMessageHandler`를 상속받습니다.
- `refresh_metrix(self, value)` : 라운드 종료 로그를 남기고 행렬을 새로 생성합니다.
- `receive(self)` : 서버로부터 받아온 데이터를 파싱합니다. 각 요청 종류별로 `ClientMessageHandler`의 메서드를 실행합니다.
- `run(self)` : 클라이언트 소켓을 만들고 서버와 연결합니다.

### ServerHandler
서버를 제어합니다. 내부에서 `RoundHandler`를 통해 행렬 연산을 시작시킵니다.
- `client_thread(self, client)` : 클라이언트가 접속했음을 알리고 `clients`리스트에 클라이언트를 추가합니다.
- `send_disconnect_signal(self)` : 클라이언트들과의 연결을 종료합니다.
- `run(self)` : 서버를 실행합니다. 만약 서버에 4개의 클라이언트들이 접속했다면 `RoundHandler`의 `run()` 메서드를 호출합니다.

### RoundHandler
라운드를 관리합니다.
> `ServerMessageHandler`를 상속받습니다.
- `round(self)` : 각 연산 케이스들을 병렬로 실행시킵니다.
- `round_thread(self, index)` : <u>행렬의 정보를 제공할 클라이언트</u>와 <u>제공받은 값을 계산할 클라이언트</u>를 나눕니다. 값을 받아와 계산할 클라이언트들에게 **공평**하게 나눕니다.
- `update_result(...)` : 받아온 값을 바로 서버에 업데이트합니다.
- `reset_result(self)` : 6개의 행렬을 새로 만듭니다.
- `save_round_result(self)` : <u>전체 결과</u>를 담는 리스트에 <u>한 라운드의 결과</u>를 저장합니다.
- `end_round(self)` : 라운드가 끝났을 때 호출됩니다. 
- `print_result(self)` : 종료되기 전 round 모든 로그를 출력합니다.
- `run(self)` : `round` 메서드를 100번 실행시킵니다.



## Syncronoization
`round_thread()`를 그냥 실행시켰을 때 쓰레드 간의 충돌로 정상적인 작동이 되지 않았습니다. `threading.Lock()`을 통해 
Race Condition을 방지할 수 있었습니다. 이 메서드는 스레드가 공유 자원에 접근하기 전에 잠금을 걸고, 사용이 끝나면 잠금을 해제하는 방식으로 동기화를 제어합니다.
```python
import threading

#Example of get_row()
lock = threading.Lock()

def get_row(target_client, row_index):
    lock.acquire() # 잠금
    target_client.send(make_encoded_json("row", row_index))
    row = json.loads(target_client.recv(1024).decode(encoding))
    lock.release() # 잠금 해제
```