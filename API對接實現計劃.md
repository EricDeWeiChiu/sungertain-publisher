# Cowork → G系統 API 對接實現計劃

**文件日期**：2026-05-15  
**狀態**：準備實施

---

## 📌 API 核心信息摘要

| 項目 | 內容 |
|------|------|
| **API 端點** | https://sungertain.deweichiu.com/api/articles/publish |
| **HTTP 方法** | POST |
| **Content-Type** | application/json |
| **認證方式** | Bearer Token (Header) |
| **API Key** | gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026 |
| **成功狀態碼** | HTTP 201 Created |
| **每分鐘限額** | 10 次調用 |
| **單個請求限制** | 10 MB |
| **Token 有效期** | 永久 |

---

## 📋 必需欄位對應表

我們的文章數據 → API 請求欄位：

| 我們的來源 | API 欄位 | 資料型態 | 說明 |
|---------|---------|--------|------|
| .docx Meta 表格 - SEO 標題 | `meta_title` | String | 55-65 字 |
| .docx Meta 表格 - SEO 描述 | `meta_description` | String | 160 字以內 |
| .docx 文章內容 | `article_body` | String (HTML) | 需轉換為 HTML |
| .docx Meta 表格 - 分類 | `category` | String | 6 個允許值之一 |
| 當前日期 | `publish_date` | ISO 8601 | 格式：2026-05-15T09:00:00+08:00 |
| 固定值 | `status` | String | "draft"（待審核） |
| .docx Meta 表格 - 推薦產品 | `related_products` | Array | ["靈芝茶包 (36入) -大"] |
| 計算值（Day 1-7） | `day_in_cycle` | Integer | 1-7 |
| .docx 超連結 | `references` | Array | [{url, title, authority_score}] |
| 固定值 | `created_by` | String | "cowork_system" |

### 允許的分類值
```
- 選購指南 ✓ (Day 2, 3)
- 入門認識 ✓ (Day 1)
- 產品評測 
- 使用心得 
- 健康知識 
- 其他
```

### 允許的狀態值
```
- draft      → 草稿，等待編輯審核（推薦）
- published  → 立即發布
- scheduled  → 排程發布（搭配 publish_date）
```

---

## 🛠️ 實現步驟

### Phase 1: 環境設定（1-2 小時）

#### Step 1.1: 保存 API 認證信息
```
位置: ~/.env 或 應用設定
變數:
  G_SYSTEM_API_URL=https://sungertain.deweichiu.com/api/articles/publish
  G_SYSTEM_API_KEY=gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026
```

#### Step 1.2: 安裝必要的 Python 庫
```bash
pip install requests python-docx --break-system-packages
```

---

### Phase 2: 開發 API 推送模組（2-3 小時）

#### Step 2.1: 建立 .docx → API 數據轉換函數

**需要實現的轉換邏輯：**

```python
def extract_docx_to_api_payload(docx_path, day_in_cycle):
    """
    將 .docx 文件提取為 API 所需格式
    
    輸入：
      - docx_path: .docx 文件路徑
      - day_in_cycle: 周期日數 (1-7)
    
    輸出：
      - dict: API payload
    """
    
    需要提取的內容：
    1. Meta 表格第 1 行：SEO 標題 → meta_title
    2. Meta 表格第 2 行：SEO 描述 → meta_description
    3. Meta 表格第 4 行：分類 → category
    4. Meta 表格第 5 行：推薦產品 → related_products (需轉為 Array)
    5. 文章正文段落 → article_body (需轉換為 HTML)
    6. 超連結清單 → references (抽取 URL、標題、評分)
    7. 當前日期 → publish_date (ISO 8601 格式)
    
    返回:
      {
        "meta_title": "...",
        "meta_description": "...",
        "article_body": "<h2>...</h2><p>...</p>...",
        "category": "選購指南",
        "tags": [],
        "related_products": ["靈芝茶包 (36入) -大"],
        "publish_date": "2026-05-15T09:00:00+08:00",
        "status": "draft",
        "day_in_cycle": 2,
        "quality_score": 85,
        "references": [
          {
            "url": "https://...",
            "title": "參考資源",
            "authority_score": 0.85
          }
        ],
        "created_by": "cowork_system"
      }
```

#### Step 2.2: 建立 API 推送函數

```python
def publish_to_g_system(api_payload):
    """
    將文章推送到 G 系統
    
    輸入：api_payload (來自 Step 2.1)
    
    返回：
      {
        "success": bool,
        "article_id": "A1B2C3D4",
        "audit_url": "https://...",
        "message": "..."
      }
    """
    
    功能：
    1. 驗證必需欄位
    2. 發送 POST 請求到 API 端點
    3. 處理三種回應：
       - 201: 成功 → 記錄 article_id 和 audit_url
       - 400: 驗證失敗 → 記錄錯誤信息
       - 401: 認證失敗 → 檢查 API Key
       - 429: 限流 → 重試機制
       - 500: 伺服器錯誤 → 重試邏輯
```

