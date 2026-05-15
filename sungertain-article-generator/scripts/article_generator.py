#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三才靈芝農場 博客文章自動生成系統
Sungertain Ganoderma Farm Blog Article Generator

This script generates SEO-optimized blog articles with verified products and sources.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

# 產品清單（從CSV匯入）
PRODUCT_DATABASE = {
    # 飲食系列 (FD)
    "FD-WOODEAR-001": {
        "name": "靈芝黑木耳露 (瓶)",
        "category": "飲食系列",
        "price": 140,
        "description": "結合靈芝精華與黑木耳，富含植物膠質與多醣體，順口好喝。"
    },
    "FD-TEA-001": {
        "name": "靈芝茶包 (6入) -小",
        "category": "飲食系列",
        "price": 250,
        "description": "採用靈芝幼茸製成的便利茶包，適合日常溫和沖泡飲用。"
    },
    "FD-COFFEE-001": {
        "name": "靈芝健康咖啡 (5 入)",
        "category": "飲食系列",
        "price": 350,
        "description": "融入靈芝萃取物的特色咖啡，提神同時兼顧日常養生。"
    },
    "FD-RAW-001": {
        "name": "靈芝原朵 (小包)",
        "category": "飲食系列",
        "price": 1000,
        "description": "完整乾燥的靈芝子實體，保留原始營養，適合自行熬煮或泡茶。"
    },
    "FD-SOUP-001": {
        "name": "靈芝養生膳食 (藥膳湯)",
        "category": "飲食系列",
        "price": 1800,
        "description": "搭配靈芝的養生藥膳包，方便在家燉煮健康美味的湯品。"
    },
    # 保健系列 (WN)
    "WN-REISHICAP-001": {
        "name": "靈芝膠囊 100% (60粒)",
        "category": "保健系列",
        "price": 500,
        "description": "濃縮靈芝精華的生技膠囊，方便現代人隨時補充多醣體。"
    },
    "WN-REISHI-001": {
        "name": "五倍靈芝粉",
        "category": "保健系列",
        "price": 4000,
        "description": "五倍高濃度萃取的靈芝精華，提供更強效的健康防護與保養。"
    },
    # 美妝換洗系列 (PR)
    "PR-TOOTH-001": {
        "name": "寶萊詩靈芝蜂膠精萃牙膏 (單支)",
        "category": "美妝換洗",
        "price": 180,
        "description": "添加靈芝與蜂膠珍貴成分，幫助維護口腔健康，保持口氣清新。"
    }
}

# 7日輪轉計劃
ROTATION_PLAN = [
    {
        "day": 1,
        "category": "入門認識",
        "sku": "FD-WOODEAR-001",
        "description": "適合初次接觸靈芝的消費者"
    },
    {
        "day": 2,
        "category": "選購指南",
        "sku": "FD-TEA-001",
        "description": "產品對比與選擇建議"
    },
    {
        "day": 3,
        "category": "選購指南",
        "sku": "WN-REISHICAP-001",
        "description": "產品對比與選擇建議"
    },
    {
        "day": 4,
        "category": "飲食指南",
        "sku": "FD-COFFEE-001",
        "description": "食用方法與搭配"
    },
    {
        "day": 5,
        "category": "保存方式",
        "sku": "FD-RAW-001",
        "description": "儲存與保質期"
    },
    {
        "day": 6,
        "category": "常見問題",
        "sku": "FD-SOUP-001",
        "description": "FAQ與解惑"
    },
    {
        "day": 7,
        "category": "深入認識",
        "sku": "WN-REISHI-001",
        "description": "科學與專業知識"
    }
]

# EEAT原則參考來源示例
REFERENCE_SOURCES = {
    "academic": [
        "NIH PubMed Central",
        "Google Scholar",
        "WHO官方文件",
        "大學醫學院發布"
    ],
    "authority": [
        "衛生福利部食藥署",
        "臺灣營養師公會",
        "健康教育中心",
        "認證健康機構"
    ],
    "media": [
        "健康相關新聞網站",
        "認可的醫療科普網站",
        "行業專家部落格"
    ]
}

