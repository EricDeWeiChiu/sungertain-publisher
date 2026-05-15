# Azure SQL設置指南

## 📋 Articles 表格結構

此表格用於存儲生成的文章及其元數據。

### SQL建立語句

```sql
-- 建立Articles表格
CREATE TABLE Articles (
    ArticleID NVARCHAR(50) PRIMARY KEY,
    PublishDate DATE NOT NULL,
    Category NVARCHAR(50) NOT NULL,
    MetaTitle NVARCHAR(60) NOT NULL,
    MetaDescription NVARCHAR(160) NOT NULL,
    ArticleBody NVARCHAR(MAX) NOT NULL,
    RecommendedProduct NVARCHAR(200) NOT NULL,
    ProductSKU NVARCHAR(20) NOT NULL,
    TargetAudience NVARCHAR(MAX),
    DayInCycle INT NOT NULL,
    QualityScore INT NOT NULL CHECK (QualityScore >= 0 AND QualityScore <= 100),
    Status NVARCHAR(20) DEFAULT 'pending',  -- pending, approved, published, archived
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    LastModifiedAt DATETIME2 DEFAULT GETUTCDATE(),
    CreatedBy NVARCHAR(100),
    ModifiedBy NVARCHAR(100),
    Notes NVARCHAR(MAX)
);

-- 建立索引以加速查詢
CREATE INDEX IDX_PublishDate ON Articles(PublishDate);
CREATE INDEX IDX_Category ON Articles(Category);
CREATE INDEX IDX_DayInCycle ON Articles(DayInCycle);
CREATE INDEX IDX_Status ON Articles(Status);
CREATE INDEX IDX_QualityScore ON Articles(QualityScore);

-- 建立複合索引用於常見查詢
CREATE INDEX IDX_Date_Status ON Articles(PublishDate, Status);
CREATE INDEX IDX_Category_Score ON Articles(Category, QualityScore DESC);
```

### 欄位說明

| 欄位 | 類型 | 說明 | 必填 |
|------|------|------|------|
| ArticleID | NVARCHAR(50) | 唯一識別符 (YYYYMMDD_分類_簡化產品) | ✅ |
| PublishDate | DATE | 發佈日期 (YYYY-MM-DD) | ✅ |
| Category | NVARCHAR(50) | 分類 (6種之一) | ✅ |
| MetaTitle | NVARCHAR(60) | SEO標題 (40-60字元) | ✅ |
| MetaDescription | NVARCHAR(160) | 元描述 (120-160字元) | ✅ |
| ArticleBody | NVARCHAR(MAX) | 文章主體 (HTML格式，600-1000字) | ✅ |
| RecommendedProduct | NVARCHAR(200) | 推薦產品完整名稱 | ✅ |
| ProductSKU | NVARCHAR(20) | 產品SKU代碼 | ✅ |
| TargetAudience | NVARCHAR(MAX) | 目標受眾描述 | ❌ |
| DayInCycle | INT | 7天周期中的日期 (1-7) | ✅ |
| QualityScore | INT | 品質分數 (0-100，≥75及格) | ✅ |
| Status | NVARCHAR(20) | 文章狀態 | ✅ |
| CreatedAt | DATETIME2 | 建立時間 (UTC) | ✅ |
| LastModifiedAt | DATETIME2 | 最後修改時間 (UTC) | ✅ |
| CreatedBy | NVARCHAR(100) | 建立者 (Claude/Cowork) | ❌ |
| ModifiedBy | NVARCHAR(100) | 最後修改者 | ❌ |
| Notes | NVARCHAR(MAX) | 備註欄 | ❌ |

---

## 📋 ExecutionLogs 表格結構

用於記錄每次文章生成的執行日誌。

