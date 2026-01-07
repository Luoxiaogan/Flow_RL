#!/usr/bin/env python3
"""
测试SimpleTeeOutput修复是否有效
模拟属性丢失的场景
"""

import sys
import os
import time
import tempfile

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scoreflow_reward_utils import SimpleTeeOutput

def test_normal_operation():
    """测试正常操作"""
    print("测试1: 正常操作")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        tee = SimpleTeeOutput(sys.stdout, f)
        tee.write("正常写入测试\n")
        tee.flush()
        print("✅ 正常操作测试通过")
        os.unlink(f.name)

def test_attribute_loss():
    """模拟属性丢失"""
    print("\n测试2: 模拟属性丢失")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        tee = SimpleTeeOutput(sys.stdout, f)
        
        # 模拟属性丢失
        print("模拟删除_file_handle属性...")
        if hasattr(tee, '_file_handle'):
            delattr(tee, '_file_handle')
        
        # 尝试写入（应该不会崩溃）
        try:
            tee.write("属性丢失后的写入测试\n")
            tee.flush()
            print("✅ 属性丢失测试通过 - 服务没有崩溃")
        except AttributeError as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            os.unlink(f.name)
    return True

def test_closed_file():
    """测试文件已关闭的情况"""
    print("\n测试3: 文件已关闭")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        filename = f.name
        tee = SimpleTeeOutput(sys.stdout, f)
        
        # 关闭文件
        f.close()
        
        # 尝试写入（应该不会崩溃）
        try:
            tee.write("文件关闭后的写入测试\n")
            tee.flush()
            print("✅ 文件关闭测试通过 - 服务没有崩溃")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            os.unlink(filename)
    return True

def test_multiple_errors():
    """测试多次错误"""
    print("\n测试4: 多次错误处理")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        filename = f.name
        tee = SimpleTeeOutput(sys.stdout, f)
        
        # 删除属性并尝试多次写入
        if hasattr(tee, '_file_handle'):
            delattr(tee, '_file_handle')
        
        success = True
        for i in range(10):
            try:
                tee.write(f"第{i+1}次写入测试\n")
                tee.flush()
            except Exception as e:
                print(f"❌ 第{i+1}次写入失败: {e}")
                success = False
                break
        
        if success:
            print("✅ 多次错误处理测试通过")
        
        os.unlink(filename)
        return success

def main():
    print("="*60)
    print("SimpleTeeOutput修复测试")
    print("="*60)
    
    tests = [
        test_normal_operation,
        test_attribute_loss,
        test_closed_file,
        test_multiple_errors
    ]
    
    all_passed = True
    for test in tests:
        try:
            result = test()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 所有测试通过！修复有效")
    else:
        print("❌ 部分测试失败，需要进一步检查")
    print("="*60)

if __name__ == "__main__":
    main()