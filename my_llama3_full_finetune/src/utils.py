# src/utils.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ModelArguments:
    """
    与模型和tokenizer相关的参数。
    """
    model_name_or_path: str = field(
        metadata={"help": "要训练或加载的模型的路径。"}
    )
    use_flash_attention_2: bool = field(
        default=True,
        metadata={"help": "是否使用Flash Attention 2来加速训练。"}
    )

@dataclass
class DataArguments:
    """
    与数据处理相关的参数。
    """
    dataset_path: str = field(
        metadata={"help": "训练数据集的路径。"}
    )
    max_seq_length: int = field(
        default=2048,
        metadata={"help": "输入模型的最大序列长度。"}
    )

@dataclass
class TrainingArguments(transformers.TrainingArguments):
    """
    继承自transformers的训练参数，可以添加自定义参数。
    """
    # 可以在这里添加自定义的训练参数
    pass