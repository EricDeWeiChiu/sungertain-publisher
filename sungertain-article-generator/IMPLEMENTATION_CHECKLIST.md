# 完整實施檢查清單

## 📋 G系統集成 + Cowork自動化部署

此檢查清單指導您逐步部署「三才靈芝農場博客文章生成系統」完整解決方案。

---

## 🎯 第1階段：準備工作 (第1週)

### Week 1, Day 1-2：驗證環境

- [ ] **Python環境檢查**
  - [ ] Python 3.8+ 已安裝
  - [ ] 可執行 `python --version` 驗證
  - [ ] pip 已安裝並可用

- [ ] **Cowork應用檢查**
  - [ ] Cowork已安裝最新版本
  - [ ] 可訪問定時任務設置
  - [ ] 已同步帳戶 (可見聯絡人和日程)

- [ ] **Azure帳戶檢查**
  - [ ] Azure帳戶已建立並登入
  - [ ] 訂閱已啟用
  - [ ] 有效的支付方式已設置

### Week 1, Day 3-4：下載並檢查Skill文件

- [ ] **Skill文件已獲取**
  - [ ] ✅ SKILL.md (完整規格)
  - [ ] ✅ README.md (使用指南)
  - [ ] ✅ INSTALLATION_GUIDE.md (安裝說明)
  - [ ] ✅ evals.json (測試用例)
  - [ ] ✅ QUICK_REFERENCE.md (快速參考)

- [ ] **適配器文件已生成**
  - [ ] ✅ scripts/article_generator.py
  - [ ] ✅ scripts/g_system_adapter.py (新建)
  - [ ] ✅ references/VERIFIED_SOURCES.md
  - [ ] ✅ references/AZURE_SETUP.md (新建)
  - [ ] ✅ references/COWORK_SCHEDULED_TASK_SETUP.md (新建)

- [ ] **檔案結構驗證**
  ```
  sungertain-article-generator/
  ├── SKILL.md ✅
  ├── README.md ✅
  ├── INSTALLATION_GUIDE.md ✅
  ├── IMPLEMENTATION_CHECKLIST.md ✅
  ├── evals.json ✅
  ├── scripts/
  │   ├── article_generator.py ✅
  │   └── g_system_adapter.py ✅
  ├── references/
  │   ├── VERIFIED_SOURCES.md ✅
  │   ├── AZURE_SETUP.md ✅
  │   └── COWORK_SCHEDULED_TASK_SETUP.md ✅
  └── examples/
      └── (5個示例文檔) ✅
  ```

### Week 1, Day 5：審視架構

- [ ] **閱讀關鍵文檔**
  - [ ] SKILL.md 全文 (理解規格)
  - [ ] COWORK_SKILL_FORMAT_ADAPTATION.md (理解JSON輸出)
  - [ ] COWORK_SCHEME_B_FEASIBILITY.md (理解整體架構)

- [ ] **理解關鍵概念**
  - [ ] 7天輪轉計劃如何運作
  - [ ] Meta信息格式要求 (40-60, 120-160)
  - [ ] 品質分數計算方法
  - [ ] JSON輸出結構
  - [ ] Azure SQL表格設計

---

## 🌥️ 第2階段：Azure SQL設置 (第2週)

### Week 2, Day 1-2：在Azure Portal建立資料庫

- [ ] **建立SQL Server**
  - [ ] 前往 https://portal.azure.com
  - [ ] 建立新SQL Server
  - [ ] 伺服器名稱：`gSystem-server` (或自訂)
  - [ ] 位置：Southeast Asia (台灣)
  - [ ] 記錄伺服器名稱和管理員用戶名

- [ ] **建立SQL資料庫**
  - [ ] 資料庫名稱：`gSystem`
  - [ ] 計算+儲存：Standard S0 (或按需求)
  - [ ] 排序規則：Chinese_Taiwan_Stroke_90_CI_AS
  - [ ] 備份冗餘：本地備份儲存

- [ ] **配置防火牆**
  - [ ] 允許Azure服務存取
  - [ ] 新增您的IP地址規則
  - [ ] 獲取連接字符串

### Week 2, Day 3：建立資料庫表格

