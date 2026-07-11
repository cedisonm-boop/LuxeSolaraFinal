import pytest
from app.domain.schemas import Rule
from app.services.qualification_engine import QualificationEngine, compare
@pytest.mark.parametrize('op,actual,expected', [('equals',1,1),('not_equals',1,2),('in','a',['a']),('not_in','b',['a']),('greater_than',2,1),('greater_than_or_equal',2,2),('less_than',1,2),('less_than_or_equal',2,2),('between',3,[1,4]),('contains',[1,2],1),('contains_any',[1,2],[2,3]),('contains_all',[1,2],[1,2]),('starts_with','abc','a'),('ends_with','abc','c')])
def test_compare(op, actual, expected): assert compare(actual, op, expected)
def test_nested_and_actions():
    rule=Rule(key='r',name='r',stage='fit_check',when={'all':[{'field':'a','operator':'equals','value':1},{'not':{'field':'b','operator':'equals','value':3}}]},then=[{'action':'add_score','category':'fit','value':5},{'action':'qualify_for_paid_audit'}])
    res=QualificationEngine().evaluate([rule], {'a':1,'b':2})
    assert res.score['fit']==5 and res.eligible_for_paid_audit
