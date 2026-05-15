# Cowork Skill 格式適配指南

針對 G系統的文章格式規範改造 sungertain-article-generator Skill

**對應文檔**：COWORK_ARTICLE_FORMAT_SPECIFICATION.md  
**適用版本**：Skill v1.0 → v1.1 (G系統適配版)  
**最後更新**：2026-05-14

---

## 📋 概述

G系統要求 Cowork 生成的文章必須符合特定的 **JSON 格式規範**。此指南說明如何改造現有 Skill，使其輸出符合 G系統的要求。

### 核心變化

```
原始輸出：Word 文檔 (.docx)
         ↓
新增輸出：JSON 格式 + Azure SQL 存儲
         + Word 文檔（可選）
```

---

## 🔄 改造工作流程

### 步驟1：改造 Skill Prompt

**原始 Prompt（通用版）：**
```
根據以下信息生成博客文章...
日期：20260514
分類：入門認識
推薦產品：靈芝黑木耳露
```

**改造後 Prompt（G系統版）：**
```markdown
# Cowork 文章生成系統 - G系統適配版

你的任務是根據 7日輪轉計劃，自動生成符合 G系統要求的文章，並輸出為指定的 JSON 格式。

## 自動執行參數

自動從系統獲取：
- 當前日期（系統日期）
- Day 編號（根據日期計算）
- 文章分類（根據 Day 查表）
- 推薦產品（根據 Day 查表）
- SKU 和價格（根據產品查表）

### 7日輪轉計劃

| Day | 日期 | 分類 | 產品 | SKU |
|-----|------|------|------|-----|
| 1 | 5/14 | 入門認識 | 靈芝黑木耳露 (瓶) | FD-WOODEAR-001 |
| 2 | 5/15 | 選購指南 | 靈芝茶包 (6入) -小 | FD-TEA-001 |
| 3 | 5/16 | 選購指南 | 靈芝膠囊 100% (60粒) | WN-REISHICAP-001 |
| 4 | 5/17 | 飲食指南 | 靈芝健康咖啡 (5 入) | FD-COFFEE-001 |
| 5 | 5/18 | 保存方式 | 靈芝原朵 (小包) | FD-RAW-001 |
| 6 | 5/19 | 常見問題 | 靈芝養生膳食 (藥膳湯) | FD-SOUP-001 |
| 7 | 5/20 | 深入認識 | 五倍靈芝粉 | WN-REISHI-001 |

### 產品資訊

**飲食系列：**
- FD-WOODEAR-001: 靈芝黑木耳露 (瓶) - $140
- FD-TEA-001: 靈芝茶包 (6入) -小 - $250
- FD-COFFEE-001: 靈芝健康咖啡 (5 入) - $350
- FD-RAW-001: 靈芝原朵 (小包) - $1000
- FD-SOUP-001: 靈芝養生膳食 (藥膳湯) - $1800

**保健系列：**
- WN-REISHICAP-001: 靈芝膠囊 100% (60粒) - $500
- WN-REISHI-001: 五倍靈芝粉 - $4000

## 生成要求

### 1. MetaTitle (必須符合 G系統格式)
- **長度**：40-60字（中英混合時都計為 1字）
- **要求**：包含主關鍵詞、清晰易讀
- **避免**：特殊符號、關鍵詞堆積

**範例（正確）：**
- "認識靈芝黑木耳露：營養、功效與安全飲用指南" (26字，太短，需擴展)
- "靈芝黑木耳露完整介紹：營養成分、健康功效、飲用方式與購買指南" (36字，還是短)
- "靈芝黑木耳露功效與食用指南｜初次購買者必讀的完整營養健康寶典" (37字)

需要達到 40-60 字的標準。重新組織：
"靈芝黑木耳露完整指南：了解營養功效、安全飲用方式、選購建議及常見問題解答" (40字)

### 2. MetaDescription (必須符合 G系統格式)
- **長度**：120-160字（中英混合時都計為 1字）
- **要求**：包含主要內容、吸引點擊、清楚表達主題
- **避免**：截斷句子、過度關鍵詞堆積

**範例：**
"靈芝黑木耳露是結合靈芝精華與黑木耳營養的創新飲品。本文詳細介紹其成分功效、食用方法、購買指南及常見問題。基於科學研究和營養專家建議，幫助初學者和潛在消費者做出明智選擇。" (95字，需擴展至120+)

擴展版本：
"靈芝黑木耳露是結合靈芝精華與黑木耳營養的創新飲品，專為現代人設計。本文詳細介紹其營養成分、科學驗證的健康功效、正確食用方法、購買建議及常見問題解答。基於WHO傳統醫學和現代營養科學，幫助初學者和潛在消費者深入了解、安全飲用並選購合適產品。" (140字)

### 3. TargetAudience (簡潔描述)
- **長度**：50-200字
- **要求**：清楚描述目標閱讀群體

**範例：**
"初次接觸靈芝或該產品的消費者，以及想深入了解黑木耳露營養價值和飲用方式的潛在客戶。特別適合關心健康養生、想補充天然營養、尋求科學指導的現代消費者。"

### 4. ArticleBody (HTML 格式)
- **格式**：正確的 HTML 標籤
- **長度**：600-1000 字（純文字，不計標籤）
- **結構**：
  ```html
  <h2>主標題</h2>
  <p>引言內容...</p>
  
  <h3>副標題</h3>
  <p>段落內容...</p>
  
  <h3>另一個副標題</h3>
  <ul>
    <li>列表項1</li>
    <li>列表項2</li>
  </ul>
  
  <h3>結語</h3>
  <p>結語內容...</p>
  ```
- **要求**：
  - 使用 `<h2>`, `<h3>` (不用 `<h1>`)
  - 使用 `<p>` 分段
  - 合理使用 `<ul>`, `<ol>`, `<li>`
  - 標籤正確閉合
  - 避免內聯樣式

### 5. References (EEAT 格式)
- **數量**：5-7 個
- **必填字段**：`title`, `url`, `access_date`, `eeat_explanation`
- **URL 要求**：必須是具體文章/頁面 URL，不是首頁
- **權威性**：至少 50% 來自 1 級權威來源

**必須使用的已驗證來源庫：**

1級來源（最優先）：
- PubMed Central: https://pubmed.ncbi.nlm.nih.gov/[article-id]
- WHO Traditional Medicine: https://www.who.int/teams/traditional-complementary-and-integrative-medicine
- 台灣食藥署: https://www.fda.gov.tw/TC/site.aspx?sid=140
- Mayo Clinic: https://www.mayoclinic.org/drugs-supplements/...
- FDA Dietary Supplements: https://www.fda.gov/food/dietary-supplements

2級來源（推薦）：
- Frontiers in Nutrition: https://www.frontiersin.org/journals/nutrition/...
- Journal of Ethnopharmacology: https://www.sciencedirect.com/journal/journal-of-ethnopharmacology/...

**EEAT 說明格式（必須完整）：**
```
專業性(Expertise)：[誰撰寫/為什麼合格]
權威性(Authoritativeness)：[機構或出版物的信譽]
真實性(Authenticity)：[提供什麼類型的證據/數據]
可信度(Trustworthiness)：[透明度和客觀性]
```

**範例：**
```
"eeat_explanation": "專業性：美國國家衛生研究院(NIH)的科學研究團隊 | 權威性：PubMed Central官方資料庫，同行評審發表 | 真實性：包含具體的臨床試驗數據和免疫指標分析 | 可信度：透明的研究方法論，基於標準實驗"
```

## 輸出格式 (JSON)

必須輸出以下 JSON 結構。所有字段都是必須的：

```json
{
  "PublishDate": "YYYY-MM-DD",
  "DayInCycle": 1,
  "Category": "入門認識|選購指南|飲食指南|保存方式|常見問題|深入認識",
  "Product": "產品完整名稱",
  "SKU": "SKU代碼",
  "Price": 價格,
  "MetaTitle": "40-60字",
  "MetaDescription": "120-160字",
  "TargetAudience": "50-200字",
  "ArticleBody": "<h2>...</h2><p>...</p>...",
  "WordCount": 600到1000之間的整數,
  "References": [
    {
      "title": "參考資源標題",
      "url": "https://具體頁面URL",
      "access_date": "YYYY-MM-DD",
      "eeat_explanation": "專業性：... | 權威性：... | 真實性：... | 可信度：..."
    },
    // ... 5-7 個參考資源
  ],
  "Status": "Draft",
  "QualityScore": 0到100之間的整數
}
```

## 品質評分計算

```
評分項目：
1. MetaTitle 長度正確 (40-60字): +20分
2. MetaDescription 長度正確 (120-160字): +20分  
3. WordCount 正確 (600-1000): +20分
4. References 數量正確 (5-7個): +20分
5. References 權威性 (至少50%為1級): +20分

