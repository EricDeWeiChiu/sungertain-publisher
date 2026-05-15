#!/bin/bash

#################################
# Azure 自動設定腳本 (互動式)
# 為三才靈芝農場文章發布系統設定 Azure 環境
#################################

set -e

echo "========================================"
echo "🚀 Azure 環境自動設定程式"
echo "========================================"
echo ""

# Step 0: 檢查 Azure CLI
echo "📋 檢查前置要件..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI 未安裝"
    echo "請先安裝: https://learn.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo "✅ Azure CLI 已安裝"
echo ""

# Step 1: 檢查登入狀態
echo "🔐 檢查 Azure 登入狀態..."
if ! az account show &> /dev/null; then
    echo "❌ 尚未登入 Azure"
    echo "執行: az login"
    az login
fi

ACCOUNT=$(az account show --query name -o tsv)
echo "✅ 已登入帳戶: $ACCOUNT"
echo ""

# Step 2: 獲取/確認訂閱 ID
echo "📌 訂閱設定..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "目前訂閱 ID: $SUBSCRIPTION_ID"
echo ""

# Step 3: 資源群組選擇
echo "📁 資源群組選擇..."
echo "現有資源群組:"
az group list --query "[].name" -o tsv | nl

read -p "輸入現有資源群組名稱 (或按 Enter 建立新的): " RESOURCE_GROUP
if [ -z "$RESOURCE_GROUP" ]; then
    RESOURCE_GROUP="sungertain-rg"
    echo "將建立新資源群組: $RESOURCE_GROUP"

    read -p "選擇區域 (eastasia/southeastasia/japaneast) [japaneast]: " LOCATION
    LOCATION=${LOCATION:-japaneast}

    az group create --name $RESOURCE_GROUP --location $LOCATION
    echo "✅ 資源群組已建立"
else
    echo "✅ 使用現有資源群組: $RESOURCE_GROUP"
fi
echo ""

# Step 4: 取得資源群組位置
LOCATION=$(az group show --name $RESOURCE_GROUP --query location -o tsv)
echo "位置: $LOCATION"
echo ""

# Step 5: 其他資源設定
echo "⚙️  設定資源名稱..."
read -p "Key Vault 名稱 (須全球唯一, 預設: sungertain-kv-$(date +%s)): " KEYVAULT_NAME
KEYVAULT_NAME=${KEYVAULT_NAME:-sungertain-kv-$(date +%s)}

read -p "App Service Plan 名稱 [sungertain-plan]: " APP_SERVICE_PLAN
APP_SERVICE_PLAN=${APP_SERVICE_PLAN:-sungertain-plan}

read -p "App Service 名稱 (須全球唯一, 預設: sungertain-pub-$(date +%s)): " APP_SERVICE_NAME
APP_SERVICE_NAME=${APP_SERVICE_NAME:-sungertain-pub-$(date +%s)}

echo ""
echo "📊 設定摘要:"
echo "  資源群組: $RESOURCE_GROUP"
echo "  位置: $LOCATION"
echo "  Key Vault: $KEYVAULT_NAME"
echo "  App Service Plan: $APP_SERVICE_PLAN"
echo "  App Service: $APP_SERVICE_NAME"
echo ""

read -p "確認繼續? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ 已取消"
    exit 1
fi
echo ""

# ========== 開始建立資源 ==========

echo "🔄 開始部署資源..."
echo ""

# Step 1: 建立 Key Vault
echo "1️⃣  建立 Azure Key Vault..."
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-soft-delete true \
  --retention-days 7 \
  --output none
echo "✅ Key Vault 已建立: $KEYVAULT_NAME"
echo ""

# Step 2: 新增密鑰到 Key Vault
echo "2️⃣  新增 API 密鑰到 Key Vault..."
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "G-SYSTEM-API-URL" \
  --value "https://sungertain.deweichiu.com/api/articles/publish" \
  --output none
echo "✅ 已設定: G-SYSTEM-API-URL"

az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "G-SYSTEM-API-KEY" \
  --value "gsy_prod_1a2b3c4d5e6f7g8h9i0j_cowork_2026" \
  --output none
echo "✅ 已設定: G-SYSTEM-API-KEY"
echo ""

# Step 3: 建立 App Service Plan
echo "3️⃣  建立 App Service Plan..."
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux \
  --output none
echo "✅ App Service Plan 已建立: $APP_SERVICE_PLAN"
echo ""

# Step 4: 建立 App Service
echo "4️⃣  建立 App Service..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $APP_SERVICE_NAME \
  --runtime "PYTHON|3.11" \
  --output none
