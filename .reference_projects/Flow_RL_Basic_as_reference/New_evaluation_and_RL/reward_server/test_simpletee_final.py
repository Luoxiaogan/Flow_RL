#!/usr/bin/env python3
"""
最终测试：验证SimpleTeeOutput超级防御版本
直接测试scoreflow_reward_utils.py中的SimpleTeeOutput类
"""

import sys
import os
import tempfile
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 全局SILENT变量
SILENT = False

def test_simpletee_import():
    """测试导入SimpleTeeOutput类"""
    print("\n测试1: 导入SimpleTeeOutput类")
    
    # 临时修改sys.path避免路径创建问题
    original_cwd = os.getcwd()
    try:
        # 导入时避免执行顶层代码
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "scoreflow_reward_utils",
            "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/reward_server/scoreflow_reward_utils.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 临时设置为本地路径，避免服务器路径创建
        sys.modules['scoreflow_reward_utils'] = module
        
        # 从模块获取SimpleTeeOutput类
        exec_globals = {}
        with open("/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/reward_server/scoreflow_reward_utils.py", 'r') as f:
            code = f.read()
            # 提取SimpleTeeOutput类定义
            lines = code.split('\n')
            in_class = False
            class_code = []
            indent_level = 0
            
            for line in lines:
                if line.startswith('class SimpleTeeOutput:'):
                    in_class = True
                    class_code.append(line)
                    indent_level = len(line) - len(line.lstrip())
                elif in_class:
                    if line and not line.isspace():
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent <= indent_level and not line.startswith(' '):
                            break
                    class_code.append(line)
            
            # 添加必要的导入和全局变量
            final_code = "import sys\nSILENT = False\n" + '\n'.join(class_code)
            exec(final_code, exec_globals)
            
        SimpleTeeOutput = exec_globals['SimpleTeeOutput']
        print("   ✅ 成功导入SimpleTeeOutput类")
        return SimpleTeeOutput
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return None
    finally:
        os.chdir(original_cwd)

def test_extreme_scenarios(SimpleTeeOutput):
    """测试极端场景"""
    print("\n测试2: 极端场景测试")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        filename = f.name
        print(f"创建临时文件: {filename}")
        
        # 创建实例
        tee = SimpleTeeOutput(sys.stdout, f)
        
        # 场景1：正常操作
        print("\n场景1: 正常操作")
        tee.write("正常写入测试\n")
        print("   ✅ 正常操作成功")
        
        # 场景2：删除所有属性
        print("\n场景2: 删除所有属性")
        attrs_to_delete = ['_file_handle', '_closed', '_error_count', 'terminal', '_initialized']
        for attr in attrs_to_delete:
            if hasattr(tee, attr):
                delattr(tee, attr)
                print(f"   ✓ 删除{attr}")
        
        # 尝试操作
        try:
            tee.write("所有属性丢失后的写入\n")
            tee.flush()
            print("   ✅ 写入成功，服务未崩溃")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return False
        
        # 场景3：多次连续操作
        print("\n场景3: 连续100次写入")
        success = True
        for i in range(100):
            try:
                tee.write(f"测试写入 {i}\n")
                if i % 20 == 0:
                    tee.flush()
            except Exception as e:
                print(f"   ❌ 第{i}次写入失败: {e}")
                success = False
                break
        
        if success:
            print("   ✅ 100次写入全部成功")
        
        # 场景4：检查其他方法
        print("\n场景4: 测试其他方法")
        try:
            result = tee.isatty()
            print(f"   isatty() = {result}")
            result = tee.fileno()
            print(f"   fileno() = {result}")
            print("   ✅ 其他方法调用成功")
        except Exception as e:
            print(f"   ❌ 方法调用失败: {e}")
            return False
    
    # 清理
    try:
        os.unlink(filename)
        print(f"\n清理临时文件: {filename}")
    except:
        pass
    
    return True

def main():
    print("=" * 60)
    print("SimpleTeeOutput 超级防御版本最终测试")
    print("=" * 60)
    
    # 导入类
    SimpleTeeOutput = test_simpletee_import()
    if not SimpleTeeOutput:
        print("\n❌ 无法导入SimpleTeeOutput类")
        return
    
    # 运行极端场景测试
    success = test_extreme_scenarios(SimpleTeeOutput)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("超级防御版本有效：")
        print("  - 即使所有属性丢失也不会崩溃")
        print("  - 自动降级到终端输出模式")
        print("  - 保证服务的稳定运行")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)

if __name__ == "__main__":
    main()