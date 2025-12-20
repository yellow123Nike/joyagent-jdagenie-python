# tests/test_ok_http_util.py

import json
import logging

from agent_backend.agent.agent_util.ok_http_util import OkHttpUtil


class TestSseListener:
    def __init__(self):
        self.contents = []
        self.completed = False
        self.error = None

    def on_event(self, event: str):
        # 原始 SSE 行
        print(f"SSE RAW EVENT: {event}")

        # 如果是 OpenAI-style stream，解析 content
        try:
            if event == "[DONE]":
                return
            data = json.loads(event)
            delta = data["choices"][0].get("delta", {})
            if "content" in delta:
                self.contents.append(delta["content"])
                print(f"SSE TOKEN: {delta['content']}")
        except Exception:
            pass

    def on_complete(self):
        self.completed = True
        print("SSE COMPLETE")

    def on_error(self, e: Exception):
        self.error = e
        print(f"SSE ERROR: {e}")

#普通post请求
def test_post_json_body_success():
    url = "http://192.168.88.235:18006/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3-32B-AWQ",
        "messages": [
            {
                "role": "user",
                "content": "您好啊"
            }
        ]
    }

    response_text = OkHttpUtil.post_json_body(
        url,
        headers=headers,
        json_body=json.dumps(payload, ensure_ascii=False),
    )

    data = json.loads(response_text)

    assert "choices" in data
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert len(data["choices"][0]["message"]["content"]) > 0

    print("模型回复：", data["choices"][0]["message"]["content"])

def test_post_json_success():
    url = "http://192.168.88.235:18006/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3-32B-AWQ",
        "messages": [
            {
                "role": "user",
                "content": "您好啊"
            }
        ]
    }

    result = OkHttpUtil.post_json(
        url=url,
        json_params=json.dumps(payload, ensure_ascii=False),
        headers=headers,
        timeout=10,
    )

    assert result is not None

def test_post_json_fail_return_none():
    result = OkHttpUtil.post_json(
        url="http://0.0.0.0:8000/not_exist",
        json_params="{}",
        headers=None,
        timeout=2,
    )

    assert result is None

def test_sync_sse():
    listener = TestSseListener()

    url = "http://192.168.88.235:18006/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "stream": True,
        "model": "Qwen/Qwen3-32B-AWQ",
        "messages": [
            {
                "role": "user",
                "content": "您好啊"
            }
        ]
    }
    OkHttpUtil.request_sse(
        url=url,
        json_body=json.dumps(payload, ensure_ascii=False),
        headers=headers,
        event_listener=listener,
    )

    assert listener.error is None
    assert listener.completed is True

