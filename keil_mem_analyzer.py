#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os

class MapFileAnalyzer:
    def __init__(self, map_file_path, flash_size_kb, ram_size_kb):
        self.map_file_path = map_file_path
        self.flash_size_bytes = flash_size_kb * 1024
        self.ram_size_bytes = ram_size_kb * 1024
        self.rom_used = 0
        self.ram_used = 0
        
    def read_tail_lines(self, num_lines=30):
        """读取文件末尾的指定行数"""
        try:
            with open(self.map_file_path, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                
                avg_line_length = 100
                bytes_to_read = min(file_size, num_lines * avg_line_length + 1000)
                
                f.seek(max(0, file_size - bytes_to_read))
                data = f.read()
                
                try:
                    content = data.decode('utf-8')
                except UnicodeDecodeError:
                    content = data.decode('latin-1')
                
                lines = content.splitlines()
                return '\n'.join(lines[-num_lines:])
                
        except Exception as e:
            print(f"Read file failed: {e}")
            return ""
    
    def parse_map_file(self):
        """解析.map文件，提取存储使用数据"""
        try:
            content = self.read_tail_lines(10)
            
            if not content:
                print("File is empty or read failed")
                return False
            
            # 优先匹配精确格式
            rom_match = re.search(r'Total ROM\s+Size\s+\(Code\s+\+\s+RO Data+\+\s+RW Data\)\s+(\d+)\s+\(\s*([\d.]+)kB\)', content)
            ram_match = re.search(r'Total RW\s+Size\s+\(RW Data\s+\+\s+ZI Data\)\s+(\d+)\s+\(\s*([\d.]+)kB\)', content)

            # 如果失败，使用宽松匹配
            if not rom_match:
                rom_match = re.search(r'Total ROM\s+Size\s*\([^)]+\)\s*(\d+)\s*\(\s*([\d.]+)\s*kB\)', content)
            if not ram_match:
                ram_match = re.search(r'Total RW\s+Size\s*\([^)]+\)\s*(\d+)\s*\(\s*([\d.]+)\s*kB\)', content)
            
            if rom_match and ram_match:
                self.rom_used = int(rom_match.group(1))
                self.ram_used = int(ram_match.group(1))
                # print("Data extracted from summary section")
                return True
            else:
                print("No matching data format found in file tail")
            # 方法2: 匹配Grand Totals行的各段数据
            totals_match = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+).*Grand Totals', content)
            if totals_match:
                # 6个数据段，跳过第二个(inc. data)
                code = int(totals_match.group(1))      # Code
                # group(2) is inc. data - skip
                ro_data = int(totals_match.group(3))   # RO Data
                rw_data = int(totals_match.group(4))   # RW Data
                zi_data = int(totals_match.group(5))   # ZI Data
                # group(6) is Debug - skip
                
                self.rom_used = code + ro_data + rw_data  # Flash = Code + RO Data + RW Data
                self.ram_used = rw_data + zi_data         # RAM = RW Data + ZI Data
                # print("Data calculated from segment details")
                return True
            
            print("No matching data format found in file tail")
            return False
                
        except Exception as e:
            print(f"Parse file error: {e}")
            return False
    
    def calculate_usage(self):
        """计算存储空间使用率"""
        if self.rom_used == 0 and self.ram_used == 0:
            return None
        
        rom_usage_percent = (self.rom_used / self.flash_size_bytes) * 100 if self.flash_size_bytes > 0 else 0
        ram_usage_percent = (self.ram_used / self.ram_size_bytes) * 100 if self.ram_size_bytes > 0 else 0
        
        rom_free = max(0, self.flash_size_bytes - self.rom_used)
        ram_free = max(0, self.ram_size_bytes - self.ram_used)
        
        return {
            'rom_used_bytes': self.rom_used,
            'ram_used_bytes': self.ram_used,
            'rom_used_kb': self.rom_used / 1024,
            'ram_used_kb': self.ram_used / 1024,
            'rom_total_kb': self.flash_size_bytes / 1024,
            'ram_total_kb': self.ram_size_bytes / 1024,
            'rom_free_kb': rom_free / 1024,
            'ram_free_kb': ram_free / 1024,
            'rom_usage_percent': rom_usage_percent,
            'ram_usage_percent': ram_usage_percent
        }
    
    def print_usage_bar(self, label, used, total, free, percent):
        """打印使用率进度条"""
        bar_length = 30
        filled_length = int(bar_length * percent / 100)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        
        # 状态指示
        if percent > 90:
            status = "[HIGH]"
        elif percent > 80:
            status = "[WARN]"
        else:
            status = "[OK]  "
        
        # 横向输出
        print(f"{label:5} ({used:4.1f}/{total:4.1f} KB) (Free: {free:4.1f} KB) {status} [{bar}] {percent:5.1f}%")
        # 纵向输出
        # print(f"{label:5} ({used:.1f}/{total:.1f} KB) (Free: {free:.1f} KB) {status}")
        # print(f"[{bar}] {percent:5.1f}%")
    
    def generate_report(self, usage_data):
        """生成精简的使用率报告"""
        if not usage_data:
            print("Cannot generate report: no usage data available")
            return
        
        # 显示Flash使用情况
        self.print_usage_bar(
            "Flash",
            usage_data['rom_used_kb'],
            usage_data['rom_total_kb'],
            usage_data['rom_free_kb'],
            usage_data['rom_usage_percent']
        )
        
        # 显示RAM使用情况
        self.print_usage_bar(
            "RAM",
            usage_data['ram_used_kb'],
            usage_data['ram_total_kb'],
            usage_data['ram_free_kb'],
            usage_data['ram_usage_percent']
        )
        print()
        
        # 使用率总结
        # print("Usage Summary:")
        # print("-" * 40)
        # print(f"Flash: {usage_data['rom_usage_percent']:5.1f}% used, {usage_data['rom_free_kb']:5.1f} KB free")
        # print(f"RAM:   {usage_data['ram_usage_percent']:5.1f}% used, {usage_data['ram_free_kb']:5.1f} KB free")
        
        # 警告信息
        if usage_data['rom_usage_percent'] > 90:
            print("Warning: Flash usage exceeds 90% - consider optimization")
        elif usage_data['rom_usage_percent'] > 80:
            print("Note: Flash usage exceeds 80%")
        
        if usage_data['ram_usage_percent'] > 90:
            print("Warning: RAM usage exceeds 90% - risk of memory shortage")
        elif usage_data['ram_usage_percent'] > 80:
            print("Note: RAM usage exceeds 80%")
    
    def analyze(self):
        """执行完整分析"""
        print(f"Analyzing: {self.map_file_path}")
        
        if not self.parse_map_file():
            print("Failed to parse .map file")
            return False
            
        usage_data = self.calculate_usage()
        if usage_data:
            self.generate_report(usage_data)
            return True
        return False

def main():
    """主函数"""
    if len(sys.argv) != 4:
        print("Usage: python map_analyzer.py <map_file> <flash_size_KB> <ram_size_KB>")
        print("Example: python map_analyzer.py project.map 64 20")
        sys.exit(1)
    
    map_file = sys.argv[1]
    flash_size = int(sys.argv[2])
    ram_size = int(sys.argv[3])
    
    if not os.path.exists(map_file):
        print(f"Error: File {map_file} does not exist")
        sys.exit(1)
    
    analyzer = MapFileAnalyzer(map_file, flash_size, ram_size)
    analyzer.analyze()

if __name__ == "__main__":
    main()