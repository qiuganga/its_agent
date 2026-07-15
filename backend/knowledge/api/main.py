"""

创建FastAPI实例 并且管理所有的路由

"""
# conda activate its_agent
# cd D:\sgg-agent\code\its_multi_agent\backend
# conda activate its_agent
# python -m knowledge.api.main

import logging
import sys
from pathlib import Path

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)
import  uvicorn
from fastapi import FastAPI
from knowledge.api.routers import router
def  create_fast_api()->FastAPI:


    # 1. 创建FastApi实例
    app=FastAPI(title="Knowledge API")


    # 2. 注册各种路由
    app.include_router(router=router)

    # 3.返回创建的FastAPI
    return app



if __name__ == '__main__':
    print("1.准备启动Web服务器")
    try:
        uvicorn.run(app=create_fast_api(),host="127.0.0.1",port=8001)
        logger.info("2.启动Web服务器成功...")
    except KeyboardInterrupt as e:
        logger.error(f"2.启动Web服务器失败: {str(e)}")














