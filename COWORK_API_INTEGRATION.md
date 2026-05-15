# Cowork → G系統 API 對接指南

**API 端點**: `https://sungertain.deweichiu.com/api/articles/publish`

---

## 📋 快速開始

### 1️⃣ API Key 認證

```bash
# 在 HTTP Header 中帶入 API Key
Authorization: Bearer gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026
```

### 2️⃣ 環境變數設定

在 Cowork `.env` 文件中添加：

```bash
G_SYSTEM_API_URL=https://sungertain.deweichiu.com/api/articles/publish
G_SYSTEM_API_KEY=gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026
```

---

## 📤 API 請求格式

### 端點信息
- **URL**: `https://sungertain.deweichiu.com/api/articles/publish`
- **方法**: `POST`
- **Content-Type**: `application/json`

### 請求範例（cURL）

```bash
curl -X POST https://sungertain.deweichiu.com/api/articles/publish \
  -H "Authorization: Bearer gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "meta_title": "靈芝的五大健康益處",
    "meta_description": "了解靈芝如何改善免疫系統、降低壓力並促進睡眠品質。",
    "article_body": "<h2>靈芝簡介</h2><p>靈芝是一種珍貴的藥用菇，具有多種健康益處...</p>",
    "category": "入門認識",
    "tags": ["靈芝", "保健", "免疫"],
    "related_products": ["靈芝茶包 (36入) -大"],
    "publish_date": "2026-05-15T09:00:00+08:00",
    "status": "draft",
    "day_in_cycle": 1,
    "quality_score": 85,
    "references": [
      {
        "url": "https://example.com/ref1",
        "title": "參考資源1",
        "authority_score": 0.85
      }
    ],
    "created_by": "cowork_system"
  }'
```

### Python 請求範例

```python
import requests
import json
from datetime import datetime, timezone

def publish_article_to_g_system(article_data):
    """發送文章到 G 系統"""
    API_URL = "https://sungertain.deweichiu.com/api/articles/publish"
    API_KEY = "gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "meta_title": article_data.get("meta_title"),
        "meta_description": article_data.get("meta_description"),
        "article_body": article_data.get("article_body"),
        "category": article_data.get("category", "其他"),
        "tags": article_data.get("tags", []),
        "related_products": article_data.get("related_products", []),
        "publish_date": article_data.get("publish_date", datetime.now(timezone.utc).isoformat()),
        "status": article_data.get("status", "draft"),
        "day_in_cycle": article_data.get("day_in_cycle", 0),
        "quality_score": article_data.get("quality_score", 0),
        "references": article_data.get("references", []),
        "created_by": "cowork_system"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {"success": False, "error": str(e)}
```

---

## 📥 請求欄位詳細說明

| 欄位 | 型態 | 必需 | 說明 | 範例 |
|-----|------|------|------|------|
| `meta_title` | String | ✅ | SEO 標題（55-65字） | "靈芝的五大健康益處" |
| `meta_description` | String | ✅ | SEO 描述（160字以內） | "了解靈芝如何改善免疫系統..." |
| `article_body` | String | ✅ | 文章內容（HTML或純文本） | "<h2>標題</h2><p>內容...</p>" |
| `category` | String | ✅ | 文章分類 | "入門認識" |
| `tags` | Array | ❌ | 標籤陣列 | ["靈芝", "保健"] |
| `related_products` | Array | ❌ | 推薦產品 | ["靈芝茶包 (36入) -大"] |
| `publish_date` | ISO 8601 | ✅ | 發布時間（ISO格式+時區） | "2026-05-15T09:00:00+08:00" |
| `status` | String | ✅ | 發布狀態 | "draft" / "published" / "scheduled" |
| `day_in_cycle` | Integer | ❌ | 內容周期日數 | 1 |
| `quality_score` | Integer (0-100) | ❌ | AI 品質評分 | 85 |
| `references` | Array | ❌ | 參考來源清單 | [{"url": "...", "title": "...", "authority_score": 0.85}] |
| `created_by` | String | ❌ | 建立者（預設：cowork_system） | "cowork_system" |

### 分類允許值

```
- 選購指南
- 入門認識
- 產品評測
- 使用心得
- 健康知識
- 其他
```

### 狀態允許值

```
- draft      （草稿，等待編輯人員審核）
- published  （已發布，立即顯示在網站）
- scheduled  （排程發布，在 publish_date 時自動發布）
```

