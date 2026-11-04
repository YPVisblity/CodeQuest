# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-2-level-3-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

from unittest.mock import patch, MagicMock
captured = {}
status = 200+user_id%4
url = f'https://example.com/student/{user_id}'
def fake_get(address,headers=None,**kwargs):
    captured.update(url=address,headers=headers or {})
    response = MagicMock()
    response.status_code = status
    return response
with patch('requests.get',side_effect=fake_get):
    result = fetch_with_header(url)
headers = captured.get('headers',{})
ua = headers.get('User-Agent','')
observe('status',result)
observe('requested_url',captured.get('url'))
observe('has_user_agent','User-Agent' in headers)
observe('browser_user_agent','python-requests' not in ua.lower() and any(word in ua.lower() for word in ['mozilla','chrome','safari','firefox','edge']))
