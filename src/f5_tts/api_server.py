from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import urllib.parse
import json
import os
import tempfile
from typing import Dict, Optional, List, Tuple, Union
from pydantic import BaseModel
import logging
from pathlib import Path
import soundfile as sf

from f5_tts.api import F5TTS
from f5_tts.model.utils import seed_everything


class TTSRequest(BaseModel):
    """TTS 请求参数模型"""
    text: str
    character: str = "default"
    emotion: str = "default"
    text_language: str = "多语种混合"
    format: str = "wav"
    top_k: float = 50.0
    top_p: float = 0.95
    batch_size: int = 1
    speed: float = 1.0
    temperature: float = 0.7
    save_temp: bool = False
    stream: bool = False


class TTSServer:
    def __init__(
        self, 
        model_path: Optional[str] = None, 
        character_dir: Optional[str] = None,
        cache_dir: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 6006,
        debug: bool = False
    ):
        """初始化 TTS 服务器"""
        self.app = FastAPI(
            title="F5 TTS API",
            description="F5 TTS 文本转语音 API 服务",
            version="1.0.0"
        )
        
        # 添加 CORS 中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 允许所有来源
            allow_credentials=True,
            allow_methods=["*"],  # 允许所有方法
            allow_headers=["*"],  # 允许所有头部
        )
        
        self.host = host
        self.port = port
        self.debug = debug
        
        self.tts_engine = F5TTS(
            model_type="F5-TTS",
            ckpt_file=model_path if model_path else "",
        )
        
        # 设置角色目录
        self.character_dir = Path(character_dir) if character_dir else Path(__file__).parent / "characters"
        if not self.character_dir.exists():
            self.character_dir.mkdir(parents=True)
            
        # 设置缓存目录
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / "cache"
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
            
        # 加载配置
        self.params_config = self._load_params_config()
        
        # 设置路由
        self._setup_routes()
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _scan_characters(self) -> Dict[str, List[str]]:
        """扫描角色目录获取可用角色列表"""
        characters = {}
        
        # 遍历角色目录
        for char_dir in self.character_dir.iterdir():
            if not char_dir.is_dir():
                continue
            
            char_name = char_dir.name
            characters[char_name] = ["default"]
                    
        return characters

    def _get_character_paths(self, character: str) -> Tuple[Optional[str], Optional[str]]:
        """获取角色的音频和文本文件路径"""
            
        char_dir = self.character_dir / character
        ref_wav = char_dir / "ref.wav"
        ref_txt = char_dir / "ref.txt"
        
        if not (char_dir.exists() and ref_wav.exists() and ref_txt.exists()):
            return None, None
            
        # 读取参考文本
        with open(ref_txt, "r", encoding="utf-8") as f:
            ref_text = f.read().strip()
            
        return str(ref_wav), ref_text

    def _load_params_config(self) -> Dict:
        """加载参数配置"""
        config_path = Path(__file__).parent / "params_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "supported_languages": ["中文", "英文", "日文", "中英混合", "日英混合", "多语种混合"],
            "supported_formats": ["wav", "mp3", "ogg"]
        }

    def _setup_routes(self):
        """设置 API 路由"""
        
        @self.app.get("/character_list")
        async def get_character_list():
            """获取支持的角色和情感列表"""
            return self._scan_characters()

        @self.app.get("/tts")
        @self.app.post("/tts")
        async def text_to_speech(request: Union[TTSRequest, None] = None, text: str = "", character: str = "default"):
            """文本转语音接口"""
            try:
                # 处理 GET 请求参数
                if request is None:
                    params = TTSRequest(
                        text=urllib.parse.unquote(text),
                        character=character
                    )
                else:
                    params = request

                # 参数验证
                if not params.text:
                    raise HTTPException(status_code=400, detail="Text is required")
                
                if params.text_language not in self.params_config["supported_languages"]:
                    raise HTTPException(status_code=400, detail=f"Unsupported language: {params.text_language}")
                    
                # 获取角色参考音频和文本
                ref_audio, ref_text = self._get_character_paths(params.character)
                if not ref_audio:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Character not found: {params.character}"
                    )

                # 生成音频
                with tempfile.NamedTemporaryFile(suffix=f".{params.format}", delete=False) as temp_file:
                    wav, sr, _ = self.tts_engine.infer(
                        ref_file=ref_audio,
                        ref_text=ref_text,
                        gen_text=params.text,
                        speed=params.speed,
                        remove_silence=True
                    )
                    
                    # 保存音频到临时文件
                    sf.write(temp_file.name, wav, sr)

                    # 返回音频文件
                    return FileResponse(
                        temp_file.name,
                        media_type=f"audio/{params.format}",
                        filename=f"tts_output.{params.format}",
                        background=BackgroundTask(lambda: os.unlink(temp_file.name))  # 文件发送后自动删除
                    )

            except Exception as e:
                self.logger.error(f"Error in TTS processing: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    def run(self, **kwargs):
        """运行服务器"""
        # 合并默认配置和自定义配置
        run_kwargs = {
            "host": self.host,
            "port": self.port,
            "reload": self.debug
        }
        run_kwargs.update(kwargs)
        
        self.logger.info(f"Starting server at http://{run_kwargs['host']}:{run_kwargs['port']}")
        uvicorn.run(self.app, **run_kwargs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="F5 TTS API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=6006, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--model-path", help="Path to model checkpoint")
    parser.add_argument("--character-dir", help="Path to character directory")
    parser.add_argument("--cache-dir", help="Path to cache directory", default="temp")
    
    args = parser.parse_args()
    
    server = TTSServer(
        model_path=args.model_path,
        character_dir=args.character_dir,
        cache_dir=args.cache_dir,
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    server.run() 