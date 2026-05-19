# 贡献指南

感谢你对 LLM Arena 的兴趣！

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/Han-cy830/llm-arena/issues) 中搜索是否已有相同问题
2. 创建新 Issue，描述：
   - 你做了什么
   - 期望的结果
   - 实际的结果
   - 系统环境 (OS, Node.js 版本, Python 版本)

### 添加新供应商

1. Fork 本仓库
2. 编辑 `data/providers.json`，添加供应商配置：

```json
{
  "your-provider": {
    "display_name": "Your Provider",
    "base_url": "https://api.your-provider.com/v1",
    "default_model": "your-model",
    "models": ["your-model", "your-model-v2"],
    "api_type": "openai",
    "env_key": "YOUR_PROVIDER_API_KEY",
    "max_tokens": 4096,
    "supports_streaming": true
  }
}
```

3. 提交 PR

### 改进评分算法

评分算法在 `src/arena_v2.py` 中。如果你有更好的评分维度或权重建议，欢迎提 Issue 讨论或直接提 PR。

### 添加新成就

成就定义在 `src/arena_v2.py` 的 `ACHIEVEMENTS` 字典中。添加新成就：

1. 定义成就 ID、emoji、名称、描述
2. 在 `_check_achievements` 方法中添加检查逻辑
3. 提交 PR

## 开发环境

```bash
git clone https://github.com/Han-cy830/llm-arena.git
cd llm-arena
python src/cli.py help
```

## 行为准则

- 尊重所有贡献者
- 保持友好和建设性
- 不接受恶意代码或后门

## License

贡献的代码将使用 MIT License。
