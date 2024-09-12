import Agently
import os
from dotenv import load_dotenv
# 加载.env文件中的环境变量
load_dotenv(dotenv_path='../.env')
# 从环境变量中读取API密钥和基础URL
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')
model = os.getenv('model', 'deepseek-chat')
agent_factory = (
    Agently.AgentFactory()
    .set_settings("current_model", "OpenAI")
    .set_settings("model.OpenAI.url",base_url)
    .set_settings("model.OpenAI.auth", {"api_key": api_key})
    .set_settings("model.OpenAI.options", {"model": model})
    .set_proxy("http://127.0.0.1:8888")
)

agent = agent_factory.create_agent()
agent_GLM_4 = (
    agent_factory.create_agent()
        .set_settings("model.OpenAI.options", { "model": "glm-4-flash" })
)
agent_gemini = (
    agent_factory.create_agent()
        .set_settings("model.OpenAI.options", { "model": "gemini-1.5-pro" })
)

# result = (
#     # agent
#     agent_GLM_4
#         .input("给我输出3个单词和2个句子")
#         .instruct("输出语言", "中文")
#         .output({
#             "单词": [("str", )],
#             "句子": ("list", ),
#         })
# .on_delta(lambda data: print(data, end=""))
#         .start()
# )
# print(result)


from datetime import datetime
import pytz
def get_current_datetime(timezone):
    print("调用了函数")
    tz = pytz.timezone(timezone)
    return datetime.now().astimezone(tz)

tool_info = {
    "tool_name": "get_now",
    "desc": "get current data and time",
    "args": {
        "timezone": (
            "str",
            "[*Required] Timezone string used in pytz.timezone() in Python"
        )
    },
    "func": get_current_datetime
}
Agently.global_tool_manager.register(
    tool_name = tool_info["tool_name"],
    desc = tool_info["desc"],
    args = tool_info["args"],
    func = tool_info["func"],
)
Agently.global_tool_manager.register(**tool_info)


# 我们用一个临时agent实例来调用全局工具

result = (
    agent_gemini
# agent_GLM_4
        #声明使用全局工具中我们刚注册的"get_now"
        .use_public_tools(["get_now"])
        # 通过输入相关询问内容测试工具调用效果
        .input("我在北京，现在几点了？")
        .start()
)
print(result)