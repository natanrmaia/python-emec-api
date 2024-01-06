from emecAPI.utils.fields import normalize_key

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