echo "✅ App Service 已建立: $APP_SERVICE_NAME"
APP_SERVICE_URL="https://${APP_SERVICE_NAME}.azurewebsites.net"
echo "   URL: $APP_SERVICE_URL"
echo ""

# Step 5: 啟用 Managed Identity
echo "5️⃣  啟用 Managed Identity..."
az webapp identity assign \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --identities [system] \
  --output none
echo "✅ Managed Identity 已啟用"

IDENTITY_ID=$(az webapp identity show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --query principalId \
  --output tsv)
echo "   Identity ID: $IDENTITY_ID"
echo ""

# Step 6: 設定 Key Vault 訪問原則
echo "6️⃣  設定 Key Vault 訪問原則..."
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --object-id $IDENTITY_ID \
  --secret-permissions get list \
  --output none
echo "✅ Key Vault 訪問原則已設定"
echo ""

# Step 7: 設定應用程式設定
echo "7️⃣  設定應用程式環境變數..."
KEYVAULT_URL="https://${KEYVAULT_NAME}.vault.azure.net/"

az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --settings \
    AZURE_KEYVAULT_URL="$KEYVAULT_URL" \
    LOG_DIR="/home/site/wwwroot/logs" \
    ARTICLES_DIR="/home/site/wwwroot/articles" \
  --output none
echo "✅ 環境變數已設定:"
echo "   AZURE_KEYVAULT_URL: $KEYVAULT_URL"
echo "   LOG_DIR: /home/site/wwwroot/logs"
echo "   ARTICLES_DIR: /home/site/wwwroot/articles"
echo ""

# Step 8: 啟用 Always On
echo "8️⃣  啟用 Always On..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --always-on true \
  --output none
echo "✅ Always On 已啟用"
echo ""

# Step 9: 部署代碼
echo "9️⃣  準備部署代碼..."
read -p "是否現在部署代碼? (y/n): " DEPLOY
if [ "$DEPLOY" = "y" ]; then
    echo "部署代碼中..."
    cd /Users/ericchiu/Documents/sungertain-design/G系統專案

    # 建立 .gitignore
    cat > .gitignore << 'EOF'
.env
*.pyc
__pycache__/
*.log
logs/
.DS_Store
EOF

    # 建立 startup.txt（告訴 App Service 如何啟動）
    cat > startup.txt << 'EOF'
pip install -r requirements.txt --break-system-packages
EOF

    # 初始化 git（如果未初始化）
    if [ ! -d .git ]; then
        git init
        git config user.email "ericapril22th@gmail.com"
        git config user.name "Sungertain System"
    fi

    git add .
    git commit -m "Initial deployment" || true

    # 使用 App Service 的內建部署
    az webapp deployment source config-local-git \
      --resource-group $RESOURCE_GROUP \
      --name $APP_SERVICE_NAME \
      --output none

    GIT_URL=$(az webapp deployment source show \
      --resource-group $RESOURCE_GROUP \
      --name $APP_SERVICE_NAME \
      --query url \
      --output tsv)

    echo ""
    echo "📤 部署 Git 設定:"
    echo "   執行以下命令部署代碼:"
    echo "   git remote add azure $GIT_URL"
    echo "   git push azure master"
    echo ""
fi

# ========== 完成 ==========

echo ""
echo "========================================"
echo "✅ Azure 環境設定完成！"
echo "========================================"
echo ""
echo "📊 部署資訊:"
echo "   訂閱 ID: $SUBSCRIPTION_ID"
echo "   資源群組: $RESOURCE_GROUP"
echo "   Key Vault: $KEYVAULT_NAME"
echo "   App Service: $APP_SERVICE_NAME"
echo "   URL: $APP_SERVICE_URL"
echo ""
echo "🔑 Key Vault 密鑰:"
echo "   G-SYSTEM-API-URL: https://sungertain.deweichiu.com/api/articles/publish"
echo "   G-SYSTEM-API-KEY: (已設定)"
echo ""
echo "🔐 身份設定:"
echo "   Managed Identity: $IDENTITY_ID"
echo "   已授予 Key Vault get/list 權限"
echo ""
echo "📋 下一步:"
echo "   1. 部署代碼: git push azure master"
echo "   2. 查看日誌: az webapp log tail -n $APP_SERVICE_NAME -g $RESOURCE_GROUP"
echo "   3. 設定定時任務: 參考 AZURE_部署指南.md Step 5"
echo ""
echo "💾 設定已保存到環境變數"
echo "   export AZURE_RESOURCE_GROUP=$RESOURCE_GROUP"
echo "   export AZURE_KEYVAULT=$KEYVAULT_NAME"
echo "   export AZURE_APP_SERVICE=$APP_SERVICE_NAME"
echo ""