#### Step 2.3: 錯誤處理與重試機制

```
重試策略：
- 網路超時：重試 3 次，間隔 5 秒
- HTTP 429 (限流)：重試 5 次，間隔 60 秒
- HTTP 500：重試 3 次，間隔 10 秒
- 其他錯誤：記錄日誌，通知用戶

失敗後的備份：
- 將失敗的 payload 存入隊列
- 定期檢查隊列並重試
```

---

### Phase 3: 整合到定時任務（1-2 小時）

#### Step 3.1: 修改定時任務流程

```
現有流程：
  1. ✓ 生成 .docx 文件
  2. ✗ 保存到本地

新流程：
  1. ✓ 生成 .docx 文件
  2. ✓ 保存到本地
  3. 新增: 提取 .docx 數據
  4. 新增: 驗證必需欄位
  5. 新增: 調用 API 推送
  6. 新增: 記錄推送結果（成功/失敗）
```

#### Step 3.2: 日誌與監控

```
記錄信息：
- 文件生成時間
- 提取的 Meta 信息
- API 推送時間
- 返回的 article_id
- 審核 URL
- 任何錯誤信息

日誌位置：
- 成功: /Users/ericchiu/Documents/sungertain-design/G系統專案/logs/success.log
- 失敗: /Users/ericchiu/Documents/sungertain-design/G系統專案/logs/error.log
```

---

### Phase 4: 測試與驗證（1 小時）

#### Step 4.1: 單元測試
- [ ] 測試 .docx 提取功能
- [ ] 測試 HTML 轉換是否正確
- [ ] 測試 API 連線與認證
- [ ] 測試必需欄位驗證
- [ ] 測試錯誤處理機制

#### Step 4.2: 整合測試
- [ ] 生成文章 → 推送 → 驗證審核 URL 是否有效
- [ ] 檢查 article_id 是否正確返回
- [ ] 驗證文章在後台是否顯示為 "draft" 狀態

#### Step 4.3: 端對端測試
- [ ] 整個定時任務執行流程（手動觸發）
- [ ] 驗證日誌記錄完整性
- [ ] 檢查網站後台是否收到文章

---

## 📊 API 請求範例

完整的 JSON payload 範例：

```json
{
  "meta_title": "靈芝茶包如何選購？36入大包裝最划算｜三才靈芝農場",
  "meta_description": "想選靈芝茶包卻不知從何下手？三才靈芝農場教你如何挑選高品質靈芝茶包，36入大包裝CP值最高。",
  "article_body": "<h2>為什麼選擇靈芝茶包？</h2><p>靈芝作為傳統養生食材...</p><h2>挑選靈芝茶包的關鍵要點</h2><p>看產地與認證...</p>",
  "category": "選購指南",
  "tags": ["靈芝", "茶包", "選購指南"],
  "related_products": ["靈芝茶包 (36入) -大"],
  "publish_date": "2026-05-15T09:00:00+08:00",
  "status": "draft",
  "day_in_cycle": 2,
  "quality_score": 85,
  "references": [
    {
      "url": "https://www.fda.gov.tw/tc/sitecontent.aspx?sid=1776",
      "title": "台灣 TFDA - 食品安全衛生",
      "authority_score": 0.95
    },
    {
      "url": "https://pmc.ncbi.nlm.nih.gov/",
      "title": "PubMed Central",
      "authority_score": 0.90
    }
  ],
  "created_by": "cowork_system"
}
```

---

## ✅ 驗收標準

實現完成後應滿足：

- [ ] 每日 9:00 自動生成 .docx 文件
- [ ] 自動推送到 G 系統 API
- [ ] 文章在後台顯示為 "draft" 狀態
- [ ] 返回正確的 article_id 和 audit_url
- [ ] 所有推送日誌完整記錄
- [ ] 失敗時自動重試且有通知機制
- [ ] 網站後台能正確顯示文章內容

---

## 🔄 後續維護

### 定期檢查
- [ ] 每週檢查推送成功率
- [ ] 月末檢查 API 調用日誌
- [ ] 監控 API Key 的有效期（永久）

### 可能的擴展
- 支援排程發布（status="scheduled"）
- 自動計算 quality_score
- 集成文章審核工作流
- 添加文章更新（PATCH）功能

---

**預計完成時間**：3-5 小時（包含測試）  
**複雜度**：中等（主要是 .docx 解析和資料轉換）
