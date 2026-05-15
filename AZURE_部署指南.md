# Azure 部署指南

**實現日期**：2026年5月15日  
**狀態**：✅ 已實現 Azure 支援  
**部署方式**：Azure App Service / Azure Container Instances

---

## 📋 Azure 架構概述

```
本地開發
  ↓
GitHub/Azure DevOps (版本控制)
  ↓
Azure App Service (或 Container Instances)
  ↓
Azure Key Vault (敏感信息)
  ↓
G系統 API (https://sungertain.deweichiu.com/api/articles/publish)
```

---

## 🔑 Step 1：在 Azure Key Vault 中創建密鑰

### 1.1 建立 Key Vault（若尚未建立）

```bash
az keyvault create --resource-group <your-resource-group> \
  --name <your-keyvault-name>
```

### 1.2 新增 API 密鑰

```bash
# 新增 API URL
az keyvault secret set --vault-name <your-keyvault-name> \
  --name "G-SYSTEM-API-URL" \
  --value "https://sungertain.deweichiu.com/api/articles/publish"

# 新增 API Key
az keyvault secret set --vault-name <your-keyvault-name> \
  --name "G-SYSTEM-API-KEY" \
  --value "gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026"
```

### 1.3 驗證密鑰

```bash
az keyvault secret list --vault-name <your-keyvault-name>
```

---

## 🔐 Step 2：配置 Azure App Service 環境變數

### 2.1 設定環境變數

在 Azure Portal 或 CLI 中設定應用程式設定：

```bash
az webapp config appsettings set --resource-group <your-resource-group> \
  --name <your-app-service-name> \
  --settings AZURE_KEYVAULT_URL="https://<your-keyvault-name>.vault.azure.net/"
```

### 2.2 啟用 Managed Identity（推薦）

```bash
# 啟用系統管理身份
az webapp identity assign --resource-group <your-resource-group> \
  --name <your-app-service-name> --identities [system]

# 取得身份 ID
IDENTITY_ID=$(az webapp identity show --resource-group <your-resource-group> \
  --name <your-app-service-name> --query principalId -o tsv)

# 授予 Key Vault 訪問權限
az keyvault set-policy --name <your-keyvault-name> \
  --object-id $IDENTITY_ID \
  --secret-permissions get list
```

---

## 📦 Step 3：準備 Azure 部署

### 3.1 更新 requirements.txt

```bash
pip install -r requirements.txt --break-system-packages
```

檔案已包含：
- `requests` - HTTP 請求
- `python-docx` - Word 文檔解析
- `azure-identity` - Azure 認證
- `azure-keyvault-secrets` - Key Vault 存取
- `python-dotenv` - 本地開發用

### 3.2 建立 .azure-config.json（可選）

```json
{
  "keyvault_name": "your-keyvault-name",
  "resource_group": "your-resource-group",
  "app_service_name": "your-app-service-name"
}
```

---

## 🚀 Step 4：部署選項

### 選項 A：Azure App Service（推薦）

#### 4A.1 透過 Azure Portal

1. 建立 App Service (Python 3.11)
2. 連結 GitHub/Azure DevOps repository
3. 配置自動部署
4. 設定環境變數和 Managed Identity

#### 4A.2 透過 Azure CLI

```bash
# 建立 App Service Plan
az appservice plan create --name <plan-name> \
  --resource-group <resource-group> --sku B1 --is-linux

# 建立 Web App
az webapp create --resource-group <resource-group> \
  --plan <plan-name> --name <app-name> \
  --runtime "PYTHON|3.11"

# 部署代碼
az webapp up --resource-group <resource-group> \
  --name <app-name>
```

### 選項 B：Azure Container Instances

#### 4B.1 建立 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

ENV AZURE_KEYVAULT_URL=${AZURE_KEYVAULT_URL}
ENV PYTHONUNBUFFERED=1

CMD ["python", "daily_article_workflow.py"]
```

#### 4B.2 建立容器映像

```bash
# 登入 Azure Container Registry
az acr login --name <your-acr-name>

# 建立映像
az acr build --registry <your-acr-name> \
  --image sungertain-publisher:latest .

# 部署容器
az container create --resource-group <resource-group> \
  --name sungertain-publisher \
  --image <your-acr-name>.azurecr.io/sungertain-publisher:latest \
  --environment-variables AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net/
```

---

## ⏰ Step 5：配置定時任務

### 5.1 使用 Azure Timer Trigger Function

建立 `function_app.py`：

```python
import azure.functions as func
import subprocess
import os

app = func.FunctionApp()

