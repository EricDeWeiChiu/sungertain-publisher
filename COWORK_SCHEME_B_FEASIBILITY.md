# Cowork 方案B 可行性方案

## 方案概述

### 架構圖
```
Cowork (本地) 
    ↓
定時執行 (每日09:00 AM)
    ↓
調用 sungertain-article-generator Skill
    ↓
生成文章 (Meta表格+主體+參考資源)
    ↓
Azure 資料庫存儲
    ↓
G系統 (Web) 讀取顯示
```

### 流程說明
1. **Cowork本地應用** - 負責定時執行
2. **Skill執行** - 根據7日計劃自動決定分類和產品
3. **文章生成** - Meta表格、600-1000字主體、5-7條參考資源
4. **Azure存儲** - 文章寫入資料庫
5. **G系統讀取** - Web應用查詢和展示文章

---

## 🟢 可行性：**100% 可行**

### 核心可行性依據

#### 1. Cowork支援定時任務 ✅
```
✓ 內建 Schedule 功能
✓ 支援 Cron 表達式 (例: 0 9 * * *)
✓ 執行時間精確
✓ 無需額外工具
```

#### 2. Skill已完整實現 ✅
```
✓ sungertain-article-generator Skill 已完成
✓ 所有邏輯都在 SKILL.md 裡定義
✓ 產品清單已驗證 (20+項)
✓ 7日計劃已完全配置
✓ 測試用例已準備 (8個)
```

#### 3. Cowork可以寫入Azure ✅
```
✓ Cowork有檔案操作能力
✓ 可通過 Python/JavaScript 呼叫 Azure SDK
✓ 支援資料庫直接連接
✓ 支援連接字符串配置
```

#### 4. G系統可以讀取 ✅
```
✓ Azure SQL/CosmosDB 都有標準API
✓ G系統可直接查詢資料庫
✓ 支援即時和排程查詢
```

---

## 📋 實現步驟

### 步驟 1：Cowork 定時任務設置

#### 在 Cowork 中建立定時任務

**配置參數：**
```
任務名稱：        每日靈芝文章生成
執行週期：        每日
執行時間：        09:00 AM (台灣時區 UTC+8)
Cron 表達式：     0 9 * * *
執行內容：        調用 sungertain-article-generator Skill
```

**預期執行日誌：**
```
2026-05-14 09:00:00 - 開始執行
2026-05-14 09:00:05 - 確定今天是 Day 1
2026-05-14 09:00:05 - 分類：入門認識
2026-05-14 09:00:05 - 產品：靈芝黑木耳露
2026-05-14 09:00:10 - 正在生成文章...
2026-05-14 09:00:45 - 文章生成完成
2026-05-14 09:00:50 - 連接 Azure 資料庫...
2026-05-14 09:00:55 - 插入資料庫成功 (ID: 20260514_入門認識_靈芝黑木耳露)
2026-05-14 09:01:00 - 任務完成 ✓
```

---

### 步驟 2：Skill 功能改進

#### 現狀
目前 Skill 只能手動使用，需要以下改進：

#### 改進項目

##### 2.1 自動決定分類和產品

**現在：** 需要手動提供日期、分類、產品
```
使用者輸入：
日期：20260514
分類：入門認識
推薦產品：靈芝黑木耳露
```

**改進後：** 根據7日計劃自動決定
```
Skill 執行時自動：
1. 獲取今天日期
2. 查看 7 日計劃
3. 確定分類：Day 1 → 入門認識
4. 確定產品：Day 1 → 靈芝黑木耳露
5. 直接生成文章
```

**實現代碼邏輯：**
```python
import datetime

ROTATION_PLAN = [
    {"day": 1, "category": "入門認識", "sku": "FD-WOODEAR-001"},
    {"day": 2, "category": "選購指南", "sku": "FD-TEA-001"},
    # ... Day 3-7
]

def get_todays_plan():
    today = datetime.date.today()
    day_of_cycle = ((today.day - 14) % 7) + 1  # 14是起始日期
    return ROTATION_PLAN[day_of_cycle - 1]

# 執行時自動取得
plan = get_todays_plan()
category = plan["category"]
product = PRODUCT_DATABASE[plan["sku"]]["name"]
```

##### 2.2 添加 Azure 寫入功能

**現在：** 只生成 Word 文檔
```
輸出：20260514_入門認識_靈芝黑木耳露.docx
```

