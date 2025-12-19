import threading
import requests
import httpx
from typing import Dict, Optional, Callable


class OkHttpUtil:
    _http_session: Optional[requests.Session] = None
    _sse_client: Optional[httpx.Client] = None
    _lock = threading.Lock()

    @classmethod
    def get_http_client(cls) -> requests.Session:
        if cls._http_session is None:
            with cls._lock:
                if cls._http_session is None:
                    session = requests.Session()
                    adapter = requests.adapters.HTTPAdapter(
                        pool_connections=1000,
                        pool_maxsize=1000,
                        max_retries=0,
                    )
                    session.mount("http://", adapter)
                    session.mount("https://", adapter)
                    cls._http_session = session
        return cls._http_session

    @classmethod
    def get_sse_client(cls) -> httpx.Client:
        if cls._sse_client is None:
            with cls._lock:
                if cls._sse_client is None:
                    cls._sse_client = httpx.Client(
                        timeout=None  # readTimeout = 0 (无限)
                    )
        return cls._sse_client

    @staticmethod
    def post_new(url: str, headers: Dict[str, str], json_body: str) -> requests.Response:
        client = OkHttpUtil.get_http_client()
        response = client.post(
            url,
            data=json_body,
            headers=headers,
            timeout=(30, 60),  # connectTimeout, readTimeout
        )
        return response

    @staticmethod
    def post_json_body(url: str, headers: Dict[str, str], json_body: str) -> str:
        print(f"post调用接口 {url} 参数：{json_body}, {headers}")
        response = OkHttpUtil.post_new(url, headers, json_body)
        if not response.ok:
            raise RuntimeError(f"调用接口 {url} 失败: {response.text}")
        return response.text

    @staticmethod
    def post_json(
        url: str,
        json_params: str,
        headers: Optional[Dict[str, str]],
        timeout: int,
    ) -> Optional[str]:
        response = requests.post(
            url,
            data=json_params,
            headers=headers,
            timeout=(timeout, timeout),
        )
        if response.ok:
            return response.text
        return None

class SseEventListener:
    def on_event(self, event: str):
        pass

    def on_complete(self):
        pass

    def on_error(self, e: Exception):
        pass
    @staticmethod
    def request_sse(
        url: str,
        json_body: str,
        headers: Dict[str, str],
        event_listener: SseEventListener,
    ):
        print(f"调用sse接口 {url} 参数：{json_body}, {headers}")
        client = OkHttpUtil.get_sse_client()

        try:
            with client.stream(
                "POST",
                url,
                headers={
                    **headers,
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json",
                },
                content=json_body,
            ) as response:
                for line in response.iter_lines():
                    if line:
                        event_listener.on_event(line.decode("utf-8"))
                event_listener.on_complete()
        except Exception as e:
            event_listener.on_error(e)
    @staticmethod
    def sse_request_async(
        url: str,
        json_body: str,
        headers: Dict[str, str],
        timeout: int,
        event_listener: SseEventListener,
    ):
        def _run():
            try:
                with httpx.Client(timeout=timeout) as client:
                    with client.stream(
                        "POST",
                        url,
                        headers=headers,
                        content=json_body,
                    ) as response:
                        for line in response.iter_lines():
                            if line:
                                event_listener.on_event(line.decode("utf-8"))
                        event_listener.on_complete()
            except Exception as e:
                event_listener.on_error(e)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