及格標準：≥75分
```

## 驗證檢查清單

必須驗證以下項目，才能輸出最終 JSON：

- [ ] PublishDate 是有效日期格式
- [ ] DayInCycle 在 1-7 之間
- [ ] Category 精確匹配允許值
- [ ] Product 來自驗證產品清單
- [ ] SKU 來自驗證產品清單
- [ ] Price 是正數
- [ ] MetaTitle 長度 40-60字
- [ ] MetaDescription 長度 120-160字
- [ ] ArticleBody 是有效 HTML
- [ ] WordCount 在 600-1000 之間
- [ ] References 有 5-7 個
- [ ] 每個 Reference 都有完整的 4 個字段
- [ ] 所有 Reference URL 都是具體頁面（非首頁）
- [ ] 至少 50% References 來自權威來源
- [ ] Status 是 "Draft"
- [ ] QualityScore ≥ 75
- [ ] EEAT 說明完整且符合格式

驗證失敗時：
1. 停止執行
2. 報告具體失敗項目
3. 拒絕輸出 JSON
4. 記錄詳細錯誤信息便於調試

完成所有檢查後，按照上述 JSON 結構輸出最終結果。
```

### 步驟2：改造 Skill 代碼邏輯

#### 2.1 添加 JSON 輸出模組

