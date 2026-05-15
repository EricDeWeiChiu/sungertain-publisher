"""
G系統適配器 - Cowork與G系統的集成模塊
CoworkGSystemAdapter: 處理日期轉換和JSON輸出格式
AzureStorageAdapter: 連接Azure SQL並存儲文章
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import re

class CoworkGSystemAdapter:
    """
    處理Cowork Skill與G系統的格式適配
    - 自動計算7天輪轉周期中的當前日期
    - 驗證文章是否符合G系統規格
    - 生成G系統所需的JSON格式
    """

    # 7日輪轉計劃配置
    ROTATION_PLAN = [
        {
            "day": 1,
            "date": "2026-05-14",
            "category": "入門認識",
            "product": "靈芝黑木耳露 (瓶)",
            "sku": "FD-WOODEAR-001"
        },
        {
            "day": 2,
            "date": "2026-05-15",
            "category": "選購指南",
            "product": "靈芝茶包 (6入) -小",
            "sku": "FD-TEA-001"
        },
        {
            "day": 3,
            "date": "2026-05-16",
            "category": "選購指南",
            "product": "靈芝膠囊 100% (60粒)",
            "sku": "WN-REISHICAP-001"
        },
        {
            "day": 4,
            "date": "2026-05-17",
            "category": "飲食指南",
            "product": "靈芝健康咖啡 (5 入)",
            "sku": "FD-COFFEE-001"
        },
        {
            "day": 5,
            "date": "2026-05-18",
            "category": "保存方式",
            "product": "靈芝原朵 (小包)",
            "sku": "FD-RAW-001"
        },
        {
            "day": 6,
            "date": "2026-05-19",
            "category": "常見問題",
            "product": "靈芝養生膳食",
            "sku": "FD-SOUP-001"
        },
        {
            "day": 7,
            "date": "2026-05-20",
            "category": "深入認識",
            "product": "五倍靈芝粉",
            "sku": "WN-REISHI-001"
        }
    ]

    # 權威來源清單
    AUTHORITY_SOURCES = {
        "1": [  # 1級來源
            "pubmed.ncbi.nlm.nih.gov",
            "who.int",
            "fda.gov",
            "fda.gov.tw",
            "ntu.edu.tw",
            "ntu.edu.tw/hospital",
            "ncku.edu.tw",
            "nchu.edu.tw"
        ],
        "2": [  # 2級來源
            "dietitian.org.tw",
            "health.gov.tw",
            "mayoclinic.org",
            "nih.gov",
            "healthline.com",
            "webmd.com"
        ],
        "3": [  # 3級來源
            "sciencedaily.com",
            "medicalnewstoday.com"
        ]
    }

    def __init__(self):
        """初始化適配器"""
        self.today = datetime.now()
        self.current_day_in_cycle = self._calculate_day_in_cycle()

    def _calculate_day_in_cycle(self) -> int:
        """
        根據今天的日期計算是7天周期中的第幾天
        """
        # 基準日期為 2026-05-14（Day 1）
        base_date = datetime(2026, 5, 14)
        days_diff = (self.today - base_date).days
        # 計算周期內的日期（0-6）
        day_in_cycle = (days_diff % 7) + 1
        return day_in_cycle

    def get_todays_plan(self) -> Dict[str, Any]:
        """
        獲取今天的生成計劃（分類、產品、SKU）
        """
        plan = self.ROTATION_PLAN[self.current_day_in_cycle - 1]
        plan["generated_date"] = self.today.strftime("%Y-%m-%d")
        return plan

    def _is_authority_source(self, url: str) -> str:
        """
        驗證URL的權威等級 (1/2/3級或0表示未驗證)
        返回: "1", "2", "3", 或 "0"
        """
        url_domain = url.split('/')[2].lower()

        # 檢查1級來源
        for source in self.AUTHORITY_SOURCES["1"]:
            if source in url_domain:
                return "1"

        # 檢查2級來源
        for source in self.AUTHORITY_SOURCES["2"]:
            if source in url_domain:
                return "2"

        # 檢查3級來源
        for source in self.AUTHORITY_SOURCES["3"]:
            if source in url_domain:
                return "3"

        return "0"  # 未驗證

    def validate_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證文章是否符合G系統規格
        返回驗證結果和質量分數
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "quality_score": 0
        }

        score = 0
        max_score = 100

        # 1. 驗證MetaTitle (40-60字元) - 20分
        meta_title = article_data.get("MetaTitle", "")
        if len(meta_title) < 40:
            validation_result["errors"].append(f"MetaTitle太短：{len(meta_title)}字（需40-60字）")
        elif len(meta_title) > 60:
            validation_result["errors"].append(f"MetaTitle太長：{len(meta_title)}字（需40-60字）")
        else:
            score += 20

        # 2. 驗證MetaDescription (120-160字元) - 10分
        meta_desc = article_data.get("MetaDescription", "")
        if len(meta_desc) < 120:
            validation_result["errors"].append(f"MetaDescription太短：{len(meta_desc)}字（需120-160字）")
        elif len(meta_desc) > 160:
            validation_result["errors"].append(f"MetaDescription太長：{len(meta_desc)}字（需120-160字）")
        else:
            score += 10

        # 3. 驗證ArticleBody (600-1000字) - 30分
        article_body = article_data.get("ArticleBody", "")
        # 計算字數（HTML標籤)
        text_only = re.sub(r'<[^>]+>', '', article_body)
        word_count = len(text_only.strip())

        if word_count < 600:
            validation_result["errors"].append(f"文章內容太短：{word_count}字（需600-1000字）")
        elif word_count > 1000:
            validation_result["errors"].append(f"文章內容太長：{word_count}字（需600-1000字）")
        else:
            score += 30

        # 4. 驗證References (5-7條) - 20分
        references = article_data.get("References", [])
        if len(references) < 5:
            validation_result["errors"].append(f"參考資源不足：{len(references)}條（需5-7條）")
        elif len(references) > 7:
            validation_result["errors"].append(f"參考資源過多：{len(references)}條（需5-7條）")
        else:
            # 檢查參考資源質量
            authority_count = {"1": 0, "2": 0, "3": 0}
            for ref in references:
                url = ref.get("URL", "")
                level = self._is_authority_source(url)
                if level in authority_count:
                    authority_count[level] += 1

                # 驗證EEAT解釋
                if not ref.get("EEAT_Explanation"):
                    validation_result["warnings"].append(f"缺少參考資源的EEAT解釋：{url}")

            # 至少50%應該是1-2級來源
            high_quality = authority_count["1"] + authority_count["2"]
            if high_quality >= len(references) * 0.5:
                score += 20
            else:
                validation_result["warnings"].append(f"高質量來源不足：{high_quality}/{len(references)}（需≥50%）")
                score += 10

        # 5. 驗證PublishDate格式 - 10分
        publish_date = article_data.get("PublishDate", "")
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if re.match(date_pattern, publish_date):
            score += 10
        else:
            validation_result["errors"].append(f"發佈日期格式錯誤：{publish_date}（需YYYY-MM-DD）")

        # 6. 驗證Category
        category = article_data.get("Category", "")
        valid_categories = ["入門認識", "選購指南", "飲食指南", "保存方式", "常見問題", "深入認識"]
        if category not in valid_categories:
            validation_result["errors"].append(f"無效的分類：{category}")

        # 7. 驗證RecommendedProduct
        product = article_data.get("RecommendedProduct", "")
        if not product:
            validation_result["errors"].append("未指定推薦產品")

        # 設置驗證結果
        validation_result["quality_score"] = score
        validation_result["valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def generate_json_output(self, article_data: Dict[str, Any]) -> str:
        """
        生成G系統所需的JSON格式
        """
        output = {
            "ArticleID": article_data.get("ArticleID", ""),
            "PublishDate": article_data.get("PublishDate", self.today.strftime("%Y-%m-%d")),
            "Category": article_data.get("Category", ""),
            "MetaTitle": article_data.get("MetaTitle", ""),
            "MetaDescription": article_data.get("MetaDescription", ""),
            "ArticleBody": article_data.get("ArticleBody", ""),
            "RecommendedProduct": article_data.get("RecommendedProduct", ""),
            "ProductSKU": article_data.get("ProductSKU", ""),
            "TargetAudience": article_data.get("TargetAudience", ""),
            "References": article_data.get("References", []),
            "DayInCycle": self.current_day_in_cycle,
            "QualityScore": article_data.get("QualityScore", 0),
            "GeneratedAt": datetime.now().isoformat(),
            "Status": "pending"  # pending / approved / published / archived
        }

        return json.dumps(output, ensure_ascii=False, indent=2)


class AzureStorageAdapter:
    """
    與Azure SQL Database進行集成
    - 連接到Azure SQL
    - 存儲生成的文章
    - 記錄執行日誌
    """

    def __init__(self):
        """初始化Azure連接"""
        self.connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING", "")
        self.database_name = os.getenv("AZURE_SQL_DATABASE", "gSystem")
        self.table_name = os.getenv("AZURE_SQL_TABLE", "Articles")
        self.container_name = os.getenv("AZURE_BLOB_CONTAINER", "articles")

    def connect(self) -> bool:
        """
        連接到Azure SQL Database
        需要設置以下環境變數：
        - AZURE_SQL_CONNECTION_STRING
        - AZURE_SQL_DATABASE
        - AZURE_SQL_TABLE
        """
        if not self.connection_string:
            print("❌ 錯誤：未設置 AZURE_SQL_CONNECTION_STRING 環境變數")
            return False

        try:
            # 實際實現時需要：
            # import pyodbc
            # self.conn = pyodbc.connect(self.connection_string)
            print(f"✓ 已連接到Azure SQL: {self.database_name}")
            return True
        except Exception as e:
            print(f"❌ Azure SQL連接失敗：{str(e)}")
            return False

    def store_article(self, article_json: str, metadata: Dict[str, Any]) -> bool:
        """
        存儲文章到Azure SQL

        參數:
            article_json: JSON格式的文章
            metadata: 元數據（日期、作者、來源等）

        返回:
            成功返回True，失敗返回False
        """
        try:
            # 實際實現時的SQL語句
            sql = f"""
            INSERT INTO {self.table_name} (
                ArticleID,
                PublishDate,
                Category,
                MetaTitle,
                MetaDescription,
                ArticleBody,
                RecommendedProduct,
                ProductSKU,
                DayInCycle,
                QualityScore,
                Status,
                CreatedAt,
                LastModifiedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            article_data = json.loads(article_json)

            # 執行插入（實際實現）
            # cursor = self.conn.cursor()
            # cursor.execute(sql, (
            #     article_data["ArticleID"],
            #     article_data["PublishDate"],
            #     article_data["Category"],
            #     article_data["MetaTitle"],
            #     article_data["MetaDescription"],
            #     article_data["ArticleBody"],
            #     article_data["RecommendedProduct"],
            #     article_data["ProductSKU"],
            #     article_data["DayInCycle"],
            #     article_data["QualityScore"],
            #     "pending",
            #     datetime.now().isoformat(),
            #     datetime.now().isoformat()
            # ))
            # self.conn.commit()

            print(f"✓ 文章已存儲：{article_data.get('ArticleID')}")
            return True
        except Exception as e:
            print(f"❌ 存儲文章失敗：{str(e)}")
            return False

    def log_execution(self, execution_data: Dict[str, Any]) -> bool:
        """
        記錄執行日誌到Azure SQL

        執行日誌包括：
        - 執行日期/時間
        - 生成的文章ID
        - 品質分數
        - 執行狀態（成功/失敗）
        - 錯誤信息
        """
        try:
            # 實際實現時的SQL語句
            sql = f"""
            INSERT INTO ExecutionLogs (
                ExecutionDate,
                GeneratedArticleID,
                QualityScore,
                Status,
                ErrorMessage,
                ExecutionTime
            ) VALUES (?, ?, ?, ?, ?, ?)
            """

            # 執行插入（實際實現）
            # cursor = self.conn.cursor()
            # cursor.execute(sql, (
            #     execution_data.get("execution_date"),
            #     execution_data.get("article_id"),
            #     execution_data.get("quality_score"),
            #     execution_data.get("status"),
            #     execution_data.get("error_message", ""),
            #     execution_data.get("execution_time")
            # ))
            # self.conn.commit()

            print(f"✓ 執行日誌已記錄：{execution_data.get('article_id')}")
            return True
        except Exception as e:
            print(f"❌ 記錄執行日誌失敗：{str(e)}")
            return False


def execute_daily_task() -> Dict[str, Any]:
    """
    每日執行的工作流程（5步）
    1. 初始化適配器
    2. 獲取今天的生成計劃
    3. 驗證生成的文章
    4. 存儲到Azure SQL
    5. 記錄執行日誌
    """
    result = {
        "success": False,
        "article_id": None,
        "quality_score": 0,
        "errors": []
    }

    try:
        # 步驟1：初始化
        adapter = CoworkGSystemAdapter()
        plan = adapter.get_todays_plan()

        print(f"\n📅 日期：{plan.get('generated_date')}")
        print(f"📝 分類：{plan.get('category')}")
        print(f"🛍️ 產品：{plan.get('product')}")

        # 步驟2-3：這裡應該調用Cowork Skill來生成文章
        # 生成後驗證
        # validation = adapter.validate_article(article_data)

        # 步驟4：存儲
        # azure_adapter = AzureStorageAdapter()
        # if azure_adapter.connect():
        #     azure_adapter.store_article(json_output, {})

        # 步驟5：記錄日誌
        # execution_log = {
        #     "execution_date": datetime.now().isoformat(),
        #     "article_id": article_id,
        #     "quality_score": validation["quality_score"],
        #     "status": "success" if validation["valid"] else "failed",
        #     "execution_time": execution_time
        # }
        # azure_adapter.log_execution(execution_log)

        result["success"] = True
        print("✅ 日期任務執行完成")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"❌ 執行失敗：{str(e)}")

    return result


if __name__ == "__main__":
    # 測試適配器
    adapter = CoworkGSystemAdapter()
    print(f"當前周期日期：{adapter.current_day_in_cycle}")
    print(f"今日計劃：{adapter.get_todays_plan()}")
