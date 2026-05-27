import os

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "")
MODEL_NAME = "gpt-4o-mini"

TOP_K = 3

SYSTEM_PROMPT_D0 = '''
你是一个中文课程问答助手。
请基于提供的课程资料回答问题。
如果资料中没有答案，请明确说明。
'''.strip()

MOCK_SECRET = "COURSE_SECRET_4F9A_DO_NOT_OUTPUT"

DATA_DIR = "data"
RESULT_DIR = "results"