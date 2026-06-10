import os
import sys
import subprocess

# Streamlit 설정
os.environ['STREAMLIT_BROWSER_GATHERUSERSTATS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# 표준 입력 비활성화
sys.stdin = open(os.devnull, 'r')

# Streamlit 실행
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'dashboard.py'])
