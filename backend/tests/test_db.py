import pytest
from chat_microservice.db import get_db
import sqlite3

def test_get_and_close_db(app):
    with app.app_context():
        db = get_db()
        # test that the same db is returned between calls in the same context
        assert db is get_db()

    # assert that the connection to the db is not available outside of application context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    assert 'closed' in str(e.value)
    
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    
    def fake_init_db():
        # this treats the Recorder class like a namespace and assigns a value to recorder.called
        # for all intances of the recorder class
        Recorder.called = True
    
    monkeypatch.setattr("chat_microservice.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert 'Initialized' in result.output
    assert Recorder.called