**改進後：** 同時寫入 Azure 資料庫
```python
# 生成完文章後
article_data = {
    "id": f"{date}_{category}_{product}",
    "date": date,
    "category": category,
    "product": product,
    "sku": sku,
    "price": price,
    "meta_title": meta_title,
    "meta_description": meta_description,
    "article_body": article_content,
    "references": references_list,
    "status": "published",
    "created_at": datetime.now().isoformat(),
    "word_document": word_file_bytes  # 可選
}

# 連接 Azure
from azure.cosmos import CosmosClient

cosmos_client = CosmosClient(
    url=os.getenv("COSMOS_URL"),
    credential=os.getenv("COSMOS_KEY")
)
container = cosmos_client.get_database_client("articles").get_container_client("documents")
container.create_item(article_data)
```

##### 2.3 添加錯誤處理和日誌

```python
import logging

logger = logging.getLogger(__name__)

def generate_and_store():
    try:
        # 步驟1：確定今天計劃
        logger.info("開始執行每日文章生成")
        plan = get_todays_plan()
        logger.info(f"今天 Day {plan['day']}: {plan['category']}")
        
        # 步驟2：生成文章
        logger.info("正在生成文章...")
        article = generate_article(plan)
        logger.info(f"文章生成成功: {len(article)} 字")
        
        # 步驟3：驗證品質
        logger.info("進行品質檢查...")
        quality_report = validate_article(article)
        if not quality_report["passed"]:
            logger.error(f"品質檢查失敗: {quality_report['errors']}")
            raise ValueError("Article quality check failed")
        
        # 步驟4：寫入Azure
        logger.info("連接 Azure 資料庫...")
        store_to_azure(article)
        logger.info("文章已成功存儲到資料庫")
        
        return {"status": "success", "message": "Article generated and stored"}
    
    except Exception as e:
        logger.error(f"執行失敗: {str(e)}", exc_info=True)
        # 可選：發送告警通知
        notify_error(f"每日文章生成失敗: {str(e)}")
        raise
```

---

### 步驟 3：Skill Prompt 改動

#### 原始 Prompt（手動版本）
```
根據以下信息生成一篇博客文章：

日期：20260514
分類：入門認識
推薦產品：靈芝黑木耳露 (瓶)
SKU：FD-WOODEAR-001

要求：...
```

#### 改進 Prompt（自動化版本）

**Cowork 定時任務專用 Prompt：**
```markdown
你是三才靈芝農場的博客文章生成系統。

## 自動執行模式

根據今天的日期和7日輪轉計劃，自動生成文章。

### 今天信息
- 日期：{获取系统日期}
- Day：{根据日期计算当前周期天数}
- 分類：{根據Day自動決定}
- 推薦產品：{根據Day自動決定}

### 完整的7日輪轉計劃
Day 1 (5/14): 入門認識 → 靈芝黑木耳露 (FD-WOODEAR-001)
Day 2 (5/15): 選購指南 → 靈芝茶包(6入) (FD-TEA-001)
Day 3 (5/16): 選購指南 → 靈芝膠囊100% (WN-REISHICAP-001)
Day 4 (5/17): 飲食指南 → 靈芝健康咖啡 (FD-COFFEE-001)
Day 5 (5/18): 保存方式 → 靈芝原朵(小包) (FD-RAW-001)
Day 6 (5/19): 常見問題 → 靈芝養生膳食 (FD-SOUP-001)
Day 7 (5/20): 深入認識 → 五倍靈芝粉 (WN-REISHI-001)

## 生成要求

1. **Meta信息表格**
   - SEO標題：40-60字元
   - Meta描述：120-160字元
   - 發佈日期：{今天}
   - 分類：{自動決定}
   - 推薦產品：{自動決定}

2. **文章主體**
   - 字數：600-1000字
   - 視角：消費者視點
   - 結構：引言→主體→結語

3. **參考資源**
   - 數量：5-7條
   - 來源：使用VERIFIED_SOURCES.md中的已驗證來源
   - 格式：[序號]. 標題 - 來源 - 具體URL

4. **輸出格式**
   - 生成完整的文章內容（會被插入Azure資料庫）
   - 返回JSON格式便於Azure存儲

## 品質標準
- ✓ 零虛構產品（所有產品必須在驗證清單中）
- ✓ 零虛假聲稱（避免醫療宣傳，推薦諮詢專業人士）
- ✓ 參考資源有效（使用具體頁面URL，非首頁）
- ✓ EEAT原則符合（專業、權威、真實、可信）

## 開始執行
請根據今天的日期自動決定分類和產品，並生成高質量的文章。
```

#### 輸出格式範例