@app.timer_trigger(arg_name="myTimer", schedule="0 1 * * *")  # 每天 1:00 UTC (9:00 台灣時間)
def article_publisher_trigger(myTimer: func.TimerRequest) -> None:
    """每日文章發布定時任務"""
    
    os.chdir('/Users/ericchiu/Documents/sungertain-design/G系統專案')
    
    try:
        result = subprocess.run(
            ['python', 'daily_article_workflow.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logging.info("✅ 文章發布成功")
        else:
            logging.error(f"❌ 文章發布失敗: {result.stderr}")
    
    except Exception as e:
        logging.error(f"❌ 定時任務執行失敗: {e}")
```

### 5.2 部署 Azure Function

```bash
# 安裝 Azure Functions Core Tools
# macOS: brew tap azure/azure && brew install azure-functions-core-tools@4

# 初始化 Function App
func init MyFunctionApp --python

# 建立定時觸發
func new --name ArticlePublisherTrigger --template "Timer trigger"

# 本地測試
func start

# 部署到 Azure
func azure functionapp publish <your-function-app-name>
```

---

## 🔍 Step 6：監控和日誌

### 6.1 Azure Application Insights

```bash
# 啟用 Application Insights
az webapp config appsettings set --resource-group <resource-group> \
  --name <app-name> \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=<key>
```

### 6.2 查看日誌

```bash
# 即時日誌
az webapp log tail --resource-group <resource-group> --name <app-name>

# 下載日誌
az webapp log download --resource-group <resource-group> \
  --name <app-name> --log-file logs.zip
```

### 6.3 應用程式洞察查詢

```kusto
traces
| where timestamp > ago(24h)
| where message contains "✅" or message contains "❌"
| project timestamp, message
| order by timestamp desc
```

---

## 🔒 Step 7：安全最佳實踐

### 7.1 API Key 管理

✅ **正確做法**
- 使用 Azure Key Vault 存儲所有密鑰
- 使用 Managed Identity 進行認證（無需密碼）
- 定期輪換 API Key
- 使用最小權限原則

❌ **避免**
- 在代碼中硬編碼 API Key
- 在環境變數中直接存儲敏感信息（使用 Key Vault 代替）
- 在 GitHub 提交 `.env` 檔案

### 7.2 網絡安全

```bash
# 限制 Key Vault 訪問
az keyvault network-rule add --name <vault-name> \
  --resource-group <resource-group> \
  --vnet-name <vnet-name> \
  --subnet <subnet-name>

# 啟用防火牆
az keyvault update --name <vault-name> \
  --resource-group <resource-group> \
  --default-action Deny \
  --bypass AzureServices
```

---

## 📊 Step 8：效能優化

### 8.1 應用程式設定

```bash
# 啟用 Always On（避免冷啟動）
az webapp config set --resource-group <resource-group> \
  --name <app-name> --always-on true

# 調整執行個體大小
az appservice plan update --name <plan-name> \
  --resource-group <resource-group> --sku S1
```

### 8.2 自動縮放

```bash
# 建立自動縮放規則
az monitor autoscale create \
  --resource-group <resource-group> \
  --resource-name <app-service-name> \
  --resource-type "Microsoft.Web/serverfarms" \
  --min-count 1 --max-count 5 --count 1
```

---

## 🧪 Step 9：測試部署

### 9.1 測試 API 連接

```bash
# 在 Azure 中執行測試
az webapp up --resource-group <resource-group> \
  --name <app-name> --runtime "PYTHON|3.11"

# 手動執行
python article_publisher.py test
```

### 9.2 測試 Key Vault 連接

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = "https://<vault-name>.vault.azure.net/"
client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())

try:
    secret = client.get_secret("G-SYSTEM-API-KEY")
    print("✅ Key Vault 連接正常")
except Exception as e:
    print(f"❌ Key Vault 連接失敗: {e}")
```

---

## 🆘 故障排除

### 場景 1：無法訪問 Key Vault

**檢查清單**
1. 確認 Managed Identity 已啟用
2. 驗證 Key Vault 訪問原則是否正確
3. 檢查防火牆設定
4. 查看 Application Insights 日誌

### 場景 2：API 推送超時

**解決方案**
1. 增加 App Service 實例大小
2. 增加 API 調用超時時間
3. 檢查網絡連接性
4. 驗證 G系統 API 是否可用

### 場景 3：定時任務未執行

**檢查清單**
1. 確認 Azure Function 已啟用
2. 驗證 Cron 表達式（`0 1 * * *` = 每天 1:00 UTC）
3. 檢查時區設定
4. 查看 Function App 日誌

---

## 📋 部署檢查清單

- [ ] 建立 Azure Key Vault
- [ ] 新增 API 密鑰到 Key Vault
- [ ] 建立/設定 App Service
- [ ] 啟用 Managed Identity
- [ ] 設定 Key Vault 訪問原則
- [ ] 設定環境變數 `AZURE_KEYVAULT_URL`
- [ ] 安裝 Azure SDK (`pip install -r requirements.txt`)
- [ ] 部署應用程式
- [ ] 測試 API 連接
- [ ] 配置定時任務（Azure Function Timer Trigger）
- [ ] 啟用 Application Insights 監控
- [ ] 設定告警規則

---

## 📚 有用的命令

```bash
# 檢查應用狀態
az webapp show --resource-group <rg> --name <app-name>

# 重啟應用
az webapp restart --resource-group <rg> --name <app-name>

# 查看環境變數
az webapp config appsettings list --resource-group <rg> --name <app-name>

# 更新設定
az webapp config appsettings set --resource-group <rg> \
  --name <app-name> --settings KEY=VALUE

# 查看成本估算
az cost management query --timeframe TheLastMonth
```

---

**最後更新**：2026-05-15  
**版本**：1.0  
**狀態**：✅ Azure 支援已實現
