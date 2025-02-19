# AstrBot DALL-E 3 图片生成插件

基于 Azure OpenAI 的 DALL-E 3 模型实现的图片生成插件。支持命令和自然语言两种方式触发图片生成。

## ✨ 功能特点

1. 支持高质量的 AI 图片生成
2. 支持命令式调用和自然语言触发
3. 基于 Azure DALL-E 3 模型,生成效果优秀
4. 支持多种图片尺寸:
   - 方形: 1024x1024
   - 横版: 1792x1024
   - 竖版: 1024x1792

## 🚀 使用方法

### 1. 配置插件

在 AstrBot 管理面板中配置以下项目:
- Azure OpenAI API Key
- Azure DALL-E 3 API 终端点

### 2. 使用方式

#### 命令方式
使用 `/draw <提示词> [尺寸]` 生成图片,例如:

```
/draw 一只可爱的橘猫
/draw 一只可爱的橘猫 横版
```

#### 自然语言
直接对机器人说想要生成什么图片,例如:

```
帮我画一只可爱的橘猫
```

## 🔗 相关链接

- [AstrBot 官方文档](https://astrbot.app)
- [插件开发文档](https://astrbot.app/dev/plugin.html)
- [Azure OpenAI 服务](https://azure.microsoft.com/products/cognitive-services/openai-service)