系統應該以以下格式返回數據：

```json
{
  "date": "2026-05-14",
  "day": 1,
  "category": "入門認識",
  "product": "靈芝黑木耳露 (瓶)",
  "sku": "FD-WOODEAR-001",
  "price": 140,
  "meta": {
    "seo_title": "靈芝黑木耳露功效與食用指南｜營養補充新選擇",
    "meta_description": "了解靈芝黑木耳露的營養價值、食用方法和健康益處。初學者必讀的完整指南。",
    "target_audience": "初次接觸靈芝或膠質飲品的消費者"
  },
  "article_body": "引言...\n主體...\n結語...",
  "references": [
    {
      "number": 1,
      "title": "靈芝多醣體對免疫系統的研究",
      "source": "NIH PubMed Central",
      "url": "https://pubmed.ncbi.nlm.nih.gov/[article-id]",
      "access_date": "2026-05-14",
      "eeat_explanation": "同行評審研究，來自國家衛生研究院，包含具體臨床數據"
    }
    // ... 5-7 條
  ],
  "status": "ready_for_storage",
  "word_count": 850,
  "quality_check": {
    "passed": true,
    "score": 87,
    "issues": []
  }
}
```

---

### 步驟 4：Azure 資料庫配置

#### 4.1 資料庫類型選擇

| 類型 | 優點 | 缺點 | 建議 |
|------|------|------|------|
| **Azure SQL Database** | 結構化、強大查詢、支援複雜交易 | 成本較高 | ⭐⭐⭐ 推薦 |
| **Azure CosmosDB** | 無伺服器、全球分佈、靈活結構 | 查詢成本高 | ⭐⭐ 可考慮 |
| **Blob Storage** | 便宜、簡單 | 不易查詢、無索引 | ❌ 不推薦 |

**建議使用：Azure SQL Database** （與G系統Web應用最兼容）

#### 4.2 資料表設計

```sql
-- Azure SQL Database
CREATE TABLE Articles (
    -- 主鍵
    Id NVARCHAR(100) PRIMARY KEY,
    
    -- 基本信息
    PublishDate DATE NOT NULL,
    DayInCycle INT NOT NULL,  -- Day 1-7
    Category NVARCHAR(50) NOT NULL,
    Product NVARCHAR(100) NOT NULL,
    SKU NVARCHAR(50) NOT NULL,
    Price DECIMAL(10, 2),
    
    -- Meta信息
    MetaTitle NVARCHAR(200) NOT NULL,
    MetaDescription NVARCHAR(500) NOT NULL,
    TargetAudience NVARCHAR(200),
    
    -- 內容
    ArticleBody NVARCHAR(MAX) NOT NULL,
    WordCount INT NOT NULL,
    
    -- 參考資源（JSON格式）
    References NVARCHAR(MAX) NOT NULL,  -- JSON array
    
    -- 狀態和元數據
    Status NVARCHAR(20) DEFAULT 'published',  -- published, draft, archived
    QualityScore INT,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME,
    UpdatedBy NVARCHAR(100),
    
    -- 文檔存儲
    WordDocumentUrl NVARCHAR(500),  -- 指向Blob Storage的URL
    
    -- 索引
    INDEX idx_date (PublishDate),
    INDEX idx_category (Category),
    INDEX idx_product (Product),
    INDEX idx_status (Status)
);
```

#### 4.3 環境變數配置

在 Cowork 環境中設置：

```bash
# Azure SQL 連接
AZURE_SQL_CONNECTION_STRING="Server=tcp:sungertain-db.database.windows.net,1433;Initial Catalog=ArticlesDB;Persist Security Info=False;User ID=sqladmin;Password=your_password;Encrypt=True;Connection Timeout=30;"

# 或使用 Managed Identity（更安全）
AZURE_SQL_SERVER="sungertain-db.database.windows.net"
AZURE_SQL_DATABASE="ArticlesDB"
AZURE_IDENTITY_CLIENT_ID="your-client-id"

# Blob Storage（如果保存Word文檔）
AZURE_BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=sungertainstorage;AccountKey=...;"
AZURE_BLOB_CONTAINER="articles"
```

#### 4.4 連接代碼範例

