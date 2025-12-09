from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from app.database import get_db
from app.services.speech_service import speech_to_text_service, text_to_speech_service

router = APIRouter(
    prefix="/api",
    tags=["speech"],
)

@router.post("/speech-to-text", response_model=schemas.ApiResponse, summary="语音转文字", description="将语音文件转换为文字")
async def speech_to_text(audio_file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    将语音文件转换为文字
    
    Args:
        audio_file: 音频文件，支持wav、mp3等格式
        
    Returns:
        dict: 包含转换结果的字典
            - text: 转换后的文字
            - confidence: 置信度
            - duration: 音频时长
    """
    try:
        # 调用语音转文字服务
        result = await speech_to_text_service.convert(audio_file)
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to convert speech to text: {str(e)}",
            "data": None
        }

@router.post("/text-to-speech", response_model=schemas.ApiResponse, summary="文字转语音", description="将文字转换为语音")
async def text_to_speech(
    text: str = Body(..., description="要转换的文字"),
    language: str = Body("zh-CN", description="语言代码"),
    voice: str = Body("default", description="语音类型"),
    speed: float = Body(None, ge=0.5, le=2.0, description="语速，范围0.5-2.0"),
    pitch: float = Body(None, ge=0.5, le=2.0, description="音调，范围0.5-2.0"),
    volume: float = Body(None, ge=0.0, le=1.0, description="音量，范围0.0-1.0"),
    language_style: str = Body(None, description="语言风格，可选值：专业严谨、亲切友善、轻松活泼、理性客观"),
    db: AsyncSession = Depends(get_db)
):
    """
    将文字转换为语音
    
    Args:
        text: 要转换的文字
        language: 语言代码，默认为中文
        voice: 语音类型，默认为default
        speed: 语速，范围0.5-2.0
        pitch: 音调，范围0.5-2.0
        volume: 音量，范围0.0-1.0
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
        # 调用文字转语音服务
        result = await text_to_speech_service.convert(
            text=text,
            language=language,
            voice=voice,
            speed=speed,
            pitch=pitch,
            volume=volume,
            language_style=language_style
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to convert text to speech: {str(e)}",
            "data": None
        }
