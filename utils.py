# utils.py
"""
通用辅助函数模块
"""
from config import HISTORY_LIMIT

def get_limited_msgs(msgs):
    """
    1. 永远保留 msgs[0:2] (第一轮完整对话)
    2. 截取最近的 (HISTORY_LIMIT - 1) 轮对话
    """
    if len(msgs) <= 2:
        return msgs
    
    first_round = msgs[:2]
    others = msgs[2:]
    
    lookback_count = (HISTORY_LIMIT - 1) * 2
    recent_msgs = others[-lookback_count:] if lookback_count > 0 else []
    
    return first_round + recent_msgs
