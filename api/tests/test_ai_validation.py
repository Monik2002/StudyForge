import pytest
from studyforge.ai import validate_question
def test_valid_question():
    q=validate_question({"type":"single_choice","stem":"What does SSH provide?","options":[{"id":"A","text":"Secure remote access"},{"id":"B","text":"Disk formatting"}],"correct_option_ids":["A"],"explanation":"SSH supports secure remote access.","difficulty":"easy"},1)
    assert q["correct_option_ids"]==["A"]
def test_invalid_answer_id_rejected():
    with pytest.raises(ValueError):
        validate_question({"type":"single_choice","stem":"What does SSH provide?","options":[{"id":"A","text":"Remote access"},{"id":"B","text":"Formatting"}],"correct_option_ids":["Z"],"explanation":"This is a useful explanation."},1)
