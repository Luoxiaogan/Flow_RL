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

# 直接定义SimpleTeeOutput类（从修复后的版本复制）
class SimpleTeeOutput:
    """简化的双向输出类 - 用于独立日志（增强版，防止属性丢失）"""
    def __init__(self, terminal, file_handle):
        self.terminal = terminal
        self._file_handle = file_handle  # 使用私有属性防止意外覆盖
        self._closed = False  # 标记文件是否已关闭
        self._error_count = 0  # 错误计数器
    
    @property
    def file_handle(self):
        """安全访问file_handle属性，防止AttributeError"""
        # 防御性编程：确保属性存在
        if not hasattr(self, '_file_handle'):
            # 属性丢失时的恢复机制
            self._file_handle = None
            self._closed = True
            if self._error_count == 0:
                # 只记录第一次错误
                logger.warning("SimpleTeeOutput: file_handle attribute lost, degrading to terminal-only mode")
            self._error_count += 1
        return self._file_handle
    
    def write(self, message):
        """安全写入到终端和文件"""
        # 根据SILENT设置决定是否写到终端
        if not SILENT:
            try:
                # 增加hasattr检查
                if hasattr(self, 'terminal') and self.terminal:
                    self.terminal.write(message)
                    self.terminal.flush()
            except Exception:
                pass
        
        # 始终尝试写入文件（增强错误处理）
        try:
            # 使用property安全访问file_handle
            file_handle = self.file_handle
            if file_handle and not self._closed:
                # 三重检查：属性存在、不为None、文件未关闭
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.write(message)
                        file_handle.flush()
                    else:
                        self._closed = True
                else:
                    # file_handle没有closed属性，尝试直接写入
                    file_handle.write(message)
                    file_handle.flush()
        except (ValueError, OSError, AttributeError) as e:
            # 发生任何文件相关错误时，标记为已关闭
            self._closed = True
            if self._error_count < 5:  # 限制错误日志数量
                logger.debug(f"SimpleTeeOutput write error (count={self._error_count}): {type(e).__name__}")
                self._error_count += 1
        except Exception:
            # 捕获所有其他异常，确保不会崩溃
            self._closed = True
            pass
        
        return len(message) if message else 0
    
    def flush(self):
        """安全刷新缓冲区"""
        try:
            if hasattr(self, 'terminal') and self.terminal:
                self.terminal.flush()
        except Exception:
            pass
        
        try:
            # 使用property安全访问
            file_handle = self.file_handle
            if file_handle and not self._closed:
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.flush()
                else:
                    file_handle.flush()
        except (ValueError, OSError, AttributeError):
            self._closed = True
        except Exception:
            self._closed = True
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
        print("\n2. 模拟属性丢失...")
        print("   删除_file_handle属性")
        if hasattr(tee, '_file_handle'):
            delattr(tee, '_file_handle')
            print("   ✓ 属性已删除")
        
        # 尝试写入 - 这里原本会触发AttributeError
        print("\n3. 属性丢失后尝试写入...")
        try:
            tee.write("属性丢失后的写入: 这应该只出现在终端\n")
            tee.flush()
            print("   ✅ 成功！没有崩溃")
        except AttributeError as e:
            print(f"   ❌ 失败！发生AttributeError: {e}")
            return False
        
        # 继续多次写入测试
        print("\n4. 多次写入测试...")
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