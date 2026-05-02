# AI ClassHelper · AI 课本精读助手

> 大一学生个人项目 · Qwen + DeepSeek 双模型混合调用

## 功能

| 功能 | 模型 | 说明 |
|------|------|------|
| 📖 知识点提取 | 通义千问 | 每章核心概念、定义、公式 |
| 🖼 图表分析 | 通义千问 | 教材插图/流程图内容识别 |
| ✍️ 练习题生成 | DeepSeek | 选择题 + 简答题 + 答案 |
| 💻 代码示例 | DeepSeek | 代码/算法带注释示例 |
| 📕 期末速览 | 双模型 | 全书浓缩 3-5 页 |

## 快速开始

```bash
pip install -r requirements.txt
export DASHSCOPE_API_KEY="你的Key"
export DEEPSEEK_API_KEY="你的Key"
python reader.py 教材.pdf


      



Token 消耗（参考）


        

教材QwenDeepSeek总计15w左右

