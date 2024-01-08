from emecAPI.utils.fields import normalize_key, convert_text_to_base64, convert_b64_to_text, set_url
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

def test_set_url():
    # Test case 1: Testing 'ies' method
    assert set_url('ies', 'abc123') == 'https://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/abc123'

    # Test case 2: Testing 'metrics' method
    assert set_url('metrics', 'def456') == 'https://emec.mec.gov.br/emec/consulta-ies/listar-historico-indicadores-ies/d96957f455f6405d14c6542552b0f6eb/def456/list/1000'

    # Test case 3: Testing 'regulatory_act' method
    assert set_url('regulatory_act', 'ghi789') == 'https://emec.mec.gov.br/emec/consulta-ies/listar-ato-regulatorio/d96957f455f6405d14c6542552b0f6eb/ghi789/list/1000'

    # Test case 4: Testing 'mec_process' method
    assert set_url('mec_process', 'jkl012') == 'https://emec.mec.gov.br/emec/consulta-ies/listar-processo/d96957f455f6405d14c6542552b0f6eb/jkl012/list/1000'

    # Test case 5: Testing 'campus' method
    assert set_url('campus', 'mno345') == 'https://emec.mec.gov.br/emec/consulta-ies/listar-endereco/d96957f455f6405d14c6542552b0f6eb/mno345/list/1000'

    # Test case 6: Testing 'courses' method
    assert set_url('courses', 'pqr678') == 'https://emec.mec.gov.br/emec/consulta-ies/listar-curso/d96957f455f6405d14c6542552b0f6eb/pqr678/list/1000'

    # Test case 7: Testing 'courses_details_info_general' method
    assert set_url('courses_details_info_general', 'stu901', 'vwx234') == 'https://emec.mec.gov.br/emec/consulta-curso/detalhe-curso/9f1aa921d96ca1df24a34474cc171f61/0/stu901/vwx234'

    # Test case 8: Testing 'courses_details_detail' method
    assert set_url('courses_details_detail', 'yz0123', '456abc') == 'https://emec.mec.gov.br/emec/consulta-curso/detalhe-curso/9f1aa921d96ca1df24a34474cc171f61/1/yz0123/456abc'

    # Test case 9: Testing unknown method
    assert set_url('unknown', 'def456') == None