```python
import json
from datetime import datetime, date
from typing import Dict, List, Any

class CoworkGSystemAdapter:
    """將Skill輸出轉換為G系統JSON格式"""
    
    def __init__(self):
        self.ROTATION_PLAN = [
            {"day": 1, "category": "入門認識", "sku": "FD-WOODEAR-001"},
            {"day": 2, "category": "選購指南", "sku": "FD-TEA-001"},
            {"day": 3, "category": "選購指南", "sku": "WN-REISHICAP-001"},
            {"day": 4, "category": "飲食指南", "sku": "FD-COFFEE-001"},
            {"day": 5, "category": "保存方式", "sku": "FD-RAW-001"},
            {"day": 6, "category": "常見問題", "sku": "FD-SOUP-001"},
            {"day": 7, "category": "深入認識", "sku": "WN-REISHI-001"},
        ]
        
        self.PRODUCTS = {
            "FD-WOODEAR-001": {"name": "靈芝黑木耳露 (瓶)", "price": 140},
            "FD-TEA-001": {"name": "靈芝茶包 (6入) -小", "price": 250},
            "WN-REISHICAP-001": {"name": "靈芝膠囊 100% (60粒)", "price": 500},
            "FD-COFFEE-001": {"name": "靈芝健康咖啡 (5 入)", "price": 350},
            "FD-RAW-001": {"name": "靈芝原朵 (小包)", "price": 1000},
            "FD-SOUP-001": {"name": "靈芝養生膳食 (藥膳湯)", "price": 1800},
            "WN-REISHI-001": {"name": "五倍靈芝粉", "price": 4000},
        }
    
    def get_todays_plan(self) -> Dict[str, Any]:
        """自動決定今天的計劃"""
        today = date.today()
        # 計算7日週期 (以5/14為Day 1)
        start_date = date(2026, 5, 14)
        days_diff = (today - start_date).days
        day_in_cycle = (days_diff % 7) + 1
        
        plan = self.ROTATION_PLAN[day_in_cycle - 1]
        product = self.PRODUCTS[plan["sku"]]
        
        return {
            "date": today.strftime("%Y-%m-%d"),
            "day": day_in_cycle,
            "category": plan["category"],
            "sku": plan["sku"],
            "product": product["name"],
            "price": product["price"]
        }
    
    def validate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """驗證文章並計算評分"""
        errors = []
        score = 0
        
        # 驗證 MetaTitle
        meta_title_len = len(article.get("MetaTitle", ""))
        if 40 <= meta_title_len <= 60:
            score += 20
        else:
            errors.append(f"MetaTitle 長度為 {meta_title_len}，應為 40-60字")
        
        # 驗證 MetaDescription
        meta_desc_len = len(article.get("MetaDescription", ""))
        if 120 <= meta_desc_len <= 160:
            score += 20
        else:
            errors.append(f"MetaDescription 長度為 {meta_desc_len}，應為 120-160字")
        
        # 驗證 WordCount
        word_count = article.get("WordCount", 0)
        if 600 <= word_count <= 1000:
            score += 20
        else:
            errors.append(f"WordCount 為 {word_count}，應為 600-1000字")
        
        # 驗證 References
        references = article.get("References", [])
        if 5 <= len(references) <= 7:
            score += 20
        else:
            errors.append(f"References 有 {len(references)} 個，應為 5-7個")
        
        # 驗證 References 質量
        authority_count = 0
        for ref in references:
            if self._is_authority_source(ref.get("url", "")):
                authority_count += 1
        
        if authority_count >= len(references) * 0.5:
            score += 20
        else:
            errors.append(f"權威來源比例 {authority_count}/{len(references)}，應≥50%")
        
        return {
            "valid": len(errors) == 0,
            "score": score,
            "errors": errors,
            "passed": score >= 75
        }
    
    def _is_authority_source(self, url: str) -> bool:
        """判斷URL是否來自權威來源"""
        authority_domains = [
            "pubmed.ncbi.nlm.nih.gov",
            "who.int",
            "fda.gov.tw",
            "fda.gov",
            "mayoclinic.org",
            "frontiersin.org",
        ]
        return any(domain in url.lower() for domain in authority_domains)
    
    def generate_json_output(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """生成最終的 G 系統 JSON"""
        plan = self.get_todays_plan()
        validation = self.validate_article(article)
        
        if not validation["passed"]:
            raise ValueError(f"驗證失敗: {', '.join(validation['errors'])}")
        
        return {
            "PublishDate": plan["date"],
            "DayInCycle": plan["day"],
            "Category": plan["category"],
            "Product": plan["product"],
            "SKU": plan["sku"],
            "Price": plan["price"],
            "MetaTitle": article["MetaTitle"],
            "MetaDescription": article["MetaDescription"],
            "TargetAudience": article["TargetAudience"],
            "ArticleBody": article["ArticleBody"],
            "WordCount": article["WordCount"],
            "References": article["References"],
            "Status": "Draft",
            "QualityScore": validation["score"]
        }
```