```sql
-- 建立執行日誌表格
CREATE TABLE ExecutionLogs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    ExecutionDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    GeneratedArticleID NVARCHAR(50),
    DayInCycle INT,
    Category NVARCHAR(50),
    RecommendedProduct NVARCHAR(200),
    QualityScore INT,
    Status NVARCHAR(20),  -- success, failed, partial
    ErrorMessage NVARCHAR(MAX),
    WarningMessages NVARCHAR(MAX),
    ExecutionTime INT,  -- 執行時間（秒）
    CloudProvider NVARCHAR(20) DEFAULT 'Cowork',  -- Cowork, API, etc
    UserID NVARCHAR(100),
    Notes NVARCHAR(MAX),
    FOREIGN KEY (GeneratedArticleID) REFERENCES Articles(ArticleID)
);

-- 建立索引
CREATE INDEX IDX_ExecutionDate ON ExecutionLogs(ExecutionDate);
CREATE INDEX IDX_GeneratedArticleID ON ExecutionLogs(GeneratedArticleID);
CREATE INDEX IDX_Status ON ExecutionLogs(Status);
CREATE INDEX IDX_DayInCycle ON ExecutionLogs(DayInCycle);
```

### 欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| LogID | INT | 自動遞增主鍵 |
| ExecutionDate | DATETIME2 | 執行日期時間 |
| GeneratedArticleID | NVARCHAR(50) | 關聯的文章ID |
| DayInCycle | INT | 7天周期中的日期 |
| Category | NVARCHAR(50) | 文章分類 |
| RecommendedProduct | NVARCHAR(200) | 推薦產品 |
| QualityScore | INT | 品質分數 |
| Status | NVARCHAR(20) | 執行狀態 |
| ErrorMessage | NVARCHAR(MAX) | 錯誤詳情 |
| WarningMessages | NVARCHAR(MAX) | 警告信息 |
| ExecutionTime | INT | 執行耗時（秒） |
| CloudProvider | NVARCHAR(20) | 執行來源 |
| UserID | NVARCHAR(100) | 用戶ID |
| Notes | NVARCHAR(MAX) | 備註 |

---

## 📋 References 表格結構

用於存儲參考資源（非JSON內嵌）。

```sql
-- 建立參考資源表格
CREATE TABLE References (
    ReferenceID INT IDENTITY(1,1) PRIMARY KEY,
    ArticleID NVARCHAR(50) NOT NULL,
    SequenceNumber INT NOT NULL,  -- 1-7
    Title NVARCHAR(500) NOT NULL,
    URL NVARCHAR(2000) NOT NULL,
    AuthorityLevel INT NOT NULL,  -- 1, 2, or 3
    PublishedDate DATE,
    AccessedDate DATE NOT NULL,
    EEATExplanation NVARCHAR(MAX),
    Domain NVARCHAR(200),
    IsVerified BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    FOREIGN KEY (ArticleID) REFERENCES Articles(ArticleID),
    UNIQUE(ArticleID, SequenceNumber)
);

-- 建立索引
CREATE INDEX IDX_ArticleID ON References(ArticleID);
CREATE INDEX IDX_URL ON References(URL);
CREATE INDEX IDX_AuthorityLevel ON References(AuthorityLevel);
```

---

## 🔑 連接字符串格式

### Azure SQL Database 連接字符串

```
Server=tcp:<server-name>.database.windows.net,1433;Initial Catalog=<database-name>;Persist Security Info=False;User ID=<username>;Password=<password>;Encrypt=True;Connection Timeout=30;
```

### 環境變數設置

在Cowork定時任務中設置以下環境變數：

```bash
# Azure SQL
AZURE_SQL_CONNECTION_STRING=Server=tcp:YOUR_SERVER.database.windows.net,1433;Initial Catalog=gSystem;User ID=YOUR_USER;Password=YOUR_PASSWORD;Encrypt=True;Connection Timeout=30;

AZURE_SQL_DATABASE=gSystem
AZURE_SQL_TABLE=Articles
AZURE_SQL_EXECUTIONLOGS_TABLE=ExecutionLogs

# Azure Blob Storage (可選，用於備份)
AZURE_BLOB_CONTAINER=articles
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
```

---

## 🛠️ 設置步驟

### 1️⃣ 在Azure Portal建立SQL資料庫

