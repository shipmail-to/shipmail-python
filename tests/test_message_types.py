from shipmail import SendMessageParams


def test_send_message_params_declares_from_as_optional() -> None:
    params: SendMessageParams = {
        "from": "hello@example.com",
        "to": ["customer@example.com"],
        "subject": "Hello",
        "text": "Hi",
    }

    assert params["from"] == "hello@example.com"
    assert "from" in SendMessageParams.__optional_keys__
    assert SendMessageParams.__required_keys__ == frozenset({"subject", "to"})
