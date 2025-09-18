# 测试框架说明

## 目录结构

```
tests/
├── unit/                          # 单元测试
│   └── software/
│       └── terminal/
│           └── windows_terminal/
│               ├── test_fix_guid.py      # GUID修复工具测试
│               └── test_configs.py       # 测试配置文件数据
├── integration/                   # 集成测试（待添加）
├── functional/                    # 功能测试（待添加）
└── conftest.py                   # pytest配置（待添加）
```

## 运行测试

### 安装开发依赖
```bash
uv add --dev pytest pytest-cov
```

### 运行所有测试
```bash
python -m pytest
```

### 运行特定测试文件
```bash
python -m pytest tests/unit/software/terminal/windows_terminal/test_fix_guid.py -v
```

### 运行测试并生成覆盖率报告
```bash
python -m pytest --cov=multi_system tests/ -v
```

## 测试配置

### pytest配置 (pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### 开发依赖 (pyproject.toml)
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

## 测试用例说明

### Windows Terminal修复工具测试
- `test_analyze_config_no_issues`: 测试无问题的配置分析
- `test_analyze_config_duplicate_guids`: 测试重复GUID检测
- `test_analyze_config_missing_guids`: 测试缺失GUID检测  
- `test_analyze_config_duplicate_profiles`: 测试重复profile检测
- `test_fix_config_duplicate_guids`: 测试重复GUID修复
- `test_fix_config_missing_guids`: 测试缺失GUID修复
- `test_validate_config_file_not_found`: 测试文件不存在验证
- `test_fix_config_file_not_found`: 测试文件不存在修复

### 测试配置文件
`test_configs.py` 包含各种测试场景的配置数据：
- `VALID_CONFIG`: 正常配置
- `DUPLICATE_GUID_CONFIG`: 重复GUID配置
- `MISSING_GUID_CONFIG`: 缺失GUID配置
- `DUPLICATE_PROFILE_CONFIG`: 重复profile配置
- `MIXED_ISSUES_CONFIG`: 混合问题配置
- `REAL_WORLD_CONFIG`: 真实世界配置示例

## 最佳实践

1. **单元测试**: 每个功能模块都应该有对应的单元测试
2. **测试数据**: 使用独立的测试配置文件，避免污染真实数据
3. **覆盖率**: 定期运行覆盖率检查，确保测试完整性
4. **持续集成**: 建议配置CI/CD自动运行测试

## 添加新测试

1. 在相应的包目录下创建 `test_*.py` 文件
2. 遵循命名约定：`Test*` 类，`test_*` 方法
3. 使用 `pytest` 装饰器进行参数化或mock
4. 添加测试数据到 `test_configs.py` 或创建新的测试数据文件

## 注意事项

- 测试文件应该独立，不依赖外部环境
- 使用临时文件进行文件操作测试
- 使用mock来模拟外部依赖
- 确保测试的可重复性和稳定性