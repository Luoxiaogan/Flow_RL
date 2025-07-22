1. 阅读`H100_config.out`的79~107 lines. 
2. 可以发现之所以120G的原因是保存了整个训练的状态.
3. 但是我只需要inference需要的权重即可
   1. 这里指的是：训练中间保存的checkpoint，以及训练完成的final的checkpoint都只保存inference需要的权重
4. 因此你需要修改`my_llama3_h100`里面的设置.