- [ ] **執行SQL指令碼**
  - [ ] 開啟Azure Query Editor
  - [ ] 複製 `AZURE_SETUP.md` 中的SQL指令碼
  - [ ] 執行建立Articles表格
  - [ ] 執行建立ExecutionLogs表格
  - [ ] 執行建立References表格 (可選)
  - [ ] 驗證表格已建立

- [ ] **檢查索引**
  - [ ] IDX_PublishDate 已建立
  - [ ] IDX_Category 已建立
  - [ ] IDX_QualityScore 已建立
  - [ ] 複合索引已建立

- [ ] **測試連接**
  ```
  使用Python測試：
  [ ] 可連接到Azure SQL
  [ ] 可執行SELECT查詢
  [ ] 連接字符串有效
  ```

### Week 2, Day 4-5：設置Azure Blob Storage (可選)

- [ ] **建立Blob Container**
  - [ ] 建立Storage Account
  - [ ] 建立Container：`articles`
  - [ ] 設置存取級別：Private
  - [ ] 記錄連接字符串

- [ ] **設置備份策略**
  - [ ] 定期備份Word檔案
  - [ ] 定期備份JSON輸出
  - [ ] 保留策略：30天

---

## 💻 第3階段：Cowork Skill安裝 (第3週)

### Week 3, Day 1：安裝Skill

- [ ] **安裝方法選擇**
  - [ ] 方法A：直接.skill檔案 (推薦)
  - [ ] 方法B：手動複製資料夾

- [ ] **執行安裝**
  - [ ] 開啟Cowork應用
  - [ ] 進入設置 → 技能
  - [ ] 點擊「安裝新技能」
  - [ ] 選擇 `sungertain-article-generator.skill` 檔案
  - [ ] 完成安裝

- [ ] **驗證安裝**
  - [ ] 在Cowork搜索「sungertain」
  - [ ] 能看到「三才靈芝農場 博客文章自動生成系統」
  - [ ] 可點擊「試試」測試

### Week 3, Day 2：配置環境變數

- [ ] **設置Cowork環境變數**
  - [ ] 開啟Cowork設置
  - [ ] 進入「環境變數」或「設置」
  - [ ] 新增變數：`AZURE_SQL_CONNECTION_STRING`
    ```
    值：Server=tcp:YOUR_SERVER.database.windows.net,1433;Initial Catalog=gSystem;User ID=YOUR_USER;Password=YOUR_PASSWORD;Encrypt=True;Connection Timeout=30;
    ```
  - [ ] 新增變數：`AZURE_SQL_DATABASE=gSystem`
  - [ ] 新增變數：`AZURE_SQL_TABLE=Articles`
  - [ ] 新增變數：`COWORK_OUTPUT_FOLDER=/Users/ericchiu/Documents/sungertain-design/G系統專案/output`

- [ ] **驗證環境變數**
  - [ ] 可在Python指令碼中存取
  - [ ] 値被正確讀取

### Week 3, Day 3-4：手動測試 (Day 1)

- [ ] **第一篇文章測試**
  - [ ] 日期：2026-05-14
  - [ ] 分類：入門認識
  - [ ] 產品：靈芝黑木耳露 (瓶)
  - [ ] SKU：FD-WOODEAR-001

- [ ] **檢查輸出**
  ```
  [ ] Word檔案已生成
  [ ] 文件名：20260514_入門認識_靈芝黑木耳露.docx
  [ ] Meta表格包含所有必要信息
  [ ] 文章字數在600-1000字範圍
  [ ] 參考資源5-7條
  [ ] 所有URL有效
  ```

- [ ] **驗證品質**
  - [ ] 執行評估：`python evals.json`
  - [ ] 品質分數：看期望≥75
  - [ ] 檢查評分詳細
  - [ ] 如<75，檢查錯誤並修正

- [ ] **生成JSON**
  - [ ] 執行g_system_adapter生成JSON
  - [ ] 檢查JSON結構完整
  - [ ] 驗證所有欄位正確
  - [ ] 測試JSON可解析

### Week 3, Day 5：存儲到Azure

