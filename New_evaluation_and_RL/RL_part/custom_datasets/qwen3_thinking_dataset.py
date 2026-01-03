"""
Qwen3 Thinking数据集类
用于VERL训练框架，确保Qwen3的thinking模式被正确启用

这个类的核心作用：
1. 继承VERL的标准数据集类RLHFDataset
2. 重写关键方法以确保tokenizer正确应用thinking模式
3. 提供详细的日志记录以便调试和验证

作者：Flow_RL项目组
创建日期：2024-01
"""

import logging
from typing import List, Dict, Any, Optional
from verl.utils.dataset.rl_dataset import RLHFDataset
import torch

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Qwen3ThinkingDataset(RLHFDataset):
    """
    专门为Qwen3 thinking模式定制的数据集类
    
    这个类确保在VERL训练过程中：
    1. Tokenizer的chat template被正确应用
    2. enable_thinking参数被正确传递
    3. Thinking标记（<think>和</think>）被正确处理
    """
    
    def __init__(self, *args, **kwargs):
        """
        初始化数据集并验证thinking模式配置
        
        在初始化时，我们会：
        1. 调用父类的初始化方法
        2. 检查tokenizer是否包含thinking相关的特殊token
        3. 记录配置信息以便调试
        """
        # 调用父类初始化
        super().__init__(*args, **kwargs)
        
        # 初始化计数器用于日志记录
        self._sample_counter = 0
        self._thinking_samples_found = 0
        
        # 验证tokenizer配置
        self._validate_tokenizer_thinking_support()
        
        # 记录数据集配置信息
        logger.info("=" * 60)
        logger.info("Qwen3 Thinking数据集初始化成功")
        logger.info(f"数据文件数量: {len(self.data_files) if hasattr(self, 'data_files') else 'N/A'}")
        logger.info(f"最大prompt长度: {self.config.get('max_prompt_length', 'N/A')}")
        logger.info(f"最大响应长度: {self.config.get('max_response_length', 'N/A')}")
        logger.info("=" * 60)
        logger.info(f"Tokenizer model_max_length: {self.tokenizer.model_max_length}")
        logger.info(f"Config max_prompt_length: {self.config.get('max_prompt_length')}")
        logger.info(f"实际使用: {self.config.get('max_prompt_length', 8192)}")
        logger.info("=" * 60)
    
    def _validate_tokenizer_thinking_support(self):
        """
        验证tokenizer是否支持thinking模式
        
        这个方法检查：
        1. Tokenizer是否包含thinking相关的特殊token
        2. Chat template是否包含thinking逻辑
        3. Token ID映射是否正确
        """
        try:
            # 检查是否有thinking相关的特殊token
            if hasattr(self.tokenizer, 'added_tokens_decoder'):
                thinking_tokens = {}
                for token_id, token_info in self.tokenizer.added_tokens_decoder.items():
                    if hasattr(token_info, 'content'):
                        if '<think>' in token_info.content:
                            thinking_tokens['think_start'] = (token_id, token_info.content)
                        elif '</think>' in token_info.content:
                            thinking_tokens['think_end'] = (token_id, token_info.content)
                
                if thinking_tokens:
                    logger.info("✅ Thinking模式支持验证通过:")
                    for key, (token_id, content) in thinking_tokens.items():
                        logger.info(f"  - {key}: ID={token_id}, 内容='{content}'")
                else:
                    logger.warning("⚠️ 未检测到thinking特殊token，请检查tokenizer配置")
            
            # 检查chat template是否包含thinking逻辑
            if hasattr(self.tokenizer, 'chat_template'):
                if 'enable_thinking' in str(self.tokenizer.chat_template):
                    logger.info("✅ Chat template包含enable_thinking逻辑")
                else:
                    logger.warning("⚠️ Chat template可能不支持enable_thinking参数")
                    
        except Exception as e:
            logger.error(f"验证tokenizer时发生错误: {e}")
    
    def preprocess_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        预处理对话消息，确保thinking模式被启用
        
        参数:
            messages: 对话消息列表，每个消息包含role和content
            
        返回:
            str: 应用chat template后的文本
            
        这个方法是确保thinking模式工作的核心
        """
        # 应用chat template，显式启用thinking
        # 注意：根据Qwen3的chat template，不传enable_thinking或传True都会启用thinking
        # 只有显式传False才会禁用thinking
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True  # 显式启用thinking模式
        )
        
        # 记录前几个样本以验证处理是否正确
        self._sample_counter += 1
        if self._sample_counter <= 5:  # 只记录前5个样本
            logger.info(f"\n样本 {self._sample_counter} 处理完成")
            logger.info(f"消息数量: {len(messages)}")
            logger.info(f"处理后文本长度: {len(text)}")
            
            # 检查是否包含thinking标记
            if '<think>' in text or '</think>' in text:
                logger.info("✅ 检测到thinking标记")
                self._thinking_samples_found += 1
            else:
                logger.info("ℹ️ 此样本未检测到thinking标记（可能是正常的）")
            
            # 显示文本的前200个字符用于调试
            preview = text[:200] + "..." if len(text) > 200 else text
            logger.debug(f"文本预览: {preview}")
        
        return text
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """
        获取单个数据项
        
        参数:
            index: 数据索引
            
        返回:
            Dict: 包含input_ids、attention_mask等的字典
            
        这个方法被DataLoader调用来构建批次
        """
        # 首先获取原始数据项
        raw_item = self.data[index] if hasattr(self, 'data') else {}
        
        # 处理消息
        if 'messages' in raw_item:
            messages = raw_item['messages']
            
            # 应用我们的预处理
            processed_text = self.preprocess_conversation(messages)
            
            # 进行tokenization
            encoded = self.tokenizer(
                processed_text,
                truncation=True, # 强制截断到max_length, 但是其实会先过一遍VERL层, 然后才到dataset层.
                max_length=self.config.get('max_prompt_length', 8192),
                padding='max_length',
                return_tensors='pt'
            )
            
            # 构建返回的数据项
            item = {
                'input_ids': encoded['input_ids'].squeeze(0),
                'attention_mask': encoded['attention_mask'].squeeze(0),
                'messages': messages,  # 保留原始消息用于调试
                'processed_text': processed_text  # 保留处理后的文本
            }
            
            # 如果有其他需要的字段，从原始数据复制
            for key in ['reward', 'response', 'prompt']:
                if key in raw_item:
                    item[key] = raw_item[key]
            
            return item
        else:
            # 如果没有messages字段，调用父类方法
            return super().__getitem__(index)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据集统计信息
        
        返回:
            Dict: 包含各种统计信息的字典
            
        这个方法可以用于监控和调试
        """
        stats = {
            'total_samples': len(self) if hasattr(self, '__len__') else 'N/A',
            'samples_processed': self._sample_counter,
            'thinking_samples_found': self._thinking_samples_found,
            'thinking_detection_rate': (
                f"{self._thinking_samples_found / max(self._sample_counter, 1) * 100:.1f}%"
                if self._sample_counter > 0 else "N/A"
            )
        }
        
        logger.info("\n数据集统计信息:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        return stats


# 用于测试的辅助函数
def test_dataset_initialization():
    """
    测试数据集是否能正确初始化
    
    这个函数可以单独运行来验证实现是否正确
    """
    from transformers import AutoTokenizer
    
    try:
        # 加载Qwen3 tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            "/nas/models/Qwen3-8B",
            trust_remote_code=True
        )
        
        # 创建测试配置
        test_config = {
            'max_prompt_length': 8192,
            'max_response_length': 8192,
            'train_batch_size': 1
        }
        
        # 创建测试数据
        test_data = [{
            'messages': [
                {'role': 'user', 'content': '请解决这个数学问题：2+2等于多少？'}
            ]
        }]
        
        # 初始化数据集
        dataset = Qwen3ThinkingDataset(
            data_files=None,
            tokenizer=tokenizer,
            processor=None,
            config=test_config
        )
        
        # 设置测试数据
        dataset.data = test_data
        
        # 测试获取一个数据项
        item = dataset[0]
        
        logger.info("✅ 数据集测试通过")
        logger.info(f"返回项的键: {item.keys()}")
        
        # 获取统计信息
        dataset.get_statistics()
        
    except Exception as e:
        logger.error(f"❌ 数据集测试失败: {e}")
        raise


if __name__ == "__main__":
    # 如果直接运行这个文件，执行测试
    test_dataset_initialization()