---

## 📨 API 回應格式

### ✅ 成功回應（HTTP 201 Created）

```json
{
  "success": true,
  "article_id": "A1B2C3D4",
  "title": "靈芝的五大健康益處",
  "url": "https://sungertain.deweichiu.com/articles/A1B2C3D4",
  "status": "draft",
  "message": "文章已保存為 draft，請在後台審核後發布",
  "created_at": "2026-05-15T09:00:00Z",
  "audit_url": "https://sungertain.deweichiu.com/articles?id=A1B2C3D4"
}
```

### ❌ 錯誤回應

#### 認證失敗（HTTP 401）
```json
{
  "success": false,
  "error_code": "INVALID_TOKEN",
  "error_message": "Invalid or expired API Key"
}
```

#### 缺少必需欄位（HTTP 400）
```json
{
  "success": false,
  "error_code": "MISSING_FIELDS",
  "error_message": "Missing required fields: meta_title, article_body"
}
```

#### 分類無效（HTTP 400）
```json
{
  "success": false,
  "error_code": "INVALID_CATEGORY",
  "error_message": "Category must be one of: 選購指南, 入門認識, 產品評測, 使用心得, 健康知識, 其他"
}
```

#### 伺服器錯誤（HTTP 500）
```json
{
  "success": false,
  "error_code": "SERVER_ERROR",
  "error_message": "Failed to save article to database"
}
```

---

## 🔄 錯誤代碼對照表

| 錯誤代碼 | HTTP 狀態 | 說明 | 建議處理 |
|---------|---------|------|--------|
| `INVALID_TOKEN` | 401 | API Key 無效或過期 | 檢查 API Key 是否正確 |
| `MISSING_FIELDS` | 400 | 缺少必需欄位 | 檢查請求中的必需欄位 |
| `INVALID_CATEGORY` | 400 | 分類值不符 | 使用允許的分類值 |
| `INVALID_STATUS` | 400 | 狀態值不符 | 使用 draft / published / scheduled |
| `SERVER_ERROR` | 500 | 伺服器錯誤 | 稍後重試或聯繫技術支援 |

---

## 📊 API 限制

| 限制項 | 值 |
|------|-----|
| 每分鐘調用數 | 10 次 |
| 每日發布篇數 | 無限制 |
| 單個請求大小 | 10 MB |
| Token 有效期 | 永久 |

如超過限制，將收到 HTTP 429 (Too Many Requests)。

---

## 🔄 整合步驟

### 在 Cowork 中整合

1. **導入請求庫**
   ```python
   import requests
   from datetime import datetime, timezone
   import os
   ```

2. **環境變數設定**（`.env` 文件）
   ```bash
   G_SYSTEM_API_URL=https://sungertain.deweichiu.com/api/articles/publish
   G_SYSTEM_API_KEY=gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026
   ```

3. **生成文章後調用 API**
   ```python
   def send_article_to_g_system(article_dict):
       api_url = os.getenv("G_SYSTEM_API_URL")
       api_key = os.getenv("G_SYSTEM_API_KEY")
       
       headers = {
           "Authorization": f"Bearer {api_key}",
           "Content-Type": "application/json"
       }
       
       response = requests.post(api_url, json=article_dict, headers=headers)
       
       if response.status_code == 201:
           result = response.json()
           print(f"✅ 文章已發送: {result['article_id']}")
           print(f"📍 審核 URL: {result['audit_url']}")
           return True
       else:
           error = response.json()
           print(f"❌ 發送失敗: {error['error_message']}")
           return False
   ```

4. **測試連線**
   ```bash
   # 使用範例數據測試
   curl -X POST https://sungertain.deweichiu.com/api/articles/publish \
     -H "Authorization: Bearer gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026" \
     -H "Content-Type: application/json" \
     -d '{"meta_title":"測試","meta_description":"測試描述","article_body":"測試內容","category":"其他","publish_date":"2026-05-15T09:00:00+08:00","status":"draft"}'
   ```

---

## 📞 技術支援

如有問題，請聯繫：
- **API 文檔**: https://sungertain.deweichiu.com/api/articles/publish
- **支援郵箱**: ericapril22th@gmail.com
- **響應時間**: 24 小時內

---

**最後更新**: 2026-05-15  
**版本**: 1.0  
**狀態**: ✅ 生產環境