- [ ] **手動測試存儲**
  - [ ] 執行SQL INSERT語句
  - [ ] 驗證記錄出現在Articles表格
  - [ ] 檢查ExecutionLogs表格

- [ ] **驗證查詢**
  ```sql
  SELECT * FROM Articles WHERE PublishDate = '2026-05-14'
  ```
  - [ ] 記錄可查詢
  - [ ] 所有欄位正確

---

## ⏰ 第4階段：設置定時任務 (第4週)

### Week 4, Day 1：建立定時任務

- [ ] **在Cowork中建立定時任務**
  - [ ] 開啟Cowork
  - [ ] 進入「設置」→「定時任務」
  - [ ] 點擊「新建任務」

- [ ] **填入基本信息**
  - [ ] 任務名稱：`三才靈芝農場 - 每日文章生成`
  - [ ] 描述：每日早上9點自動生成靈芝農場博客文章
  - [ ] 選擇「定期執行」

- [ ] **設置執行時間表**
  - [ ] Cron表達式：`0 9 * * *`
  - [ ] 時區：`Asia/Taipei (UTC+8)`
  - [ ] 驗證下次執行時間顯示為今天09:00

- [ ] **複製Prompt**
  - [ ] 從 `COWORK_SCHEDULED_TASK_SETUP.md` 複製完整Prompt
  - [ ] 貼入定時任務的「提示詞」欄位
  - [ ] 驗證所有內容正確複製

### Week 4, Day 2-3：測試定時任務

- [ ] **手動執行一次**
  - [ ] 不等待定時，立即執行定時任務
  - [ ] 監控執行進度
  - [ ] 檢查輸出結果

- [ ] **驗證Day 2的自動執行**
  - [ ] 等待次日09:00
  - [ ] 檢查是否自動執行
  - [ ] 驗證Day 2的產品和分類正確
  - [ ] 檢查生成的文檔

- [ ] **監控Day 3-7**
  - [ ] 監控每日執行
  - [ ] 檢查品質分數
  - [ ] 驗證7天輪轉是否正確循環
  - [ ] 記錄執行時間和任何錯誤

### Week 4, Day 4-5：驗證完整工作流

- [ ] **驗證7天完整循環**
  - [ ] Day 1 ✅ 檢查執行
  - [ ] Day 2 ✅ 檢查執行
  - [ ] Day 3 ✅ 檢查執行
  - [ ] Day 4 ✅ 檢查執行
  - [ ] Day 5 ✅ 檢查執行
  - [ ] Day 6 ✅ 檢查執行
  - [ ] Day 7 ✅ 檢查執行

- [ ] **檢查Azure SQL**
  - [ ] 所有7篇文章都在Articles表格
  - [ ] ExecutionLogs記錄了執行歷史
  - [ ] 品質分數都≥75

- [ ] **檢查自動化流程**
  - [ ] Day 8執行是否循環回Day 1
  - [ ] 是否自動計算DayInCycle
  - [ ] 是否自動查詢正確的產品

---

## 🎨 第5階段：G系統集成 (第5週)

### Week 5, Day 1-2：收集G系統信息

- [ ] **獲取G系統規格**
  - [ ] G系統的JSON schema
  - [ ] Articles端點URL
  - [ ] 認證方法 (API Key / OAuth / 其他)
  - [ ] 請求示例

- [ ] **測試G系統連接**
  - [ ] 可連接到G系統 API
  - [ ] 可發送測試請求
  - [ ] 可接收回應
  - [ ] 認證工作正確

### Week 5, Day 3-4：修改Skill以支持G系統輸出

- [ ] **修改SKILL.md**
  - [ ] 添加JSON輸出格式詳細說明
  - [ ] 添加G系統集成說明
  - [ ] 添加API端點配置

- [ ] **修改Prompt**
  - [ ] 更新Cowork定時任務的Prompt
  - [ ] 添加G系統JSON格式要求
  - [ ] 添加自動上傳到G系統的指示

- [ ] **測試JSON輸出**
  - [ ] 生成的JSON符合G系統規格
  - [ ] 可成功發送到G系統
  - [ ] G系統能接收並存儲

### Week 5, Day 5：完整集成測試

