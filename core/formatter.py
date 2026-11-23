import re

def format_for_wechat(text: str) -> str:
    """
    Format raw LLM/RAG markdown responses into clean Style A (方头括号 【 】) layout for WeChat.
    1. Removes redundant inline citations like [1], [2], [1, 2]
    2. Converts LaTeX formulas into standard Unicode math characters
    3. Replaces ### Markdown headers with 🔹 【Title】
    4. Replaces **bold** words with 【keyword】
    5. Normalizes lists and cleans up redundant colons and whitespace
    """
    # 1. Clean citation brackets
    cleaned = re.sub(r'\[\s*\d+(\s*,\s*\d+)*\s*\]', '', text)
    
    # 2. LaTeX symbol replacements
    cleaned = cleaned.replace(r'\times', '×')
    cleaned = cleaned.replace(r'\cdot', '·')
    cleaned = cleaned.replace(r'\dots', '...')
    cleaned = cleaned.replace(r'\ldots', '...')
    cleaned = cleaned.replace(r'\rightarrow', '→')
    cleaned = cleaned.replace(r'\leftarrow', '←')
    cleaned = cleaned.replace(r'\le', '≤')
    cleaned = cleaned.replace(r'\ge', '≥')
    cleaned = cleaned.replace(r'\approx', '≈')
    cleaned = cleaned.replace(r'\ne', '≠')
    cleaned = cleaned.replace(r'\pm', '±')
    cleaned = re.sub(r'\\text\{([^}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1 / \2)', cleaned)
    cleaned = re.sub(r'[$]+([^$]+)[$]+', r'\1', cleaned)
    
    # 3. Headers to Style A 【方头括号】
    def header_replace(m):
        num = m.group(1) or ""
        title = m.group(2).strip().strip('*').strip()
        if title.startswith('【') and title.endswith('】'):
            return f"\n🔹 {num}{title}"
        return f"\n🔹 {num}【{title}】"
        
    cleaned = re.sub(r'^###\s*(\d+[\.、]?\s*)?(.*)$', header_replace, cleaned, flags=re.MULTILINE)
    
    def h2_replace(m):
        title = m.group(1).strip().strip('*').strip()
        if title.startswith('【') and title.endswith('】'):
            return f"\n📌 {title}"
        return f"\n📌【{title}】"
        
    cleaned = re.sub(r'^##\s+(.*)$', h2_replace, cleaned, flags=re.MULTILINE)
    
    # 4. Convert all **bold** to 【bold】 (eliminating all raw asterisks)
    def bold_replace(m):
        inner = m.group(1).strip()
        if inner.startswith('【') and inner.endswith('】'):
            return inner
        return f"【{inner}】"
        
    cleaned = re.sub(r'\*\*(.*?)\*\*', bold_replace, cleaned)
    
    # 5. Standardize bullet points
    cleaned = re.sub(r'^\*\s{2,}', r'• ', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^\*\s+', r'• ', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^-\s+', r'• ', cleaned, flags=re.MULTILINE)
    
    # 6. Clean colons after brackets and normalize spacing
    cleaned = re.sub(r'【(.*?)】[：:]', r'【\1】 ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()

def split_message_chunks(text: str, max_bytes: int = 1800) -> list:
    """
    Split long messages into smaller chunks strictly adhering to WeChat's 2048-byte limit
    to completely prevent mid-sentence truncation.
    """
    utf8_bytes = len(text.encode('utf-8'))
    if utf8_bytes <= max_bytes:
        return [text]
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_bytes = 0
    
    for p in paragraphs:
        p_bytes = len((p + '\n\n').encode('utf-8'))
        if current_bytes + p_bytes > max_bytes and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [p]
            current_bytes = len(p.encode('utf-8'))
        else:
            current_chunk.append(p)
            current_bytes += p_bytes
            
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    if len(chunks) > 1:
        total = len(chunks)
        numbered_chunks = []
        for i, c in enumerate(chunks, 1):
            header = f"📄 (第 {i}/{total} 部分)\n\n"
            numbered_chunks.append(header + c)
        return numbered_chunks
        
    return chunks
