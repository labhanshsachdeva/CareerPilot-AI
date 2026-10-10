from career_engine import analyze_resume, make_interview_pack, make_improvement_plan

def test_analysis_has_expected_fields(monkeypatch):
    monkeypatch.setattr('career_engine._llm_json', lambda *args, **kwargs: None)
    result = analyze_resume('Python developer with pandas project', 'Python and pandas required', 'Data Analyst')
    assert 0 <= result['coverage'] <= 100
    assert isinstance(result['strengths'], list)
    assert isinstance(result['gaps'], list)
    assert 'Role Fit Brief' in result['report']

def test_empty_input_rejected():
    try:
        analyze_resume('', 'some job description')
    except ValueError:
        pass
    else:
        raise AssertionError('Expected ValueError')

def test_interview_fallback_has_questions(monkeypatch):
    monkeypatch.setattr('career_engine._llm_json', lambda *args, **kwargs: None)
    pack = make_interview_pack('AI Engineer', 'Python, ML', 'Built a small ML project', 5)
    assert 'Interview Studio' in pack
    assert '## 5.' in pack

def test_action_plan_has_two_weeks():
    plan = make_improvement_plan()
    assert len(plan) == 2
    assert all(week['tasks'] for week in plan)
