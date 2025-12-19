import sys, json, re
try:
    data = json.load(sys.stdin)
    text = data.get('message', {}).get('content', '[No response]')
    # Strip markdown
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'^[#]+\s*', '', text, flags=re.M)
    text = re.sub(r'^[-*]\s+', '', text, flags=re.M)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.M)
    print(text.strip())
except:
    print('[Parse error]')
