from emecAPI.utils.fields import normalize_key, convert_text_to_base64, convert_b64_to_text
import base64

def test_normalize_key():
    # Test case 1: Normalizing a key with leading and trailing whitespace and colons
    assert normalize_key("  Key  ") == "key"

    # Test case 2: Normalizing a key with uppercase letters
    assert normalize_key("KeY") == "key"

    # Test case 3: Normalizing a key with spaces
    assert normalize_key("key with spaces") == "key_with_spaces"

    # Test case 4: Normalizing a key with parentheses
    assert normalize_key("(key)") == "key"

    # Test case 5: Normalizing a key with non-ascii characters
    assert normalize_key("këÿ") == "key"

    # Test case 6: Normalizing a key with a mix of characters
    assert normalize_key("  Key with (spaces) and Ëxträ Chärs  ") == "key_with_spaces_and_extra_chars"

def test_convert_text_to_base64():
    # Test case 1: Converting a text string to base64 encoding
    assert convert_text_to_base64("Hello, World!") == "SGVsbG8sIFdvcmxkIQ=="

    # Test case 2: Converting an empty string to base64 encoding
    assert convert_text_to_base64("") == ""

    # Test case 3: Converting a text string with non-ascii characters to base64 encoding
    assert convert_text_to_base64("Olá, Mundo!", encoding="latin-1") == "T2zhLCBNdW5kbyE="

    # Test case 4: Converting a text string with special characters to base64 encoding
    assert convert_text_to_base64("Hello, @World!", encoding="utf-8") == "SGVsbG8sIEBXb3JsZCE="

    # Test case 5: Converting a text string with newline characters to base64 encoding
    assert convert_text_to_base64("Hello\nWorld!", encoding="utf-8") == "SGVsbG8KV29ybGQh"

def test_convert_b64_to_text():
    # Test case 1: Converting a base64 encoded string to plain text
    assert convert_b64_to_text("SGVsbG8sIFdvcmxkIQ==") == "Hello, World!"

    # Test case 2: Converting an empty string to plain text
    assert convert_b64_to_text("") == ""

    # Test case 3: Converting a base64 encoded string with non-ascii characters to plain text
    assert convert_b64_to_text("T2zhLCBNdW5kbyE=", encoding="latin-1") == "Olá, Mundo!"

    # Test case 4: Converting a base64 encoded string with special characters to plain text
    assert convert_b64_to_text("SGVsbG8sIEBXb3JsZCE=", encoding="utf-8") == "Hello, @World!"

    # Test case 5: Converting a base64 encoded string with newline characters to plain text
    assert convert_b64_to_text("SGVsbG8KV29ybGQh", encoding="utf-8") == "Hello\nWorld!"