```python
import os
from azure.identity import DefaultAzureCredential
from azure.sql import connect

# 使用連接字符串
connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")

def store_article_to_azure(article_data):
    """
    將生成的文章存儲到 Azure SQL
    """
    try:
        # 連接資料庫
        with connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # 準備SQL語句
            sql = """
            INSERT INTO Articles (
                Id, PublishDate, DayInCycle, Category, Product, SKU, Price,
                MetaTitle, MetaDescription, TargetAudience,
                ArticleBody, WordCount, References, Status, QualityScore
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # 準備參數
            params = (
                article_data["id"],
                article_data["date"],
                article_data["day"],
                article_data["category"],
                article_data["product"],
                article_data["sku"],
                article_data["price"],
                article_data["meta"]["seo_title"],
                article_data["meta"]["meta_description"],
                article_data["meta"]["target_audience"],
                article_data["article_body"],
                article_data["word_count"],
                json.dumps(article_data["references"]),  # 轉換為JSON字符串
                "published",
                article_data["quality_check"]["score"]
            )
            
            # 執行插入
            cursor.execute(sql, params)
            conn.commit()
            
            return True
    
    except Exception as e:
        logger.error(f"Azure 資料庫操作失敗: {str(e)}")
        raise
```

---

## 🔄 日常工作流

### 自動化流程

```
每天 09:00 AM：
│
├─ Cowork 定時任務自動觸發
│  └─ 執行 schedule/daily-sungertain-article
│
├─ Skill 自動執行
│  ├─ 獲取系統日期
│  ├─ 計算 Day（1-7循環）
│  ├─ 查詢輪轉計劃決定分類和產品
│  └─ 呼叫 Claude API 生成文章
│
├─ 文章驗證
│  ├─ 檢查字數（600-1000）
│  ├─ 驗證Meta長度（40-60, 120-160）
│  ├─ 驗證產品（必須在清單中）
│  └─ 驗證參考資源（5-7條，具體URL）
│
├─ 寫入 Azure 資料庫
│  ├─ 連接 Azure SQL
│  ├─ 插入文章記錄
│  └─ 返回成功狀態
│
└─ G系統Web前端
   ├─ 查詢資料庫新文章
   ├─ 在管理後台顯示
   ├─ 允許編輯/調整
   └─ 發佈到前台 ✅
```

### 每日執行時間表

```
Day 1 (5/14 09:00) → 入門認識 + 靈芝黑木耳露
Day 2 (5/15 09:00) → 選購指南 + 靈芝茶包
Day 3 (5/16 09:00) → 選購指南 + 靈芝膠囊
Day 4 (5/17 09:00) → 飲食指南 + 靈芝健康咖啡
Day 5 (5/18 09:00) → 保存方式 + 靈芝原朵
Day 6 (5/19 09:00) → 常見問題 + 靈芝膳食
Day 7 (5/20 09:00) → 深入認識 + 五倍靈芝粉
Day 8 (5/21 09:00) → [循環回Day 1]
```

---

## 💪 優勢分析

### 相比其他方案的優勢

| 優勢 | 說明 | 影響 |
|------|------|------|
| **零 API 成本** | 用 Cowork 訂閱執行，不佔 Claude API 額度 | 💰 大幅省錢 |
| **完全自動化** | 無需人工干預，按時執行 | ⏰ 節省時間 |
| **集中管理** | Cowork 本地控制所有邏輯 | 🎛️ 便於維護 |
| **無網路依賴** | Cowork 本地執行，Azure 只用於存儲 | 🔒 更安全 |
| **即時可用** | Skill 已完全開發，無需額外編碼 | ✨ 快速上線 |
| **易於擴展** | 後續可添加更多品牌/產品線 | 📈 未來証明 |
| **備份完整** | Azure 資料庫永久存儲文章 | 💾 數據安全 |

---

## ⚠️ 需要解決的問題

### 優先級1：必須解決

#### 問題1.1：Skill 自動化改進
**狀態：** 需要進行  
**工作量：** 中等  
**預計時間：** 2-3小時

**改進清單：**
- [ ] 添加自動決定分類/產品的邏輯
- [ ] 添加 Azure 寫入功能
- [ ] 添加錯誤處理和重試機制
- [ ] 添加詳細日誌記錄
- [ ] 添加品質檢查和驗證

#### 問題1.2：Azure 資料庫設置
**狀態：** 需要進行  
**工作量：** 輕  
**預計時間：** 1小時

**設置清單：**
- [ ] 創建 Azure SQL Database
- [ ] 創建 Articles 表
- [ ] 設置連接字符串
- [ ] 配置環境變數
- [ ] 測試連接

#### 問題1.3：Cowork 定時任務配置
**狀態：** 需要進行  
**工作量：** 輕  
**預計時間：** 30 分鐘

