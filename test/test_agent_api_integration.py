#!/usr/bin/env python3
"""Agent 调用后端 API 的集成测试。"""

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.agent import LabAgent


def read_env() -> dict[str, str]:
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')
    values: dict[str, str] = {}
    for line in (Path(__file__).resolve().parents[1] / '.env').read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            values[key] = value
    return values


def login(base_url: str, user_number: str, password: str) -> dict:
    url = (
        f"{base_url}/v1/user/login?userNumber={urllib.parse.quote(user_number)}"
        f"&password={urllib.parse.quote(password)}"
    )
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode('utf-8'))


def main() -> None:
    env = read_env()
    base_url = env.get('LAB_API_BASE_URL', 'http://localhost:8080')
    user_number = env['TEST_USER_NUMBER']
    password = env['TEST_PASSWORD']

    token_data = login(base_url, user_number, password)
    token = token_data['data']['tokenValue']

    auth_info = {
        'is_authenticated': True,
        'user_id': int(token_data['data']['loginId']),
        'user_number': user_number,
        'auth_token': token,
    }

    agent = LabAgent()
    session_id = 'agent-api-test-session'

    queries = [
        ('user_info', f'请调用接口获取学工号 {user_number} 的用户信息，并直接返回结果'),
        ('classroom_list', '请调用接口获取教室列表，页码1，每页10条，并直接返回结果'),
        ('room_names', '请调用接口获取所有房间名称，并直接返回结果'),
    ]

    for name, query in queries:
        print(f'\n=== {name} ===')
        print(f'QUERY: {query}')
        response = agent.run(query, session_id=session_id, auth_info=auth_info)
        print('RESPONSE:')
        print(response)


if __name__ == '__main__':
    main()
