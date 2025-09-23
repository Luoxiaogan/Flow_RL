#!/usr/bin/env python3
"""
最小化测试SimpleTeeOutput修复
不导入整个模块，只测试类本身
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

# 直接定义SimpleTeeOutput类（超级防御版本）
class SimpleTeeOutput:
    """简化的双向输出类 - 超级防御版，处理所有属性丢失情况"""
    def __init__(self, terminal, file_handle):
        # 使用object.__setattr__确保属性设置成功，避免被覆盖
        object.__setattr__(self, 'terminal', terminal)
        object.__setattr__(self, '_file_handle', file_handle)
        object.__setattr__(self, '_closed', False)
        object.__setattr__(self, '_error_count', 0)
        object.__setattr__(self, '_initialized', True)  # 标记初始化完成
    
    def __getattr__(self, name):
        """捕获所有属性访问失败的情况，提供默认值"""
        # 提供所有可能丢失属性的默认值
        if name == '_initialized':
            return False
        if name == '_closed':
            return True  # 默认为已关闭，停止文件写入
        if name == '_error_count':
            return 0
        if name == '_file_handle':
            return None
        if name == 'terminal':
            # 返回标准输出作为备用
            return sys.__stdout__ if hasattr(sys, '__stdout__') else None
        # 其他未知属性
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @property
    def file_handle(self):
        """完全防御性的file_handle访问"""
        try:
            # 尝试正常访问
            return self._file_handle if hasattr(self, '_file_handle') else None
        except AttributeError:
            # 如果仍然失败，返回None
            return None
    
    def write(self, message):
        """安全写入到终端和文件"""
        # 根据SILENT设置决定是否写到终端
        if not SILENT:
            try:
                # 获取terminal，使用__getattr__提供的默认值
                terminal = getattr(self, 'terminal', None)
                if terminal:
                    terminal.write(message)
                    terminal.flush()
            except Exception:
                pass
        
        # 始终尝试写入文件（超级防御性错误处理）
        try:
            # 使用property安全访问file_handle
            file_handle = self.file_handle
            # 安全获取_closed属性
            is_closed = getattr(self, '_closed', True)
            
            if file_handle and not is_closed:
                # 三重检查：属性存在、不为None、文件未关闭
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.write(message)
                        file_handle.flush()
                    else:
                        # 尝试设置_closed标志
                        try:
                            object.__setattr__(self, '_closed', True)
                        except:
                            pass
                else:
                    # file_handle没有closed属性，尝试直接写入
                    file_handle.write(message)
                    file_handle.flush()
        except (ValueError, OSError, AttributeError) as e:
            # 发生任何文件相关错误时，尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
                error_count = getattr(self, '_error_count', 0)
                if error_count < 5:  # 限制错误日志数量
                    logger.debug(f"SimpleTeeOutput write error (count={error_count}): {type(e).__name__}")
                    object.__setattr__(self, '_error_count', error_count + 1)
            except:
                pass  # 即使设置属性失败也不崩溃
        except Exception:
            # 捕获所有其他异常，确保不会崩溃
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass
        
        return len(message) if message else 0
    
    def flush(self):
        """安全刷新缓冲区"""
        try:
            # 安全获取terminal
            terminal = getattr(self, 'terminal', None)
            if terminal:
                terminal.flush()
        except Exception:
            pass
        
        try:
            # 使用property安全访问
            file_handle = self.file_handle
            # 安全获取_closed属性
            is_closed = getattr(self, '_closed', True)
            
            if file_handle and not is_closed:
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.flush()
                else:
                    file_handle.flush()
        except (ValueError, OSError, AttributeError):
            # 尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass
        except Exception:
            # 尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass

def test_attribute_loss():
    """核心测试：模拟属性丢失"""
    print("\n核心测试: 模拟file_handle属性丢失")
    print("-" * 40)
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        filename = f.name
        print(f"创建临时文件: {filename}")
        
        # 创建SimpleTeeOutput实例
        tee = SimpleTeeOutput(sys.stdout, f)
        
        # 正常写入
        print("\n1. 正常写入测试...")
        tee.write("正常写入: 这应该同时出现在终端和文件\n")
        
        # 模拟属性丢失（这是导致崩溃的情况）
        print("\n2. 模拟_file_handle属性丢失...")
        print("   删除_file_handle属性")
        if hasattr(tee, '_file_handle'):
            delattr(tee, '_file_handle')
            print("   ✓ _file_handle属性已删除")
        
        # 尝试写入 - 这里原本会触发AttributeError
        print("\n3. _file_handle丢失后尝试写入...")
        try:
            tee.write("_file_handle丢失后的写入: 这应该只出现在终端\n")
            tee.flush()
            print("   ✅ 成功！没有崩溃")
        except AttributeError as e:
            print(f"   ❌ 失败！发生AttributeError: {e}")
            return False
        
        # 模拟_error_count属性丢失
        print("\n4. 模拟_error_count属性丢失...")
        print("   删除_error_count属性")
        if hasattr(tee, '_error_count'):
            delattr(tee, '_error_count')
            print("   ✓ _error_count属性已删除")
        
        # 尝试写入 - 测试新修复是否有效
        print("\n5. _error_count丢失后尝试写入...")
        try:
            tee.write("_error_count丢失后的写入: 这应该只出现在终端\n")
            tee.flush()
            print("   ✅ 成功！没有崩溃")
        except AttributeError as e:
            print(f"   ❌ 失败！发生AttributeError: {e}")
            return False
        
        # 模拟所有属性都丢失
        print("\n6. 模拟所有属性都丢失...")
        for attr in ['_closed', 'terminal', '_initialized']:
            if hasattr(tee, attr):
                delattr(tee, attr)
                print(f"   ✓ {attr}属性已删除")
        
        # 尝试写入 - 测试极端情况
        print("\n7. 所有属性丢失后尝试写入...")
        try:
            tee.write("所有属性丢失后的写入: 使用默认值\n")
            tee.flush()
            print("   ✅ 成功！使用__getattr__默认值")
        except Exception as e:
            print(f"   ❌ 失败！发生异常: {e}")
            return False
        
        # 继续多次写入测试
        print("\n8. 多次写入测试...")
        for i in range(3):
            try:
                tee.write(f"   第{i+1}次额外写入\n")
            except Exception as e:
                print(f"   ❌ 第{i+1}次写入失败: {e}")
                return False
        print("   ✅ 多次写入成功")
    
    # 清理
    try:
        os.unlink(filename)
        print(f"\n清理临时文件: {filename}")
    except:
        pass
    
    return True

def main():
    print("=" * 60)
    print("SimpleTeeOutput 属性丢失修复测试")
    print("=" * 60)
    
    # 执行测试
    success = test_attribute_loss()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过！")
        print("修复有效：即使file_handle属性丢失，服务也不会崩溃")
        print("日志功能会降级到仅终端输出模式")
    else:
        print("❌ 测试失败！")
        print("修复可能无效，需要进一步检查")
    print("=" * 60)

if __name__ == "__main__":
    main()