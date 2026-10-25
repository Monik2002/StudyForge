from types import SimpleNamespace
from studyforge.main import finalize
def test_scoring_exact_match():
    q={"key":"q1","correct_option_ids":["A"]}
    r=SimpleNamespace(question_key="q1",selected_option_ids=["A"],is_correct=None,awarded_points=None)
    a=SimpleNamespace(question_snapshot=[q],responses=[r],passing_score=70,score_points=None,max_points=None,percentage=None,passed=None,status="in_progress",submitted_at=None)
    finalize(None,a)
    assert a.percentage==100 and a.passed and r.is_correct
def test_multiple_select_requires_exact_match():
    q={"key":"q1","correct_option_ids":["A","B"]}
    r=SimpleNamespace(question_key="q1",selected_option_ids=["A"],is_correct=None,awarded_points=None)
    a=SimpleNamespace(question_snapshot=[q],responses=[r],passing_score=70,score_points=None,max_points=None,percentage=None,passed=None,status="in_progress",submitted_at=None)
    finalize(None,a)
    assert a.percentage==0 and not r.is_correct
