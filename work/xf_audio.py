# -*- coding: utf-8 -*-

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import threading
from pydub import AudioSegment
import base64
import websocket
import threading
import time
import json
import ssl
from pydub import AudioSegment
from io import BytesIO

class SpeechRecognizer:
    STATUS_FIRST_FRAME = 0
    STATUS_CONTINUE_FRAME = 1
    STATUS_LAST_FRAME = 2

    def __init__(self, appid, api_key, api_secret, audio_bytes):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.audio_bytes = audio_bytes
        self.result = ""
        self.ws = None

    def convert_audio(self):
        audio_stream = BytesIO(self.audio_bytes)
        audio = AudioSegment.from_file(audio_stream, format="wav")
        audio = audio.set_channels(1).set_frame_rate(16000)
        output_stream = BytesIO()
        audio.export(output_stream, format="wav")
        self.audio_bytes = output_stream.getvalue()

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

    def on_message(self, ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            if code != 0:
                errMsg = message["message"]
                print(f"sid:{sid} call error:{errMsg} code is:{code}")
            else:
                data = message["data"]["result"]["ws"]
                for i in data:
                    for w in i["cw"]:
                        self.result += w["w"]
                print(f"sid:{sid} call success!,data is:{json.dumps(data, ensure_ascii=False)}")
        except Exception as e:
            print("receive msg,but parse exception:", e)

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            frameSize = 8000  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔
            status = self.STATUS_FIRST_FRAME

            audio_stream = BytesIO(self.audio_bytes)
            while True:
                buf = audio_stream.read(frameSize)
                if not buf:
                    status = self.STATUS_LAST_FRAME
                if status == self.STATUS_FIRST_FRAME:
                    # 构建第一帧数据
                    d = {"common": {"app_id": self.appid},
                         "business": {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1, "vad_eos":10000},
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    status = self.STATUS_CONTINUE_FRAME
                elif status == self.STATUS_CONTINUE_FRAME:
                    # 构建中间帧数据
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                elif status == self.STATUS_LAST_FRAME:
                    # 构建最后一帧数据
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                time.sleep(intervel)
            ws.close()

        threading.Thread(target=run).start()

    def run(self):
        self.convert_audio()  # 转换音频格式
        ws_url = self.create_url()  # 创建 WebSocket 连接的 URL
        self.ws = websocket.WebSocketApp(ws_url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def get_result(self):
        return self.result

# 使用示例
# if __name__ == "__main__":
#     recognizer = SpeechRecognizer()
#     recognizer.run()
#     print(recognizer.get_result())
