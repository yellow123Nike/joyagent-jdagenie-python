import re
from agent_backend.agent.agent_util.string_util import (
    generate_random_string,
    text_desensitization,
    remove_special_chars,
    get_uuid,
    _luhn_bank_card_verify,
)

def test_generate_random_string():
    s = generate_random_string(16)
    assert len(s) == 16
    assert re.fullmatch(r"[a-z0-9]+", s)

def test_luhn_bank_card_verify():
    valid_card = "6226327514303272"
    invalid_card = "6226327514303273"

    assert _luhn_bank_card_verify(valid_card) is True
    assert _luhn_bank_card_verify(invalid_card) is False

def test_text_desensitization_basic():
    patterns = {
        r"(?:[^A-Za-z0-9_-]|^)password[^A-Za-z0-9_-]": "PASSWORD"
    }

    content = (
        "邮箱 test@example.com "
        "手机号 13800138000 "
        "身份证 510104199001011234 "
        "银行卡 6226327514303272 "
        "password: admin123"
    )

    result = text_desensitization(content, patterns)

    # 邮箱 @ -> 全角＠
    assert "test＠example.com" in result

    # 手机号中间脱敏
    assert "138✿✿✿✿8000" in result

    # 身份证后 6 位脱敏
    assert "510104199001✿✿✿✿✿✿" in result

    # 银行卡后 6 位脱敏
    assert "622632751430✿✿✿✿✿✿" in result

    # 自定义敏感词脱敏
    assert "PASSWORD" in result

def test_text_desensitization_internal_email():
    content = "内部邮箱 test@jd.com"
    result = text_desensitization(content, {})
    assert "test@jd.com" in result

def test_remove_special_chars():
    s = 'abc "$@=+?{}[]<>#|\' xyz'
    result = remove_special_chars(s)

    assert '"' not in result
    assert "$" not in result
    assert "@" not in result
    assert "abc" in result
    assert "xyz" in result

def test_remove_special_chars_empty():
    assert remove_special_chars(None) == ""
    assert remove_special_chars("") == ""