#### 2.2 添加 Azure 存儲模組

```python
import os
import json
from azure.data.tables import TableClient
from azure.identity import DefaultAzureCredential

class AzureStorageAdapter:
    """將 JSON 存儲到 Azure SQL"""
    
    def __init__(self):
        self.connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("未設置 AZURE_SQL_CONNECTION_STRING 環境變數")
    
    def store_article(self, article_json: Dict[str, Any]) -> bool:
        """存儲文章到 Azure SQL"""
        try:
            import pyodbc
            
            # 連接資料庫
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # SQL 插入語句
            sql = """
            INSERT INTO Articles (
                PublishDate, DayInCycle, Category, Product, SKU, Price,
                MetaTitle, MetaDescription, TargetAudience,
                ArticleBody, WordCount, References, Status, QualityScore,
                CreatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # 準備參數
            params = (
                article_json["PublishDate"],
                article_json["DayInCycle"],
                article_json["Category"],
                article_json["Product"],
                article_json["SKU"],
                article_json["Price"],
                article_json["MetaTitle"],
                article_json["MetaDescription"],
                article_json["TargetAudience"],
                article_json["ArticleBody"],
                article_json["WordCount"],
                json.dumps(article_json["References"], ensure_ascii=False),  # JSON 序列化
                article_json["Status"],
                article_json["QualityScore"]
            )
            
            # 執行插入
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        
        except Exception as e:
            print(f"Azure 存儲失敗: {str(e)}")
            raise
    
    def log_execution(self, task_name: str, status: str, message: str = ""):
        """記錄執行日誌"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task_name,
            "status": status,
            "message": message
        }
        print(json.dumps(log_entry, ensure_ascii=False))
```

