# ===== 코랩용 라이엇 API 내전 관리 시스템 =====

# 1. 필요한 라이브러리 설치
!pip install requests pandas matplotlib seaborn plotly streamlit

# 2. 라이브러리 import
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 3. 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("✅ 라이브러리 설치 및 import 완료!")