- [ ] **端到端測試**
  - [ ] Cowork生成文章
  - [ ] 保存Word檔案
  - [ ] 生成JSON
  - [ ] 存儲到Azure SQL
  - [ ] 發送到G系統
  - [ ] 驗證G系統接收到數據

- [ ] **驗證數據一致性**
  - [ ] Azure SQL中的數據
  - [ ] G系統中的數據
  - [ ] Word檔案內容
  - [ ] 所有三個位置的數據一致

---

## 📊 第6階段：監控和優化 (第6週+)

### Week 6, Day 1-2：設置監控

- [ ] **Azure SQL監控**
  - [ ] 啟用查詢性能分析
  - [ ] 設置Azure警報
  - [ ] 監控執行時間

- [ ] **Cowork日誌**
  - [ ] 查看定時任務執行日誌
  - [ ] 檢查錯誤和警告
  - [ ] 驗證成功率 (應≥95%)

- [ ] **G系統驗證**
  - [ ] 檢查文章是否成功發布
  - [ ] 驗證元數據正確
  - [ ] 監控最終發布狀態

### Week 6, Day 3-4：性能優化

- [ ] **優化SQL查詢**
  - [ ] 檢查執行計劃
  - [ ] 確認索引被使用
  - [ ] 優化緩慢查詢

- [ ] **優化Cowork Prompt**
  - [ ] 根據實際執行調整Prompt
  - [ ] 優化品質分數計算
  - [ ] 加快生成時間

### Week 6, Day 5：文檔和知識轉移

- [ ] **更新文檔**
  - [ ] 記錄實際部署經驗
  - [ ] 更新故障排除指南
  - [ ] 添加最佳實踐

- [ ] **建立操作手冊**
  - [ ] 日常監控清單
  - [ ] 常見問題解決方案
  - [ ] 緊急應對程序

---

## 🎯 驗收標準

### 功能驗收

- [ ] ✅ 每日09:00自動生成文章
- [ ] ✅ 7天輪轉計劃正常運作
- [ ] ✅ 所有文章品質分數≥75
- [ ] ✅ Meta信息長度符合要求
- [ ] ✅ 參考資源驗證成功
- [ ] ✅ JSON輸出正確格式
- [ ] ✅ Azure SQL存儲成功
- [ ] ✅ G系統可接收數據

### 性能驗收

- [ ] ✅ 文章生成時間 < 3分鐘
- [ ] ✅ Azure SQL查詢 < 500ms
- [ ] ✅ 月度成功率 ≥ 95%
- [ ] ✅ 月度平均品質分數 ≥ 82

### 可靠性驗收

- [ ] ✅ 定時任務未中斷執行
- [ ] ✅ 無數據遺失
- [ ] ✅ 所有執行都被記錄
- [ ] ✅ 可追蹤完整執行歷史

---

## 🆘 遇到問題？

### 快速排查

| 問題 | 檢查清單 |
|------|--------|
| **定時任務未執行** | ✓ Cron表達式 ✓ 時區 ✓ Cowork運行狀態 |
| **品質分數 < 75** | ✓ 字數 ✓ 參考資源 ✓ 虛假聲稱 |
| **Azure連接失敗** | ✓ 連接字符串 ✓ 防火牆 ✓ 認證 |
| **參考資源無效** | ✓ URL格式 ✓ 訪問權限 ✓ EEAT解釋 |
| **JSON格式錯誤** | ✓ 字段名稱 ✓ 數據類型 ✓ 編碼 |

### 支援資源

- 📖 SKILL.md - 完整規格
- 📘 README.md - 使用指南
- 📔 INSTALLATION_GUIDE.md - 安裝說明
- ⚙️ AZURE_SETUP.md - Azure配置
- ⏰ COWORK_SCHEDULED_TASK_SETUP.md - 定時任務設置
- 📊 QUICK_REFERENCE.md - 快速參考

---

## 📝 簽核

實施完成後，請填寫：

```
日期：________________
實施者：______________
驗收者：______________
註釋：_________________
```

---

**版本：1.0**  
**最後更新：2026-05-14**  
**預期完成時間：4-6週**