#### 2.3 改造主執行函數

```python
async def daily_sungertain_article_task():
    """
    Cowork 每日任務執行函數
    調用順序：
    1. 取得今日計劃
    2. 生成文章 (調用 Claude)
    3. 驗證品質
    4. 轉換 JSON 格式
    5. 存儲到 Azure
    """
    
    adapter = CoworkGSystemAdapter()
    storage = AzureStorageAdapter()
    
    try:
        # Step 1: 取得今日計劃
        plan = adapter.get_todays_plan()
        print(f"今日計劃: Day {plan['day']} - {plan['category']} - {plan['product']}")
        
        # Step 2: 生成文章 (這裡應調用 Claude API 或 Skill)
        # 使用改造後的 Prompt
        article = await generate_article_with_claude(plan)
        print(f"文章生成完成: {article['WordCount']} 字")
        
        # Step 3: 驗證品質
        validation = adapter.validate_article(article)
        print(f"品質評分: {validation['score']}/100")
        
        if not validation["passed"]:
            storage.log_execution(
                task_name="daily-sungertain-article",
                status="FAILED",
                message=f"品質驗證失敗: {', '.join(validation['errors'])}"
            )
            raise ValueError(f"品質驗證失敗: {validation['errors']}")
        
        # Step 4: 轉換 JSON 格式
        output_json = adapter.generate_json_output(article)
        print(f"JSON 格式轉換完成")
        
        # Step 5: 存儲到 Azure
        success = storage.store_article(output_json)
        
        if success:
            storage.log_execution(
                task_name="daily-sungertain-article",
                status="SUCCESS",
                message=f"文章已存儲: {plan['date']} - {plan['category']}"
            )
            print(f"✅ 任務完成: {output_json['PublishDate']} - {output_json['Category']}")
        
        return output_json
    
    except Exception as e:
        storage.log_execution(
            task_name="daily-sungertain-article",
            status="ERROR",
            message=str(e)
        )
        raise
```

### 步驟3：更新 Cowork 環境配置

需要設置以下環境變數在 Cowork 中：

```bash
# Azure SQL 連接
AZURE_SQL_CONNECTION_STRING="Server=tcp:sungertain-db.database.windows.net,1433;Initial Catalog=ArticlesDB;Persist Security Info=False;User ID=sqladmin;Password=your_password;Encrypt=True;Connection Timeout=30;"

# 或使用 Managed Identity（推薦，更安全）
AZURE_SQL_SERVER="sungertain-db.database.windows.net"
AZURE_SQL_DATABASE="ArticlesDB"

# Claude API
ANTHROPIC_API_KEY="sk-ant-..."
```

### 步驟4：驗證 Azure SQL 表結構

```sql
-- 確保 Articles 表包含以下列
CREATE TABLE Articles (
    Id NVARCHAR(100) PRIMARY KEY,
    PublishDate DATE NOT NULL,
    DayInCycle INT NOT NULL,
    Category NVARCHAR(50) NOT NULL,
    Product NVARCHAR(100) NOT NULL,
    SKU NVARCHAR(50) NOT NULL,
    Price DECIMAL(10, 2),
    MetaTitle NVARCHAR(200) NOT NULL,
    MetaDescription NVARCHAR(500) NOT NULL,
    TargetAudience NVARCHAR(500),
    ArticleBody NVARCHAR(MAX) NOT NULL,
    WordCount INT NOT NULL,
    References NVARCHAR(MAX) NOT NULL,  -- JSON 格式
    Status NVARCHAR(20) DEFAULT 'Draft',
    QualityScore INT,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME,
    INDEX idx_date (PublishDate),
    INDEX idx_day (DayInCycle),
    INDEX idx_status (Status)
);
```

---

## 📊 輸出示例

### 完整的 JSON 輸出（Day 1）

