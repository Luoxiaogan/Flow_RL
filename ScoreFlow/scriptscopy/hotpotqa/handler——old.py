from typing import List, Dict, Any
# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HotpotqaHandler(BenchmarkHandler):
    """
    HotPotQA (Multi-hop Question Answering) 数据集的具体处理器。
    处理多文档推理问题，需要跨文档连接信息来回答问题。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
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
                answer = problem.get('answer', 'N/A')  # 答案可选
                supporting_facts = problem.get('supporting_facts', [])
                
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

**ANSWER:(in the testing of the workflow, this will not be provided to the workflow)**
{answer}

**SUPPORTING FACTS:(in the testing of the workflow, this will not be provided to the workflow)**
{supporting_facts}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotPotQA数据中提取问题时出错: {e}")
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题和相关文档，并格式化为清晰的文本用于工作流执行。
        
        注意：此方法用于实际执行阶段，提供完整的上下文文档，不进行截断。
        
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
                answer = problem.get('answer', 'N/A')  # 答案可选
                supporting_facts = problem.get('supporting_facts', [])
                
                # 提取并格式化上下文文档
                context = problem['context']
                titles = context['title']
                sentences_list = context['sentences']
                
                # 构建文档文本
                documents_text = "**CONTEXT DOCUMENTS:**\n\n"
                for i, (title, sentences) in enumerate(zip(titles, sentences_list), 1):
                    documents_text += f"Document {i}: {title}\n"
                    # 将句子列表合并为段落，保留完整内容供工作流执行使用
                    paragraph = ' '.join(sentences)
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
    
    def get_prompt_text_example(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题和相关文档，并格式化为清晰的文本用于生成工作流。
        每个样本中，**CONTEXT DOCUMENTS:** 部分（含换行符）总长度 ≤ 200 字。
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []

            for problem in problems:
                # 1. 提取原始数据
                question = problem['question']
                titles = problem['context']['title']
                sentences_list = problem['context']['sentences']

                # 2. 构造不超过 200 字的上下文
                header = "**CONTEXT DOCUMENTS:**\n\n"
                max_len = 350
                context_parts = [header]
                used = len(header)

                for idx, (title, sents) in enumerate(zip(titles, sentences_list), 1):
                    # 单文档文本块
                    title_line = f"Document {idx}: {title}\n"
                    body_text = ' '.join(sents) + "\n\n"
                    doc_block = title_line + body_text

                    # 如果加上这一段会超限，则截断并终止
                    if used + len(doc_block) > max_len:
                        # 如果连标题都放不下，直接舍弃
                        if used + len(title_line) > max_len:
                            break
                        # 只保留标题并补 [...]
                        context_parts.append(title_line + "[...]\n\n")
                        break

                    context_parts.append(doc_block)
                    used += len(doc_block)

                documents_text = ''.join(context_parts).rstrip()

                # 3. 组装最终样本
                formatted_problem = (
                    f"---\n{documents_text}\n\n**QUESTION:**\n{question}\n---"
                )
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