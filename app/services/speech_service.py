# app/services/speech_service.py

"""
语音处理服务模块
提供语音转文字和文字转语音功能
"""

import logging
import tempfile
import os
from typing import Optional, Dict, Any
from fastapi import UploadFile

# 配置日志
logger = logging.getLogger(__name__)

# 模拟语音转文字服务
class SpeechToTextService:
    """语音转文字服务"""
    
    def __init__(self):
        """初始化语音转文字服务"""
        # 这里可以初始化真实的语音识别服务，如Whisper、Azure Speech等
        self.service_type = "mock"  # mock, whisper, azure
        logger.info(f"语音转文字服务初始化完成，使用服务类型: {self.service_type}")
    
    async def convert(self, audio_file: UploadFile, language: str = "zh-CN") -> Dict[str, Any]:
        """
        将语音转换为文字
        
        Args:
            audio_file: 音频文件
            language: 语言代码，默认为中文
            
        Returns:
            dict: 包含转换结果的字典
                - text: 转换后的文字
                - confidence: 置信度
                - duration: 音频时长
        """
        try:
            logger.info(f"开始语音转文字处理，文件: {audio_file.filename}, 语言: {language}")
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                content = await audio_file.read()
                temp.write(content)
                temp_path = temp.name
            
            try:
                # 根据服务类型选择不同的处理逻辑
                if self.service_type == "whisper":
                    # 使用Whisper进行语音识别
                    result = await self._whisper_speech_to_text(temp_path, language)
                elif self.service_type == "azure":
                    # 使用Azure Speech进行语音识别
                    result = await self._azure_speech_to_text(temp_path, language)
                else:
                    # 使用模拟数据
                    result = await self._mock_speech_to_text(temp_path, language)
                
                logger.info(f"语音转文字成功，识别结果: {result['text'][:50]}...")
                return result
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except Exception as e:
            logger.error(f"语音转文字失败: {str(e)}")
            raise
    
    async def _mock_speech_to_text(self, audio_path: str, language: str) -> Dict[str, Any]:
        """模拟语音转文字"""
        # 模拟语音识别延迟
        import asyncio
        await asyncio.sleep(0.5)
        
        # 模拟识别结果
        mock_results = [
            "我觉得大学生应该多参加实习，积累工作经验。",
            "职业规划很重要，需要提前了解自己的兴趣和能力。",
            "我希望毕业后能进入互联网公司工作。",
            "我对人工智能领域很感兴趣，正在学习相关知识。",
            "我认为在校期间应该多学习专业知识，同时培养软实力。"
        ]
        
        import random
        return {
            "text": random.choice(mock_results),
            "confidence": round(random.uniform(0.8, 0.99), 2),
            "duration": round(random.uniform(2, 8), 2)
        }
    
    async def _whisper_speech_to_text(self, audio_path: str, language: str) -> Dict[str, Any]:
        """使用Whisper进行语音识别"""
        # 这里可以集成OpenAI Whisper或本地Whisper模型
        # 示例：使用openai-whisper库
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language=language)
            
            return {
                "text": result["text"].strip(),
                "confidence": 0.95,  # Whisper不直接返回置信度
                "duration": result["duration"]
            }
        except ImportError:
            logger.error("未安装whisper库，无法使用Whisper语音识别")
            # 回退到模拟数据
            return await self._mock_speech_to_text(audio_path, language)
    
    async def _azure_speech_to_text(self, audio_path: str, language: str) -> Dict[str, Any]:
        """使用Azure Speech进行语音识别"""
        # 这里可以集成Azure Speech Service
        # 示例：使用azure-cognitiveservices-speech库
        return await self._mock_speech_to_text(audio_path, language)

