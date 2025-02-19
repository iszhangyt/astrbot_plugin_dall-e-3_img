from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image
import os
import json
import aiohttp
import re

@register("dalle3", "moko", "一个使用 DALL-E 3 生成图片的插件", "1.0.0")
class DallE3Plugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.api_endpoint = self.config.get("api_endpoint", "")
        self.default_size = "1024x1024"
        self.size_mapping = {
            "方形": "1024x1024",
            "横版": "1792x1024",
            "竖版": "1024x1792"
        }
        self.supported_sizes = list(self.size_mapping.values())

    @filter.command("draw")
    async def draw(self, event: AstrMessageEvent, prompt: str, size: str = None):
        '''使用 DALL-E 3 生成图片
        
        Args:
            prompt(string): 图片描述提示词
            size(string): 图片尺寸,支持 方形/横版/竖版,或直接指定 1024x1024/1792x1024/1024x1792
        '''
        if not self.api_key or not self.api_endpoint:
            yield event.plain_result("请先在管理面板配置 Azure API Key 和 API 终端点")
            return

        # 验证并转换尺寸
        if size:
            size = self.size_mapping.get(size, size)
            if size not in self.supported_sizes:
                yield event.plain_result(f"不支持的尺寸: {size}，自动切换为默认尺寸\n支持的尺寸: 方形/横版/竖版 或 {', '.join(self.supported_sizes)}")
                return

        yield event.plain_result("检测到画图请求,正在调用 DALL-E 3 生成...")
        
        try:
            image_url = await self._generate_image(prompt, size)
            if image_url:
                yield event.image_result(image_url)
            else:
                yield event.plain_result("图片生成失败")
        except Exception as e:
            logger.error(f"生成图片错误: {e}")
            yield event.plain_result(f"生成图片出错: {str(e)}")

    @filter.llm_tool("dalle3_draw")
    async def dalle3_draw(self, event: AstrMessageEvent, prompt: str, size: str = None):
        '''使用 DALL-E 3 生成图片。当用户想要生成、绘制、画图时使用此工具。
        
        Args:
            prompt(string): 图片描述提示词,需要尽可能详细地描述用户想要的图片内容
            size(string): 图片尺寸,根据用户描述自动判断,支持 方形/横版/竖版,如果用户没有特别指定尺寸，则使用"方形"，不需要询问用户
        '''
        if not self.api_key or not self.api_endpoint:
            yield event.plain_result("请先在管理面板配置 Azure API Key 和 API 终端点")
            return

        # 验证并转换尺寸
        if size:
            size = self.size_mapping.get(size, size)
            if size not in self.supported_sizes:
                yield event.plain_result(f"不支持的尺寸: {size}，自动切换为默认尺寸\n支持的尺寸: 方形/横版/竖版 或 {', '.join(self.supported_sizes)}")
                return

        yield event.plain_result("检测到画图请求,正在调用 DALL-E 3 生成...")
        
        try:
            image_url = await self._generate_image(prompt, size)
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