```json
{
  "PublishDate": "2026-05-14",
  "DayInCycle": 1,
  "Category": "入門認識",
  "Product": "靈芝黑木耳露 (瓶)",
  "SKU": "FD-WOODEAR-001",
  "Price": 140,
  "MetaTitle": "靈芝黑木耳露功效與食用指南｜營養補充新選擇",
  "MetaDescription": "了解靈芝黑木耳露的營養價值、食用方法和健康益處。初學者必讀的完整指南。基於科學研究，幫助消費者安全有效地補充營養。適合初次接觸的消費者和健康愛好者參考。",
  "TargetAudience": "初次接觸靈芝或該產品的消費者，以及想深入了解黑木耳露營養價值的潛在客戶。特別適合關心健康養生、尋求科學指導的現代消費者。",
  "ArticleBody": "<h2>什麼是靈芝黑木耳露？</h2><p>靈芝黑木耳露是一款創新的健康飲品，結合了靈芝精華與黑木耳的營養價值...</p><h3>主要成分</h3><ul><li>靈芝多醣體</li><li>黑木耳膠質</li></ul><h3>健康益處</h3><p>根據多項科學研究...</p>",
  "WordCount": 850,
  "References": [
    {
      "title": "Ganoderma Lucidum Polysaccharides Promote Immune Function",
      "url": "https://pubmed.ncbi.nlm.nih.gov/xxxxx",
      "access_date": "2026-05-14",
      "eeat_explanation": "專業性：NIH國家衛生研究院研究團隊 | 權威性：同行評審發表 | 真實性：包含具體臨床數據 | 可信度：透明的研究方法論"
    },
    {
      "title": "Traditional Medicine Monographs: Ganoderma Lucidum",
      "url": "https://www.who.int/teams/traditional-complementary-and-integrative-medicine",
      "access_date": "2026-05-14",
      "eeat_explanation": "專業性：WHO傳統醫學專家 | 權威性：WHO官方認可 | 真實性：傳統應用與現代驗證 | 可信度：全球認可指南"
    }
  ],
  "Status": "Draft",
  "QualityScore": 92
}
```

---

## ✅ 改造檢查清單

### 第1週：Prompt 改造
- [ ] 編寫新 Prompt（含7日計劃、產品清單）
- [ ] 添加 MetaTitle/Description 詳細要求
- [ ] 添加 ArticleBody HTML 格式要求
- [ ] 添加 References EEAT 說明要求
- [ ] 測試 Prompt 生成品質

### 第2週：代碼改造
- [ ] 實現 CoworkGSystemAdapter 類
- [ ] 實現 AzureStorageAdapter 類
- [ ] 實現驗證邏輯
- [ ] 實現 JSON 轉換
- [ ] 單元測試

### 第3週：集成和部署
- [ ] 配置 Azure SQL 表
- [ ] 設置環境變數
- [ ] 集成 Claude API
- [ ] Cowork 定時任務配置
- [ ] 端到端測試
- [ ] 正式上線

---

## 📞 可能的問題和解決方案

### Q1: WordCount 計算不準確

**問題**：HTML 標籤被計入字數  
**解決**：在計算前提取純文字

```python
def count_words(html_content):
    from html.parser import HTMLParser
    
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
        
        def handle_data(self, data):
            self.text.append(data)
    
    extractor = TextExtractor()
    extractor.feed(html_content)
    text = ''.join(extractor.text)
    return len(text.replace(' ', ''))
```

### Q2: Azure 連接超時

**問題**：連接字串配置錯誤或防火牆  
**解決**：
1. 確認連接字串正確
2. 檢查 Azure SQL 防火牆設置
3. 添加客戶端 IP 到允許清單

### Q3: References 驗證失敗

**問題**：URL 不符合要求  
**解決**：使用預先驗證的 VERIFIED_SOURCES.md 中的來源

---

## 📈 性能指標

改造完成後預期達到：

| 指標 | 目標 |
|------|------|
| 文章生成時間 | <3 分鐘 |
| 品質及格率 | ≥90% |
| 平均 QualityScore | ≥85/100 |
| Azure 存儲時間 | <10 秒 |
| 每月成本 | $50-80 |

---

## 版本追蹤

| 版本 | 描述 | 狀態 |
|------|------|------|
| v1.0 | 原始 Skill | ✅ 完成 |
| v1.1 | G系統適配版 | 🔄 開發中 |
| v1.2 | 性能優化版 | 📋 計劃中 |

---

**最後更新**：2026-05-14  
**狀態**：準備實施
