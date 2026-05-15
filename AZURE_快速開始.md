# Azure 快速開始指南

## 🔧 前置要件

### 1. 安裝 Azure CLI

**macOS:**
```bash
brew install azure-cli
```

**Windows:**
下載安裝程式: https://aka.ms/installazurecliwindows

**Linux:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. 驗證安裝
```bash
az --version
```

---

## 🚀 執行自動設定

### Step 1: 使腳本可執行

```bash
chmod +x /Users/ericchiu/Documents/sungertain-design/G系統專案/azure-setup-interactive.sh
```

### Step 2: 執行設定腳本

```bash
/Users/ericchiu/Documents/sungertain-design/G系統專案/azure-setup-interactive.sh
```

**腳本會自動執行以下操作:**
- ✅ 檢查 Azure CLI
- ✅ 詢問你的 Azure 帳戶和訂閱
- ✅ 建立資源群組
- ✅ 建立 Azure Key Vault
- ✅ 新增 API 密鑰
- ✅ 建立 App Service
- ✅ 啟用 Managed Identity
- ✅ 設定環境變數
- ✅ 準備代碼部署

---

## 📋 腳本會詢問的問題

| 問題 | 預設值 | 說明 |
|------|--------|------|
| 資源群組名稱 | sungertain-rg | 可使用現有或建立新的 |
| Azure 區域 | japaneast | 建議用日本東部(最近) |
| Key Vault 名稱 | sungertain-kv-{時間戳} | 須全球唯一 |
| App Service 計畫 | sungertain-plan | - |
| App Service 名稱 | sungertain-pub-{時間戳} | 須全球唯一 |

---

## 🔐 登入 Azure (必需)

如果尚未登入，腳本會自動執行:

```bash
az login
```

這會開啟瀏覽器窗口，讓你用 Azure 帳戶登入。

---

## 📤 部署代碼到 Azure

執行完腳本後，會得到 Git 部署 URL。執行:

```bash
cd /Users/ericchiu/Documents/sungertain-design/G系統專案

# 設定 Azure 作為 Git remote
git remote add azure <YOUR_GIT_URL_FROM_SCRIPT>

# 推送代碼
git push azure master
```

---

## ✅ 驗證部署

### 查看部署狀態
```bash
az webapp deployment slot list \
  --resource-group <RESOURCE_GROUP> \
  --name <APP_SERVICE_NAME>
```

### 查看即時日誌
```bash
az webapp log tail \
  --resource-group <RESOURCE_GROUP> \
  --name <APP_SERVICE_NAME>
```

### 測試 API 連接

進入 SSH:
```bash
az webapp ssh \
  --resource-group <RESOURCE_GROUP> \
  --name <APP_SERVICE_NAME>
```

然後執行:
```bash
cd /home/site/wwwroot
python article_publisher.py test
```

---

## ⏰ 設定定時任務

部署代碼後，根據需求選擇:

### 選項 A: Azure Function Timer Trigger (推薦)

```bash
# 建立 Function App
az functionapp create \
  --resource-group <RESOURCE_GROUP> \
  --consumption-plan-location <LOCATION> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name sungertain-scheduler
```

參考: `AZURE_部署指南.md` Step 6

### 選項 B: Cron Job (簡單)

使用 Azure Automation:
```bash
az automation account create \
  --resource-group <RESOURCE_GROUP> \
  --automation-account-name sungertain-automation
```

---

## 📊 查看資源

```bash
# 查看所有資源
az resource list --resource-group <RESOURCE_GROUP>

# 查看 Key Vault 密鑰
az keyvault secret list --vault-name <KEYVAULT_NAME>

# 查看 App Service 設定
az webapp config appsettings list \
  --resource-group <RESOURCE_GROUP> \
  --name <APP_SERVICE_NAME>
```

---

## 🗑️ 清理資源 (如需刪除)

```bash
# 刪除整個資源群組（包含所有資源）
az group delete --resource-group <RESOURCE_GROUP>

# 刪除特定資源
az webapp delete --resource-group <RESOURCE_GROUP> --name <APP_SERVICE_NAME>
```

---

## 🆘 常見問題

### Q: 執行 `az login` 後沒有反應
**A:** 
```bash
az login --use-device-code
```
然後到 https://microsoft.com/devicelogin 輸入代碼

### Q: Key Vault 名稱已存在
**A:** Key Vault 名稱必須全球唯一。腳本會自動附加時間戳。如手動設定，請使用不同的名稱。

### Q: App Service 啟動緩慢
**A:** 這是正常的。App Service 首次啟動需要時間。查看日誌:
```bash
az webapp log tail --resource-group <RG> --name <NAME>
```

### Q: 部署後代碼未更新
**A:** 執行:
```bash
az webapp restart --resource-group <RG> --name <NAME>
```

---

## 📚 詳細文檔

- `AZURE_部署指南.md` - 完整部署指南
- `requirements.txt` - Python 依賴
- `article_publisher.py` - 主要應用邏輯

---

**需要幫助?** 查看 Azure 官方文檔: https://docs.microsoft.com/azure/
