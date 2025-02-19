from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image
import os
import json
import aiohttp
import re

@register("dalle3", "Your Name", "一个使用 DALL-E 3 生成图片的插件", "1.0.0")
class DallE3Plugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.api_endpoint = self.config.get("api_endpoint", "")
        self.default_size = "1024x1024"
        self.supported_sizes = ["1024x1024", "1792x1024", "1024x1792"]

    @filter.command("draw")
    async def draw(self, event: AstrMessageEvent, prompt: str, size: str = None):
        '''使用 DALL-E 3 生成图片
        
        Args:
            prompt(string): 图片描述提示词
            size(string): 图片尺寸,支持 1024x1024/1792x1024/1024x1792,默认1024x1024
        '''
        if not self.api_key or not self.api_endpoint:
            yield event.plain_result("请先在管理面板配置 Azure API Key 和 API 终端点")
            return

        # 验证尺寸
        if size and size not in self.supported_sizes:
            yield event.plain_result(f"不支持的尺寸: {size}\n支持的尺寸: {', '.join(self.supported_sizes)}")
            return

        yield event.plain_result("正在生成图片,请稍候...")
        
        try:
            image_url = await self._generate_image(prompt, size)
            if image_url:
                yield event.image_result(image_url)
            else:
                yield event.plain_result("图片生成失败")
        except Exception as e:
            logger.error(f"生成图片错误: {e}")
            yield event.plain_result(f"生成图片出错: {str(e)}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def auto_draw(self, event: AstrMessageEvent):
        '''自动检测画图意图并生成'''
        if not self.api_key or not self.api_endpoint:
            return
            
        message = event.message_str
        # 检测是否包含画图意图的关键词
        keywords = ["画", "生成图片", "画图", "绘制", "生成一张", "帮我画"]
        if any(keyword in message for keyword in keywords):
            # 移除命令词,提取描述内容
            for keyword in keywords:
                message = message.replace(keyword, "")
            
            # 尝试提取尺寸
            size = None
            for supported_size in self.supported_sizes:
                if supported_size in message:
                    size = supported_size
                    message = message.replace(supported_size, "")
                    break
            
            message = message.strip()
            if message:
                yield event.plain_result("检测到画图请求,正在生成...")
                try:
                    image_url = await self._generate_image(message, size)
                    if image_url:
                        yield event.image_result(image_url)
                    else:
                        yield event.plain_result("图片生成失败")
                except Exception as e:
                    logger.error(f"生成图片错误: {e}")
                    yield event.plain_result(f"生成图片出错: {str(e)}")

    async def _generate_image(self, prompt: str, size: str = None) -> str:
        '''调用 DALL-E 3 API 生成图片'''
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "prompt": prompt,
            "n": 1,
            "size": size or self.default_size
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_endpoint, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if "data" in result and len(result["data"]) > 0:
                        return result["data"][0]["url"]
                raise Exception(f"API 调用失败: {response.status} {await response.text()}")