# 模拟文字转语音服务
class TextToSpeechService:
    """文字转语音服务"""
    
    def __init__(self):
        """初始化文字转语音服务"""
        # 语言风格到音色的映射配置
        self.style_to_voice = {
            "专业严谨": {
                "voice": "professor",
                "speed": 0.9,   # 稍慢，体现专业
                "pitch": 0.9,   # 稍低，体现稳重
                "volume": 0.85, # 适中，体现专业
                "description": "专业严谨的音色配置"
            },
            "亲切友善": {
                "voice": "assistant",
                "speed": 1.0,   # 正常语速
                "pitch": 1.1,   # 稍高，体现亲切
                "volume": 0.9,  # 稍大，体现热情
                "description": "亲切友善的音色配置"
            },
            "轻松活泼": {
                "voice": "student",
                "speed": 1.1,   # 稍快，体现活泼
                "pitch": 1.2,   # 较高，体现活力
                "volume": 0.95, # 较大，体现热情
                "description": "轻松活泼的音色配置"
            },
            "理性客观": {
                "voice": "manager",
                "speed": 0.95,  # 稍慢，体现理性
                "pitch": 1.0,   # 正常音调
                "volume": 0.8,  # 稍低，体现客观
                "description": "理性客观的音色配置"
            }
        }
        
        # 角色音色映射配置
        self.voice_mapping = {
            "default": {"name": "default", "description": "默认语音"},
            "professor": {"name": "zh-CN-YunxiNeural", "description": "教授/导师 - 沉稳专业"},
            "student": {"name": "zh-CN-YunxiaNeural", "description": "学生 - 活泼年轻"},
            "manager": {"name": "zh-CN-YunyangNeural", "description": "经理 - 自信干练"},
            "assistant": {"name": "zh-CN-YunyangNeural", "description": "助手 - 亲切友好"}
        }
        
        # 使用开源免费的edge-tts进行语音合成
        self.service_type = "edge-tts"  # mock, pyttsx3, azure, edge-tts
        logger.info(f"文字转语音服务初始化完成，使用服务类型: {self.service_type}")
    
    async def convert(self, text: str, language: str = "zh-CN", voice: str = "default", 
                     speed: float = None, pitch: float = None, volume: float = None,
                     language_style: str = None) -> Dict[str, Any]:
        """
        将文字转换为语音
        
        Args:
            text: 要转换的文字
            language: 语言代码，默认为中文
            voice: 语音类型/角色，默认为default
            speed: 语速，范围0.5-2.0，默认为None（根据语言风格自动设置）
            pitch: 音调，范围0.5-2.0，默认为None（根据语言风格自动设置）
            volume: 音量，范围0.0-1.0，默认为None（根据语言风格自动设置）
            language_style: 语言风格，可选值：专业严谨、亲切友善、轻松活泼、理性客观
            
        Returns:
            dict: 包含转换结果的字典
                - audio_data: 音频数据（base64编码）
                - format: 音频格式
                - duration: 音频时长
                - voice_used: 实际使用的语音
                - style_config: 实际使用的风格配置
        """
        try:
            # 根据语言风格自动设置音色参数
            style_config = {}
            if language_style and language_style in self.style_to_voice:
                style_config = self.style_to_voice[language_style]
                # 如果用户没有指定具体参数，则使用语言风格对应的参数
                if speed is None:
                    speed = style_config["speed"]
                if pitch is None:
                    pitch = style_config["pitch"]
                if volume is None:
                    volume = style_config["volume"]
                if voice == "default":
                    voice = style_config["voice"]
            
            # 获取实际使用的语音配置
            actual_voice = self.voice_mapping.get(voice, self.voice_mapping["default"])["name"]
            
            # 确保使用有效的edge-tts voice name，如果是default，使用一个默认的中文语音
            if actual_voice == "default":
                actual_voice = "zh-CN-YunxiNeural"  # 使用默认的中文语音
            
            logger.info(f"开始文字转语音处理，文本: {text[:50]}..., 语音: {actual_voice}, 风格: {language_style}, "
                      f"语速: {speed}, 音调: {pitch}, 音量: {volume}")
            
            # 为None的参数设置默认值
            if speed is None:
                speed = 1.0
            if pitch is None:
                pitch = 1.0
            if volume is None:
                volume = 1.0
            
            # 根据服务类型选择不同的处理逻辑
            if self.service_type == "pyttsx3":
                # 使用pyttsx3进行语音合成
                result = await self._pyttsx3_text_to_speech(text, language, actual_voice, speed, pitch, volume)
            elif self.service_type == "azure":
                # 使用Azure Speech进行语音合成
                result = await self._azure_text_to_speech(text, language, actual_voice, speed, pitch, volume)
            elif self.service_type == "edge-tts":
                # 使用Edge TTS进行语音合成
                result = await self._edge_tts_to_speech(text, language, actual_voice, speed, pitch, volume)
            else:
                # 使用模拟数据
                result = await self._mock_text_to_speech(text, language, actual_voice, speed, pitch, volume)
            
            # 添加实际使用的语音信息和风格配置
            result["voice_used"] = actual_voice
            result["style_config"] = style_config
            
            logger.info(f"文字转语音成功，音频时长: {result['duration']}秒，使用语音: {actual_voice}")
            return result
        except Exception as e:
            logger.error(f"文字转语音失败: {str(e)}")
            raise
    
    async def _mock_text_to_speech(self, text: str, language: str, voice: str, 
                                  speed: float = 1.0, pitch: float = 1.0, volume: float = 1.0) -> Dict[str, Any]:
        """模拟文字转语音"""
        # 模拟语音合成延迟
        import asyncio
        await asyncio.sleep(0.5)
        
        # 模拟生成音频数据（实际应该是真实的音频数据）
        # 这里使用空的base64编码字符串作为示例
        import base64
        
        # 根据语速计算模拟时长
        duration = max(1.0, len(text) / (150 * speed) * 60)
        
        return {
            "audio_data": base64.b64encode(b"").decode("utf-8"),  # 空的base64字符串
            "format": "wav",
            "duration": round(duration, 2)
        }
    
    async def _pyttsx3_text_to_speech(self, text: str, language: str, voice: str, 
                                    speed: float = 1.0, pitch: float = 1.0, volume: float = 1.0) -> Dict[str, Any]:
        """使用pyttsx3进行文字转语音"""
        # 示例：使用pyttsx3库
        try:
            import pyttsx3
            import tempfile
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                temp_path = temp.name
            
            # 初始化pyttsx3引擎
            engine = pyttsx3.init()
            
            # 设置属性
            engine.setProperty('rate', int(150 * speed))  # 语速调整
            engine.setProperty('volume', volume)  # 音量调整
            
            # 设置语音（支持更多语音选择）
            voices = engine.getProperty('voices')
            
            # 尝试匹配语音
            selected_voice = None
            for v in voices:
                # 支持按名称或ID匹配
                if voice in v.id or voice.lower() in v.name.lower():
                    selected_voice = v.id
                    break
            
            # 如果没有匹配到，使用第一个中文语音
            if not selected_voice:
                for v in voices:
                    if 'chinese' in v.id.lower() or 'zh' in v.id.lower():
                        selected_voice = v.id
                        break
            
            # 如果还是没有，使用默认语音
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            
            # 保存音频文件
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # 读取音频数据
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            # 清理临时文件
            os.unlink(temp_path)
            
            # 计算时长（简化处理）
            duration = max(1.0, len(text) / (150 * speed) * 60)
            
            return {
                "audio_data": base64.b64encode(audio_data).decode("utf-8"),
                "format": "wav",
                "duration": round(duration, 2)
            }
        except ImportError:
            logger.error("未安装pyttsx3库，无法使用pyttsx3语音合成")
            # 回退到模拟数据
            return await self._mock_text_to_speech(text, language, voice, speed, pitch, volume)
    
    async def _azure_text_to_speech(self, text: str, language: str, voice: str, 
                                  speed: float = 1.0, pitch: float = 1.0, volume: float = 1.0) -> Dict[str, Any]:
        """使用Azure Speech进行语音合成"""
        # 这里可以集成Azure Speech Service
        # 示例：使用azure-cognitiveservices-speech库
        return await self._mock_text_to_speech(text, language, voice, speed, pitch, volume)
    
    async def _edge_tts_to_speech(self, text: str, language: str, voice: str, 
                                speed: float = 1.0, pitch: float = 1.0, volume: float = 1.0) -> Dict[str, Any]:
        """使用Edge TTS进行语音合成"""
        # 示例：使用edge-tts库
        try:
            import edge_tts
            import tempfile
            import asyncio
            import base64
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                temp_path = temp.name
            
            # 计算语速、音调和音量参数，确保使用edge-tts接受的值
            # edge-tts不接受0%，需要使用默认值
            speed_percentage = int((speed - 1.0) * 100)
            pitch_percentage = int((pitch - 1.0) * 100)
            volume_percentage = int((volume - 1.0) * 100)
            
            # 构建Edge TTS参数，只在非0时传递
            edge_tts_args = {
                'text': text,
                'voice': voice
            }
            
            # 只有当百分比不为0时才添加参数，否则使用默认值
            if speed_percentage != 0:
                edge_tts_args['rate'] = f"{speed_percentage}%"
            if pitch_percentage != 0:
                edge_tts_args['pitch'] = f"{pitch_percentage}Hz"
            if volume_percentage != 0:
                edge_tts_args['volume'] = f"{volume_percentage}%"
            
            # 构建Edge TTS参数
            communicate = edge_tts.Communicate(**edge_tts_args)
            await communicate.save(temp_path)
            
            # 读取音频数据
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            # 清理临时文件
            os.unlink(temp_path)
            
            # 计算时长（简化处理）
            duration = max(1.0, len(text) / (150 * speed) * 60)
            
            return {
                "audio_data": base64.b64encode(audio_data).decode("utf-8"),
                "format": "wav",
                "duration": round(duration, 2)
            }
        except ImportError:
            logger.error("未安装edge-tts库，无法使用Edge TTS语音合成")
            # 回退到模拟数据
            return await self._mock_text_to_speech(text, language, voice, speed, pitch, volume)

# 创建全局服务实例
speech_to_text_service = SpeechToTextService()
text_to_speech_service = TextToSpeechService()
