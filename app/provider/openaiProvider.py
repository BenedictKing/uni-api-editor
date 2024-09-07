import asyncio
import os
import httpx
from typing import Dict, Any, AsyncGenerator, Tuple
from fastapi import HTTPException

from app.provider.httpxHelp import get_api_data
from app.provider.models import Message
import ujson as json
from app.log import logger
from app.provider.openaiSSEHandler import openaiSSEHandler
from app.provider.openaiSendBodyHeandler import openaiSendBodyHeandler
import pyefun

class openaiProvider:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "User-Agent": "curl/7.68.0",

            },
            timeout=httpx.Timeout(connect=15.0, read=600, write=30.0, pool=30.0),
            # http2=False,  # 将 http2 设置为 False
            # verify=False,
            # follow_redirects=True,
            #
            # proxies={  # 使用字典形式来指定不同类型的代理
            #     "http://": "http://127.0.0.1:8888",
            #     "https://": "http://127.0.0.1:8888",  # 如果代理服务器支持 HTTP 和 HTTPS，则可以这样设置
            # },
        )
        self.DataHeadler = openaiSSEHandler

        self._debug = True
        self._cache = True
        self.setDebugSave("openai")

    def setDebugSave(self, name="openai"):
        name = name.replace("/", "-")
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构造文件的绝对路径
        self._debugfile_sse = os.path.join(current_dir + f"/debugdata/{name}_sse.txt")
        self._debugfile_data = os.path.join(current_dir + f"/debugdata/{name}_data.txt")



    async def sendChatCompletions(self, request) -> AsyncGenerator[str, None]:
        id = request.get('id',"")
        model = request.get('model',"")
        logger.name = f"openaiProvider.{id}.request.model"
        # payload = await self.get_payload(request)
        sendReady = openaiSendBodyHeandler(self.api_key, self.base_url, model)
        sendReady.header_openai(request)
        pushdata = sendReady.get_oepnai()
        url = pushdata["url"]
        headers = pushdata["headers"]
        body = pushdata["body"]

        logger.info(f"\r\nsend {url} \r\nbody:\r\n{json.dumps(body, indent=2, ensure_ascii=False)}")

        # 调试部分 不要看
        debug_file = self._debugfile_sse if request.get("stream",False) else self._debugfile_data
        if self._debug:
            error = False
            if self._cache:
                logger.info(f"使用缓存{debug_file}")
                try:
                    data = pyefun.读入文本(debug_file)
                    if not request.get("stream",False):
                        if data != "":
                            yield data
                            return

                    arr = pyefun.分割文本(data, "\n")
                    for line in arr:
                        line = line.strip()
                        if line != "":
                            yield line
                            error = True

                except FileNotFoundError:
                    error = False
                    logger.warning(f"Debug file {debug_file} not found, it will be created in write mode.")
            if error:
                return
            if pyefun.文件是否存在(debug_file):
                pyefun.删除文件(debug_file)


        async for line in get_api_data(pushdata):
            if self._cache:
                if request.get("stream", False):
                    pyefun.文件_追加文本(debug_file, line)
                else:
                    pyefun.文件_写出(debug_file, line)

            logger.info(f"收到数据\r\n{line}")
            yield line


    async def chat2api(self, request, request_model_name: str = "", id: str = "") -> AsyncGenerator[
        str, None]:

        try:
            genData = self.sendChatCompletions(request)
            first_chunk = await genData.__anext__()
        except Exception as e:
            raise HTTPException(status_code=404, detail=e)

        self.DataHeadler = openaiSSEHandler(id, request_model_name)
        if not request.get("stream",False):
            content = self.DataHeadler.handle_data_line(first_chunk)
            yield content
            stats_data = self.DataHeadler.get_stats()
            logger.info(f"SSE 数据流迭代完成，统计信息：{stats_data}")
            return

        # 流处理的代码
        yield True
        yield "data: " + self.DataHeadler.generate_sse_response(None)
        content = self.DataHeadler.handle_SSE_data_line(first_chunk)
        if content:
            yield "data: " + content
        async for chunk in genData:
            content = self.DataHeadler.handle_SSE_data_line(chunk)
            if content == "[DONE]":
                yield "data: [DONE]"
                break
            if content:
                yield "data: " + content
        stats_data = self.DataHeadler.get_stats()
        logger.info(f"SSE 数据流迭代完成，统计信息：{stats_data}")
        # logger.info(f"转换为普通：{handler.generate_response()}")

    async def raise_for_status(self, response: httpx.Response):
        if response.status_code == 200:
            return
        response_content = await response.aread()
        error_data = {
            "error": "上游服务器出现错误",
            "response_body": response_content.decode("utf-8"),
            "status_code": response.status_code
        }
        raise HTTPException(status_code=500, detail=error_data)



if __name__ == "__main__":
    async def main():
        from app.database import Database
        db = Database("../api.yaml")
        model_test = [
            "glm-4-flash",
            # "doubao-pro-128k",
            # "moonshot-v1-128k",
            # "qwen2-72b",
            # "deepseek-coder"
        ]
        for model_name in model_test:
            providers, error = await db.get_user_provider("sk-111111", model_name)
            provider = providers[0]
            api_key = provider['api_key']
            base_url = provider['base_url']
            model_name = provider['mapped_model']
            # print(provider)
            print("正在测试", model_name)
            openai_interface = openaiProvider(api_key, base_url)
            openai_interface.setDebugSave(f"{model_name}_{provider['provider']}")
            openai_interface._debug = True
            openai_interface._cache = False

            content = ""
            async for response in openai_interface.chat2api({
                "model": model_name,
                "messages": [{"role": "user", "content": "请用三句话描述春天。"}],
                "stream": False,
            }):
                # content += response
                # logger.info( response)
                logger.info(response)


    asyncio.run(main())