```
1. 前往 portal.azure.com
2. 點擊「建立資源」→ SQL資料庫
3. 設置：
   - 資料庫名稱：gSystem
   - 服務器：建立新伺服器
   - 計算+儲存：標準層 (B/S1級別)
4. 點擊「檢視+建立」→「建立」
```

### 2️⃣ 執行SQL指令碼

```
1. 前往 Azure Portal → SQL資料庫 → gSystem
2. 點擊「查詢編輯器」
3. 複製上面的SQL建立語句
4. 貼入並執行
5. 驗證表格已建立
```

### 3️⃣ 配置防火牆規則

```
1. 前往 SQL伺服器 設置
2. 點擊「防火牆和虛擬網路」
3. 新增規則允許您的IP地址
   - 開始IP：YOUR_IP
   - 結束IP：YOUR_IP
4. 儲存
```

### 4️⃣ 測試連接

```python
import pyodbc

connection_string = "Server=tcp:YOUR_SERVER.database.windows.net,1433;Initial Catalog=gSystem;User ID=YOUR_USER;Password=YOUR_PASSWORD;Encrypt=True;Connection Timeout=30;"

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Articles")
    print("✓ 連接成功")
    conn.close()
except Exception as e:
    print(f"❌ 連接失敗：{e}")
```

---

## 📊 查詢範例

### 查詢今日文章

```sql
SELECT * FROM Articles 
WHERE PublishDate = CAST(GETDATE() AS DATE)
ORDER BY CreatedAt DESC;
```

### 查詢品質分數≥75的文章

```sql
SELECT ArticleID, QualityScore, Category, PublishDate
FROM Articles
WHERE QualityScore >= 75
ORDER BY QualityScore DESC;
```

### 查詢執行統計

```sql
SELECT 
    CAST(ExecutionDate AS DATE) as ExecutionDate,
    COUNT(*) as TotalExecutions,
    SUM(CASE WHEN Status = 'success' THEN 1 ELSE 0 END) as SuccessCount,
    AVG(ExecutionTime) as AvgExecutionTime
FROM ExecutionLogs
GROUP BY CAST(ExecutionDate AS DATE)
ORDER BY ExecutionDate DESC;
```

### 查詢按分類統計

```sql
SELECT 
    Category,
    COUNT(*) as ArticleCount,
    AVG(QualityScore) as AvgScore,
    MIN(QualityScore) as MinScore,
    MAX(QualityScore) as MaxScore
FROM Articles
GROUP BY Category
ORDER BY AvgScore DESC;
```

---

## ⚠️ 常見問題

### Q: 如何選擇資料庫層級？
**A:** 
- 開發/測試：Basic層（$5/月）
- 小型生產：S0/S1標準層（$15-30/月）
- 中型生產：S2/S3層（$60-150/月）

三才靈芝農場每日1篇文章，建議**S0層**即可。

### Q: 如何備份資料？
**A:** Azure SQL自動備份35天。可配置：
1. 點擊「備份」→「設定備份策略」
2. 設置長期保留（每週/月/年）
3. 或使用Blob Storage進行備份

### Q: 如何優化查詢性能？
**A:**
- 已建立關鍵欄位的索引
- 複合索引用於常見查詢
- 定期檢查執行計劃
- 考慮分區（如文章量超過100萬）

### Q: 如何監控成本？
**A:**
- Azure Portal → 成本管理
- 設定預算警報（$100/月）
- 查看詳細使用情況
- 調整儲存層級

---

## 🔐 安全最佳實踐

1. **不要在程式碼中硬編碼密碼**
   - 使用環境變數
   - 或使用Azure Key Vault

2. **加密敏感數據**
   - 已啟用SQL加密 (TDE)
   - 使用HTTPS連接

3. **定期備份**
   - Azure自動每日備份
   - 設置長期保留策略

4. **監控存取**
   - 啟用審計日誌
   - 設置IP防火牆

---

**版本：1.0**  
**最後更新：2026-05-14**