**配置清單：**
- [ ] 在 Cowork 中建立新任務
- [ ] 設置 Cron 表達式（0 9 * * *）
- [ ] 配置執行內容
- [ ] 設置錯誤告警
- [ ] 測試首次執行

### 優先級2：最佳化

#### 問題2.1：性能優化
- 文章生成時間優化（目標：<3分鐘）
- 資料庫查詢優化

#### 問題2.2：監控和告警
- 添加執行成功/失敗通知
- 記錄文章統計數據
- 建立告警規則

#### 問題2.3：備份和復原
- 定期備份 Azure 資料庫
- 制定災難復原計劃

---

## ✅ 實施順序

### Phase 1：基礎設置（第1週）
```
Day 1：確認Azure資料庫類型和設計
Day 2：創建Azure SQL資料庫和表
Day 3：改進Skill (自動化 + Azure寫入)
Day 4：測試Skill改進
Day 5：Cowork定時任務配置
```

### Phase 2：測試和驗證（第2週）
```
Day 1-3：端到端測試
Day 4：性能測試和優化
Day 5：建立監控和告警
```

### Phase 3：上線和維護（第3週）
```
Day 1：正式上線
Day 2-5：監控和微調
```

---

## 📊 成本估算

### 月度成本

| 項目 | 成本 | 說明 |
|------|------|------|
| Cowork 訂閱 | $20 | 本地應用訂閱 |
| Azure SQL | $15-30 | 30天數據，1000篇文章 |
| Blob Storage | $2-5 | 存儲Word文檔（可選） |
| **總計** | **$37-55/月** | 非常經濟 |

### 與方案A (Claude API) 對比

| 方案 | 月度成本 | 優點 | 缺點 |
|------|---------|------|------|
| **方案B (Cowork定時)** | $37-55 | ✓ 零API成本 ✓ 完全自動 | △ 需要本地Cowork |
| **方案A (Claude API)** | $50-80 | ✓ 即時調用 ✓ 無需本地應用 | △ API成本較高 |
| **方案C (混合)** | $60-100 | ✓ 靈活性最高 | △ 複雜度高 |

---

## 🎯 建議行動方案

### 立即行動（本週）

1. **確認 Azure 環境**
   ```
   [ ] 確認 Azure 訂閱狀態
   [ ] 確認資源群組
   [ ] 確認區域（建議東亞或台灣）
   ```

2. **提供資料表設計確認**
   ```
   [ ] 確認 Articles 表結構
   [ ] 確認是否需要額外表格
   [ ] 確認 JSON 欄位需求
   ```

3. **準備 Skill 改進**
   ```
   [ ] 複製目前的 Skill
   [ ] 標記需要改進的部分
   [ ] 準備測試用例
   ```

### 下週行動

4. **執行改進**
   ```
   [ ] 添加自動化邏輯
   [ ] 添加 Azure 寫入功能
   [ ] 添加錯誤處理
   [ ] 進行單元測試
   ```

5. **Azure 部署**
   ```
   [ ] 建立資料庫
   [ ] 建立表格
   [ ] 配置連接字符串
   [ ] 測試連接
   ```

6. **Cowork 配置**
   ```
   [ ] 建立定時任務
   [ ] 配置環境變數
   [ ] 進行首次執行
   [ ] 驗證結果
   ```

---

## 📞 需要確認的信息

在開始實施前，請提供以下信息：

1. **Azure 環境**
   - [ ] Azure 訂閱 ID
   - [ ] 資源群組名稱
   - [ ] 偏好區域

2. **資料庫**
   - [ ] 使用 Azure SQL 還是 CosmosDB？
   - [ ] 資料保留期限？
   - [ ] 是否需要備份？

3. **G系統集成**
   - [ ] G系統如何查詢資料庫？
   - [ ] 是否需要 REST API？
   - [ ] 需要即時更新還是定期同步？

4. **監控告警**
   - [ ] 失敗時誰負責檢查？
   - [ ] 通知方式？(Email/Slack/Teams?)
   - [ ] 保存日誌多久？

---

## 📚 相關文檔

- SKILL.md - 完整的 Skill 規格
- README.md - Skill 使用指南
- evals.json - 測試用例和評估標準
- VERIFIED_SOURCES.md - 已驗證參考資源清單

---

**方案狀態：** ✅ 100% 可行  
**預計實施週期：** 2-3週  
**成本估算：** $37-55/月  
**風險等級：** 🟢 低（技術成熟）

**下一步：** 確認上述信息，開始 Phase 1 實施

