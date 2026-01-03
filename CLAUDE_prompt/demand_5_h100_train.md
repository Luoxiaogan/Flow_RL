接下来, 需要做的事情是:

参考`./my_llama3_full_finetune`里面对于A100的配置, 我需要写一份平行的对H100的配置in `./my_llama3_h100`, 我已经复制好了一份, 目前和A100的文件一样

要点:
1. H100相关的设置可以在`H100_config.out`里面读取
2. H100服务器的配置
+ llama地址: `/nas/models/Meta-Llama-3-8B-Instruct`
+ 数据盘文件存放在: `/nas/ganluo/sft_output` 