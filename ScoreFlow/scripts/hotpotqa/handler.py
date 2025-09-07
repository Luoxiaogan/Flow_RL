from typing import List, Dict, Any
# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HotpotqaHandler(BenchmarkHandler):
    """
    HotPotQA (Multi-hop Question Answering) 数据集的具体处理器。
    处理多文档推理问题，需要跨文档连接信息来回答问题。
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题和相关文档，并格式化为清晰的文本用于生成工作流。
        格式:
        ---
        **QUESTION:**
        [question text]
        
        **CONTEXT DOCUMENTS:**
        Document 1: [Title]
        [sentences]
        
        Document 2: [Title]
        [sentences]
        ...
        ---
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题
                question = problem['question']
                
                # 提取并格式化上下文文档
                context = problem['context']
                titles = context['title']
                sentences_list = context['sentences']
                
                # 构建文档文本
                documents_text = "**CONTEXT DOCUMENTS:**\n\n"
                for i, (title, sentences) in enumerate(zip(titles, sentences_list), 1):
                    documents_text += f"Document {i}: {title}\n"
                    # 将句子列表合并为段落
                    paragraph = ' '.join(sentences)
                    
                    # 智能截断：如果段落超过200字
                    if len(paragraph) > 200:
                        # 在200字符内找到最后一个合适的截断点（句号、空格等）
                        truncate_pos = 200
                        
                        # 优先在句号处截断
                        last_period = paragraph[:200].rfind('.')
                        if last_period > 100:  # 如果句号位置合理（至少保留100字符）
                            truncate_pos = last_period + 1
                        else:
                            # 其次在空格处截断
                            last_space = paragraph[:200].rfind(' ')
                            if last_space > 100:
                                truncate_pos = last_space
                        
                        paragraph = paragraph[:truncate_pos].strip() + "... [too long, truncated.]"
                    
                    documents_text += f"{paragraph}\n\n"
                
                # 组合问题和文档
                formatted_problem = f"""---
{documents_text.strip()}

**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotPotQA数据中提取问题时出错: {e}")
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 HotPotQA 问题的完整数据，用于后续的执行和验证。
        这包括问题、上下文文档、答案、支持事实等信息。
        """
        return self._get_problem_by_index(index)
    
    # judge方法继承自基类，使用LLM进行智能判断
    # 如果需要特殊处理，可以覆盖该方法