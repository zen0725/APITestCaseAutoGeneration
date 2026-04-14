import asyncio
import logging
from serviceDiscover.service_discovery_engine import ServiceDiscoveryEngine
from serviceDiscover.service_models import DiscoveryConfig

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def main():
    # 配置发现引擎
    config = DiscoveryConfig(
        poll_interval=30,  # 每30秒发现一次
        health_check_timeout=5,  # 健康检查超时5秒
        api_docs_timeout=10,  # API文档获取超时10秒
        enable_auto_refresh=True  # 启用自动刷新
    )

    # 创建发现引擎
    discovery_engine = ServiceDiscoveryEngine(config)

    try:
        # 启动发现引擎
        registry_url = "http://eureka-server:8761"  # 或者Consul、Nacos等的URL
        await discovery_engine.start(registry_url)

        # 等待首次发现完成
        await asyncio.sleep(5)

        # 获取发现统计
        stats = discovery_engine.get_service_stats()
        print(f"服务发现统计: {stats}")

        # 获取所有API契约
        contracts = discovery_engine.get_all_contracts()
        print(f"发现 {len(contracts)} 个API契约")

        # 示例：获取特定服务的契约
        user_service_contract = discovery_engine.get_service_contract("user-service")
        if user_service_contract:
            print(f"用户服务端点: {user_service_contract.endpoints[:5]}...")  # 显示前5个端点

        # 保持运行（在实际应用中，这里可以集成到主循环中）
        await asyncio.sleep(300)  # 运行5分钟

    except KeyboardInterrupt:
        print("正在停止...")
    finally:
        await discovery_engine.stop()

if __name__ == "__main__":
    asyncio.run(main())