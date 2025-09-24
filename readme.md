# Keil Memory Analyzer

一个用于解析Keil MDK编译输出的内存占用信息的Python工具，提供直观的可视化分析报告。

## 功能特点

- ✅ 自动解析Keil编译输出的RAM和ROM使用情况
- ✅ 提取使用内存、剩余内存、使用率等关键指标
- ✅ 进度条可视化显示内存使用情况
- ✅ 简单易用的命令行接口


## 使用方法

### 基本语法

```shell
python keil_mem_analyzer.py <map_file> <flash_size_KB> <ram_size_KB>
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `<map_file>` | Keil生成的.map文件路径 | 
| `<flash_size_KB>` | 芯片的Flash总大小(KB) | 
| `<ram_size_KB>` | 芯片的RAM总大小(KB) | 

### 使用示例

#### Python脚本执行
```shell
python keil_mem_analyzer.py ./test.map 64 20
```

#### 可执行文件执行
```shell
.\dist\keil_mem_analyzer.exe .\test.map 64 20
```

### 输出示例
```
Analyzing: ./test.map
Flash (17.6/64.0 KB) (Free: 46.4 KB) [OK]   [########----------------------]  27.5%
RAM   ( 9.8/20.0 KB) (Free: 10.2 KB) [OK]   [##############----------------]  48.8%
```


## 项目结构

```
keil_memory_analyzer/
├── dist                   # 可执行文件夹
├── keil_mem_analyzer.py   # 主程序
├── test.map               # 测试用的map文件
└── README.md              # 说明文档
```

## 构建可执行文件

```shell
pip install pyinstaller
pyinstaller -F keil_mem_analyzer.py
```
