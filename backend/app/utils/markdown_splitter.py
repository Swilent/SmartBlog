import re
from typing import List


def split_markdown(content: str, title: str = "") -> List[str]:
    """
    将 Markdown 内容分割成语义完整的文本块

    规则：
    1. 按二级标题（##）分割大段落
    2. 若某段落 > 512 tokens，则按句子边界进一步切分
    3. 每个 chunk 附加标题上下文（如果有）
    """
    chunks = []

    # 预处理：统一换行符
    content = content.replace("\r\n", "\n")

    # 按二级标题分割
    # 使用正则表达式匹配 ## 开头的标题
    pattern = r"\n## (?=[^\n#])"
    sections = re.split(pattern, "\n" + content)

    # 第一个section可能是标题前的内容
    for i, section in enumerate(sections):
        if not section.strip():
            continue

        # 移除开头的换行符
        section = section.lstrip("\n")

        # 检查是否以标题开头（第一个section可能没有标题）
        lines = section.split("\n", 1)
        if len(lines) == 2 and section.startswith("##"):
            heading = lines[0].replace("##", "").strip()
            body = lines[1]
        else:
            heading = ""
            body = section

        # 构建带上下文的文本
        if heading:
            full_text = f"# {title}\n## {heading}\n{body}"
        else:
            full_text = f"# {title}\n{body}"

        # 简单估算 token 数（中文约 1 字符 = 1 token，英文约 4 字符 = 1 token）
        # 这里使用字符数/2 作为粗略估算
        estimated_tokens = len(full_text) // 2

        if estimated_tokens <= 512:
            chunks.append(full_text.strip())
        else:
            # 如果过长，按句子进一步分割
            sub_chunks = split_by_sentences(full_text.strip(), max_length=512)
            chunks.extend(sub_chunks)

    # 如果没有二级标题，整个内容作为一块
    if not chunks and content.strip():
        full_text = f"# {title}\n{content}"
        if len(full_text) // 2 <= 512:
            chunks.append(full_text.strip())
        else:
            chunks = split_by_sentences(full_text.strip(), max_length=512)

    return chunks


def split_by_sentences(text: str, max_length: int = 512) -> List[str]:
    """
    按句子边界分割文本，确保每块不超过指定长度
    """
    chunks = []
    current_chunk = ""

    # 按句子分割（中文句号、问号、感叹号，英文句号、问号、感叹号）
    # 使用更细粒度的分割
    sentences = re.split(r"([。！？.!?])", text)

    # 重新组合句子和标点
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i] + sentences[i + 1]

        # 估算 token 数
        estimated_tokens = (len(current_chunk) + len(sentence)) // 2

        if estimated_tokens <= max_length:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    # 添加最后一块
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
