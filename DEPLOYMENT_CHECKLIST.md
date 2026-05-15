# GitHub Actions 自動發布系統 - 部署檢查清單

## ✅ 已完成的設置

### 1. 工作流程檔案 (.github/workflows/main.yml)
- **位置**: `.github/workflows/main.yml`
- **功能**: 每天 UTC 1:00 (台灣時間 9:00) 自動執行文章發布
- **狀態**: ✅ 已建立 (YAML 語法已修正)

```yaml
name: Daily Article Publisher
on:
  schedule:
    - cron: '0 1 * * *'  # 每天 UTC 1:00 (台灣時間 9:00)
jobs:
  publish:
    runs-on: ubuntu-latest
    steps: [Python 設置, 依賴安裝, 執行發布腳本]
```

### 2. Python 依賴檔案 (requirements.txt)
- **位置**: `requirements.txt`
- **內容**:
  - requests==2.31.0 (API 調用)
  - python-dotenv==1.0.0 (環境變數)
- **狀態**: ✅ 已建立

### 3. 核心發布腳本
- **article_publisher.py**: ✅ 已存在 (API 調用、DOCX 解析)
- **daily_article_workflow.py**: ✅ 已存在 (工作流程編排)
- **狀態**: 兩個腳本都已完成配置

### 4. 測試文章
- **檔案**: `20260515_選購指南_靈芝茶包 (36入) -大.docx`
- **狀態**: ✅ 已建立，包含完整的 Meta 表格和內容

---

## 📋 需要您在本地執行的步驟

### 步驟 1: 推送改動到 GitHub

在您的本地電腦上（您有 GitHub 認證）：

```bash
cd ~/Documents/sungertain-design/G系統專案

# 查看待推送的改動
git status

# 添加工作流程和依賴檔案
git add .github/workflows/main.yml requirements.txt

# 提交
git commit -m "feat: setup GitHub Actions daily article publisher

- Add .github/workflows/main.yml for daily scheduling (9 AM Taiwan time)
- Update requirements.txt with minimal dependencies
- Ready for G系統 API integration"

# 推送到 GitHub
git push origin main
```

### 步驟 2: 在 GitHub 設置 Secrets

進入 GitHub 倉庫頁面：

1. 點擊 **Settings** → **Secrets and variables** → **Actions**
2. 新增密鑰：
   - **Name**: `G_SYSTEM_API_URL`
   - **Value**: `https://sungertain.deweichiu.com/api/articles/publish`
   
   點 **Add secret**

3. 再新增第二個密鑰：
   - **Name**: `G_SYSTEM_API_KEY`
   - **Value**: `您的 API 金鑰` (您已在本地環境設定過)
   
   點 **Add secret**

### 步驟 3: 測試工作流程

有兩種方式測試：

**選項 A - 等待自動執行** (推薦用於正式測試)
- 工作流程將在每天台灣時間 9:00 自動執行
- 檢查 **Actions** 分頁查看執行結果

**選項 B - 立即手動觸發測試**
1. 進入 GitHub 倉庫
2. 點擊 **Actions** 分頁
3. 左側選擇 "Daily Article Publisher"
4. 點擊 **Run workflow** → **Run workflow**
5. 工作流程會立即執行

---

## 🔍 驗證工作流程是否成功

執行完後，檢查：

1. **GitHub Actions 結果**
   - 進入 **Actions** → **Daily Article Publisher**
   - 檢查最新的執行日誌
   - 應該看到綠色的 ✓ 標記

2. **G系統確認**
   - 登入 G系統 後台
   - 檢查是否有新文章被發布
   - 確認文章狀態為 "draft" (待審核)

3. **日誌檔案** (本地執行時)
   - 檢查 `logs/workflow.log` 內容
   - 應該顯示文章解析和推送成功的訊息

---

## 📝 工作流程架構說明

```
每天 9:00 AM (台灣時間)
    ↓
GitHub Actions 觸發
    ↓
Checkout 代碼
    ↓
安裝 Python 3.11
    ↓
安裝依賴 (requests, python-dotenv)
    ↓
執行 daily_article_workflow.py
    ├─ 讀取環境變數 (G_SYSTEM_API_URL, G_SYSTEM_API_KEY)
    ├─ 計算循環中的日期 (Day 1-7)
    ├─ 尋找對應的 .docx 文件
    ├─ 解析 DOCX 並提取內容
    └─ 推送到 G系統 API
        ↓
    成功 → 記錄日誌
    失敗 → 發送錯誤訊息
```

---

## 🐛 常見問題排解

### 問題 1: "找不到文章文件" 錯誤
- **原因**: 檔名格式不符
- **解決**: 確保檔名格式為 `YYYYMMDD_分類_產品名.docx`
  - 例: `20260515_選購指南_靈芝茶包 (36入) -大.docx`

### 問題 2: "認證失敗 (401)" 錯誤
- **原因**: API 金鑰無效或未正確設置
- **解決**: 
  1. 確認 GitHub Secret 中的 `G_SYSTEM_API_KEY` 正確
  2. 確認金鑰在 G系統 後台仍然有效

### 問題 3: 工作流程沒有自動執行
- **原因**: GitHub Actions 可能需要啟用
- **解決**:
  1. 進入倉庫 **Settings** → **Actions** → **General**
  2. 確認 "Allow all actions and reusable workflows" 是選中狀態

---

## 📊 後續操作

### 每日文章發布流程
1. **上午**: 您在 Cowork 或本地生成當天的文章 (.docx)
2. **存放**: 將文件保存到 `G系統專案` 目錄
3. **9:00 AM**: GitHub Actions 自動檢測並發布文章
4. **確認**: 檢查 G系統 後台確認發布成功

### 文章循環計畫
```
Day 1 (5/14): 入門認識 - 纖芝翠-靈芝黑木耳露(瓶)
Day 2 (5/15): 選購指南 - 靈芝茶包 (36入) -大
Day 3 (5/16): 選購指南 - 靈芝膠囊 100% (60粒)
Day 4 (5/17): 飲食指南 - 靈芝健康咖啡 (5 入)
Day 5 (5/18): 保存方式 - 靈芝原朵 (小包)
Day 6 (5/19): 常見問題 - 五倍靈芝粉
Day 7 (5/20): 深入認識 - 靈芝藥膳湯
```

---

## 📞 需要幫助？

如果遇到任何問題，檢查：
1. GitHub 倉庫中 **Actions** 分頁的執行日誌
2. G系統 後台的文章發布狀態
3. 本地 `logs/` 目錄中的詳細日誌檔案

**準備就緒！您可以開始推送改動了。** 🚀
