# utils.py
"""
Common utility functions module
"""
from config import HISTORY_LIMIT

def get_limited_msgs(msgs):
    """
    1. Always keep msgs[0:2] (the first full conversation round)
    2. Keep the most recent (HISTORY_LIMIT - 1) rounds of conversation
    """
    if len(msgs) <= 2:
        return msgs
    
    first_round = msgs[:2]
    others = msgs[2:]
    
    lookback_count = (HISTORY_LIMIT - 1) * 2
    recent_msgs = others[-lookback_count:] if lookback_count > 0 else []
    
    return first_round + recent_msgs
