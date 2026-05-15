#!/usr/bin/env python3
"""
每日部落格文章自動工作流程
- 生成 .docx 文章
- 自動推送到 G 系統

每天早上 9:00 (台灣時間) 執行
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 添加當前目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from article_publisher import publish_article
import logging

# 配置日誌
LOG_DIR = Path('/Users/ericchiu/Documents/sungertain-design/G系統專案/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_day_in_cycle():
    """
    根據日期計算 7 日循環中的日期
    5月14日 = Day 1
    5月15日 = Day 2
    ...
    5月20日 = Day 7
    5月21日 = Day 1 (循環)
    """
    # 基準日期：2026年5月14日 (Day 1)
    base_date = datetime(2026, 5, 14)
    today = datetime.now()

    # 計算天數差
    days_diff = (today - base_date).days

    # 循環計算 (1-7)
    day_in_cycle = ((days_diff) % 7) + 1

    return day_in_cycle


def get_article_info():
    """
    根據日期取得文章信息
    """
    # 文章計劃
    plan = [
        {'day': 1, 'date': '5/14', 'category': '入門認識', 'product': '纖芝翠-靈芝黑木耳露(瓶)'},
        {'day': 2, 'date': '5/15', 'category': '選購指南', 'product': '靈芝茶包 (36入) -大'},
        {'day': 3, 'date': '5/16', 'category': '選購指南', 'product': '靈芝膠囊 100% (60粒)'},
        {'day': 4, 'date': '5/17', 'category': '飲食指南', 'product': '靈芝健康咖啡 (5 入)'},
        {'day': 5, 'date': '5/18', 'category': '保存方式', 'product': '靈芝原朵 (小包)'},
        {'day': 6, 'date': '5/19', 'category': '常見問題', 'product': '五倍靈芝粉'},
        {'day': 7, 'date': '5/20', 'category': '深入認識', 'product': '靈芝藥膳湯'}
    ]

    day = get_day_in_cycle()
    return plan[day - 1], day


def find_article_file(day: int, category: str):
    """
    查找對應的 .docx 文件

    檔名格式: YYYYMMDD_分類_商品名.docx
    例: 20260515_選購指南_靈芝茶包 (36入) -大.docx
    """
    articles_dir = Path('/Users/ericchiu/Documents/sungertain-design/G系統專案')

    # 取得今天的日期
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')

    # 嘗試找到文件
    for file in articles_dir.glob(f'{date_str}_*.docx'):
        if category in file.name and not file.name.startswith('['):
            return file

    return None


def main():
    """主程序"""
    logger.info("=" * 70)
    logger.info("🚀 開始每日部落格文章工作流程")
    logger.info("=" * 70)

    try:
        # 取得今天的文章信息
        info, day = get_article_info()
        logger.info(f"\n📅 Day {day} - {info['category']}")
        logger.info(f"   推薦產品: {info['product']}")

        # 查找文章文件
        article_file = find_article_file(day, info['category'])

        if not article_file:
            logger.error(f"❌ 找不到文章文件")
            logger.error(f"   預期檔名: {datetime.now().strftime('%Y%m%d')}_{info['category']}_*.docx")
            return 1

        logger.info(f"\n📄 找到文章: {article_file.name}")

        # 推送文章
        logger.info(f"\n🚀 開始推送到 G 系統...")
        success = publish_article(str(article_file), day)

        if success:
            logger.info("\n✅ 工作流程完成！")
            logger.info(f"   日誌: {LOG_DIR}")
            return 0
        else:
            logger.error("\n❌ 推送失敗")
            return 1

    except Exception as e:
        logger.error(f"\n❌ 發生錯誤: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    exit_code = main()
    logger.info("=" * 70)
    sys.exit(exit_code)
