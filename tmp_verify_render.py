from app import app

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    resp = client.get('/question/arrays-hashing/0')
    print(resp.status_code)
    body = resp.get_data(as_text=True)
    print('Execution Trace' in body)
    print('visualization-shell' in body)
