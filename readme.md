
## Introduction

这是一个统一管理大模型API的项目，可以通过一个统一的API接口调用多个后端服务，统一转换为 OpenAI 格式，支持负载均衡。

目前支持的后端服务有： OpenAI、Anthropic、Gemini、Vertex、cloudflare、DeepBricks、OpenRouter 等。

## Configuration

使用 api.yaml 配置文件，可以配置多个模型，每个模型可以配置多个后端服务，支持负载均衡。下面是 api.yaml 配置文件的示例：

api.yaml
```
providers:
  - provider: openai
    name: 智谱清言
    base_url: https://open.bigmodel.cn/api/paas/v4
    api_key: 请填写你的api_key
    model:
      - glm-4-flash
      

  - provider: gemini
    name: Gemini
    base_url: https://generativelanguage.googleapis.com/v1beta
    api_key: 请填写你的api_key
    model:
      - gemini-1.5-pro
      - gemini-1.5-flash
      - gemini-1.5-flash: gpt-4o

  - provider: openai
    name: 豆包
    base_url: https://ark.cn-beijing.volces.com/api/v3
    api_key: 请填写你的api_key
    model:
      - ep-20240906033439-zrc2x: doubao-pro-128k
      - ep-20240613130011-c2zgx: doubao-pro-32k
      - ep-20240729175503-5bbf7: moonshot-v1-128k

  - provider: openai
    name: 硅基流动
    base_url: https://api.siliconflow.cn/v1
    api_key: 请填写你的api_key
    model:
      - Qwen/Qwen2-72B-Instruct: qwen2-72b
      - Qwen/Qwen1.5-110B-Chat: qwen1.5-110b
      - deepseek-ai/DeepSeek-V2-Chat: deepseek-chat
#      - deepseek-ai/DeepSeek-Coder-V2-Instruct: deepseek-coder
      - Qwen/Qwen2-7B-Instruct: qwen2-7b
      - Qwen/Qwen2-7B-Instruct: gpt-3.5-turbo
      - Qwen/Qwen2-1.5B-Instruct: qwen2-1.5b
      - Qwen/Qwen1.5-7B-Chat: qwen1.5-7b-chat
      - THUDM/glm-4-9b-chat: glm-4-9b-chat
      - THUDM/chatglm3-6b: chatglm3-6b
      - 01-ai/Yi-1.5-9B-Chat-16K: yi-1.5-9b-chat-16k
      - 01-ai/Yi-1.5-6B-Chat: yi-1.5-6b-chat
      - google/gemma-2-9b-it: gemma-2-9b
      - internlm/internlm2_5-7b-chat: internlm-7b-chat
      - meta-llama/Meta-Llama-3-8B-Instruct: meta-llama-3-8b
      - meta-llama/Meta-Llama-3.1-8B-Instruct: meta-llama-3.1-8b
      - mistralai/Mistral-7B-Instruct-v0.2: mistral-7b


  - provider: openai
    name: deepseek
    base_url: https://api.deepseek.com/v1
    api_key: 请填写你的api_key
    model:
      - deepseek-chat
      - deepseek-coder


  - provider: vertexai_claude
    name: vertexai_claude
    PROJECT_ID: 请填写
    CLIENT_ID: 请填写
    CLIENT_SECRET: 请填写
    REFRESH_TOKEN: 请填写
    model:
      - claude-3-5-sonnet@20240620
      - claude-3-5-sonnet@20240620: claude-3-5-sonnet

  - provider: vertexai_gemini
    name: vertexai_gemini
    PROJECT_ID: 请填写
    CLIENT_ID: 请填写
    CLIENT_SECRET: 请填写
    REFRESH_TOKEN: 请填写
    model:
      - gemini-1.5-flash-001


tokens:
  - api_key: sk-111111
    model:
      - glm*
      - all

  - api_key: sk-222222
    model:
      - gpt-3.5-turbo

server:
    port: 8000
    host: 0.0.0.0
    default_model: glm-4-flash
    debug: false
    cache: false
    db_cache: true # 相同内容的情况下返回上一次成功的回复
    save_log_file: false
    db_path: ./request_log.db

```


## 环境变量

- CONFIG_URL: 配置文件的下载地址，可以是本地文件，也可以是远程文件，选填

## Docker Local Deployment

Start the container

```bash
docker run --user root -p 8001:8000 --name pro-api -dit \
-v ./api.yaml:/home/api.yaml \
duolabmeng6/pro-api:latest
```

Or if you want to use Docker Compose, here is a docker-compose.yml example:

```yaml
services:
  pro-api:
    container_name: pro-api
    image: duolabmeng6/pro-api:latest
    environment:
      - CONFIG_URL=http://file_url/api.yaml
    ports:
      - 8001:8000
    volumes:
      - ./api.yaml:/home/api.yaml
```

CONFIG_URL 就是可以自动下载远程的配置文件。比如你在某个平台不方便修改配置文件，可以把配置文件传到某个托管服务，可以提供直链给 pro-api 下载，CONFIG_URL 就是这个直链。

Run Docker Compose container in the background

```bash
docker-compose pull
docker-compose up -d
```

Docker build

```bash
docker build --no-cache -t pro-api:latest -f Dockerfile --platform linux/amd64 .
docker tag pro-api:latest duolabmeng6/pro-api:latest
docker push duolabmeng6/pro-api:latest
```

One-Click Restart Docker Image

```bash
set -eu
docker pull duolabmeng6/pro-api:latest
docker rm -f pro-api
docker run --user root -p 8001:8000 -dit --name pro-api \
-e CONFIG_URL=http://file_url/api.yaml \
-v ./api.yaml:/home/api.yaml \
duolabmeng6/pro-api:latest
docker logs -f pro-api
```

RESTful curl test

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer ${API}" \
-d '{"model": "gpt-4o","messages": [{"role": "user", "content": "Hello"}],"stream": true}'
```


## Star History

<a href="https://github.com/duolabmeng6/pro-api/stargazers">
        <img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=duolabmeng6/pro-api&type=Date">
</a>