class ArticleGenerator:
    """文章生成器主類"""

    def __init__(self):
        self.product_db = PRODUCT_DATABASE
        self.rotation = ROTATION_PLAN

    def validate_product(self, sku: str) -> Tuple[bool, str]:
        """驗證產品是否在清單中"""
        if sku in self.product_db:
            return True, self.product_db[sku]["name"]
        else:
            valid_skus = ", ".join(self.product_db.keys())
            return False, f"產品 {sku} 不在驗證清單中。可用產品: {valid_skus}"

    def get_product_info(self, sku: str) -> Dict:
        """獲取產品信息"""
        if sku in self.product_db:
            return self.product_db[sku]
        return None

    def validate_meta_table(self, meta_info: Dict) -> Tuple[bool, List[str]]:
        """驗證Meta信息表格的完整性"""
        required_fields = [
            "seo_title",
            "meta_description",
            "publish_date",
            "category",
            "product_name",
            "product_sku",
            "target_audience"
        ]

        errors = []
        for field in required_fields:
            if field not in meta_info or not meta_info[field]:
                errors.append(f"缺少必需字段: {field}")

        # 驗證SEO標題長度（40-60字元）
        if "seo_title" in meta_info:
            title_len = len(meta_info["seo_title"])
            if title_len < 40 or title_len > 60:
                errors.append(f"SEO標題應為40-60字元，當前{title_len}字元")

        # 驗證Meta描述長度（120-160字元）
        if "meta_description" in meta_info:
            desc_len = len(meta_info["meta_description"])
            if desc_len < 120 or desc_len > 160:
                errors.append(f"Meta描述應為120-160字元，當前{desc_len}字元")

        return len(errors) == 0, errors

    def validate_word_count(self, text: str) -> Tuple[bool, int]:
        """驗證文章字數（600-1000字）"""
        word_count = len(text)
        return 600 <= word_count <= 1000, word_count

    def validate_references(self, references: List[Dict]) -> Tuple[bool, List[str]]:
        """驗證參考資源"""
        errors = []

        # 檢查數量
        if len(references) < 5 or len(references) > 7:
            errors.append(f"應有5-7條參考資源，當前{len(references)}條")

        # 驗證每個參考資源
        for i, ref in enumerate(references):
            ref_num = i + 1

            # 檢查必需字段
            if "title" not in ref:
                errors.append(f"參考資源{ref_num}缺少標題")
            if "url" not in ref:
                errors.append(f"參考資源{ref_num}缺少URL")
            if "access_date" not in ref:
                errors.append(f"參考資源{ref_num}缺少存取日期")
            if "eeat_explanation" not in ref:
                errors.append(f"參考資源{ref_num}缺少EEAT說明")

            # 檢查URL是否為具體頁面（不是首頁）
            if "url" in ref:
                url = ref["url"].lower()
                # 簡單檢查：URL末尾不應該是 / 或 .com/.org等
                if url.endswith(("/", ".com", ".org", ".net", ".tw")):
                    errors.append(f"參考資源{ref_num}的URL看起來是首頁，應該是具體文章頁面")

        return len(errors) == 0, errors

    def check_product_authenticity(self, text: str) -> Tuple[bool, List[str]]:
        """檢查文本中是否提及虛構的產品"""
        errors = []

        # 檢查已知的虛構產品
        fake_products = ["靈芝孢子粉", "靈芝濃縮液", "靈芝片"]
        for fake in fake_products:
            if fake in text:
                errors.append(f"檢測到虛構產品: {fake}（不在驗證清單中）")

        return len(errors) == 0, errors

    def generate_quality_report(self,
                               meta_info: Dict,
                               article_body: str,
                               references: List[Dict]) -> Dict:
        """生成品質檢查報告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        # Meta信息檢查
        meta_valid, meta_errors = self.validate_meta_table(meta_info)
        report["checks"]["meta_info"] = {
            "valid": meta_valid,
            "errors": meta_errors
        }

        # 字數檢查
        word_valid, word_count = self.validate_word_count(article_body)
        report["checks"]["word_count"] = {
            "valid": word_valid,
            "count": word_count,
            "requirement": "600-1000字"
        }

        # 參考資源檢查
        ref_valid, ref_errors = self.validate_references(references)
        report["checks"]["references"] = {
            "valid": ref_valid,
            "count": len(references),
            "errors": ref_errors
        }

        # 產品真實性檢查
        product_valid, product_errors = self.check_product_authenticity(article_body)
        report["checks"]["product_authenticity"] = {
            "valid": product_valid,
            "errors": product_errors
        }

        # 整體評分
        all_valid = all([
            meta_valid,
            word_valid,
            ref_valid,
            product_valid
        ])
        report["overall_pass"] = all_valid

        return report


def main():
    """主程序入口"""
    generator = ArticleGenerator()

    print("=" * 60)
    print("三才靈芝農場 博客文章生成系統")
    print("=" * 60)

    # 示例：驗證產品
    print("\n[產品驗證示例]")
    is_valid, message = generator.validate_product("FD-WOODEAR-001")
    print(f"FD-WOODEAR-001: {message}")

    is_valid, message = generator.validate_product("FAKE-001")
    print(f"FAKE-001: {message}")

    # 示例：獲取7日計劃
    print("\n[7日輪轉計劃]")
    for day_plan in generator.rotation:
        product = generator.get_product_info(day_plan["sku"])
        print(f"Day {day_plan['day']}: {day_plan['category']}")
        print(f"  產品: {product['name']} ({day_plan['sku']})")
        print(f"  說明: {day_plan['description']}\n")


if __name__ == "__main__":
    main()
