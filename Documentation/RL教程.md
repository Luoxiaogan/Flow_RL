## Internbootcamp RL流程

### 合成数据集
cd Test_FILE\verl_internbootcamp
python filter_and_generate_verl.py --output-dir dataset/xxx

## 配置config.json
Test_FILE\verl_internbootcamp\config.json修改此数据集

### 启动reward_server
export METAGPT_PROJECT_ROOT=项目根目录/metagpt_root
cd Test_FILE\verl_internbootcamp
python internbootcamp_reward_server.py

### 启动网关
cd ROOT_DIR
python api_key_proxy.py

### 启动RL
cd Test_FILE\verl_internbootcamp
修改里面的数据集等参数
bash test.sh

## Internbootcamp RL流程

### 合成数据集
cd Test_FILE\verl_internbootcamp
python filter_and_generate_verl.py --output-dir dataset/xxx

## 配置config.json
Test_FILE\verl_internbootcamp\config.json修改此数据集

### 启动reward_server
export METAGPT_PROJECT_ROOT=项目根目录/metagpt_root
cd Test_FILE\verl_internbootcamp
python internbootcamp_reward_server.py

### 启动网关
cd ROOT_DIR
python api_key_proxy.py

### 启动RL
cd Test_FILE\verl_internbootcamp
修改里面的数据集等参数
bash test.sh

## Internbootcamp RL流程

### 合成数据集
cd Test_FILE\verl_internbootcamp
python filter_and_generate_verl.py --output-dir dataset/xxx

## 配置config.json
Test_FILE\verl_internbootcamp\config.json修改此数据

### 启动reward_server
export METAGPT_PROJECT_ROOT=项目根目录/metagpt_root
cd Test_FILE\verl_internbootcamp
python internbootcamp_reward_server.py

### 启动网关
cd ROOT_DIR
python api_key_proxy.py

### 启动RL
cd Test_FILE\verl_internbootcamp
修改里面的数据集等参数
bash test.sh

## ScoreFlow RL流程

### 合成数据集
cd Test_FILE\verl_support
python generate_verl_training_data.py --num-train-entries 20 --num-test-entries 2 --output-dir data/xxxw --benchmarks all

## 配置config.json
Test_FILE\verl_support\config.json修改此数据

### 启动reward_server
export METAGPT_PROJECT_ROOT=项目根目录/metagpt_root
cd Test_FILE\verl_internbootcamp
python internbootcamp_reward_server.py

### 启动网关
cd ROOT_DIR
python api_key_proxy.py

### 启动RL
cd Test_FILE\verl_support
修改里面的数据集等参数
bash test.sh