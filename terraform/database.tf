resource "random_password" "db_password" {
  length  = 20
  special = false
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-psql2"
  resource_group_name    = azurerm_resource_group.main.name
  location               = "eastus2"
  version                = "16"
  administrator_login    = "medappoint_admin"
  administrator_password = random_password.db_password.result
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  zone                   = "1"
  public_network_access_enabled = true
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_database" "app_db" {
  name      = "medappoint"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

output "db_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}