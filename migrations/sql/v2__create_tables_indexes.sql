-- Create indexes for better performance
-- Product indexes
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_product_status ON product(status);
CREATE INDEX idx_product_created_by ON product(created_by);
CREATE INDEX idx_product_sku ON product(sku);
-- Inventory indexes
CREATE INDEX idx_investory_product ON investory(product_id);
CREATE INDEX idx_investory_quantity ON investory(quantity);
CREATE INDEX idx_investory_restock_date ON investory(last_restock_date);
-- Order indexes
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_channel ON orders(channel_id);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
CREATE INDEX idx_orders_total_amount ON orders(total_amount);
-- Order items indexes
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
-- Inventory history indexes
CREATE INDEX idx_inventory_history_inventory ON inventory_history(inventory_id);
CREATE INDEX idx_inventory_history_changed_by ON inventory_history(changed_by);
CREATE INDEX idx_inventory_history_created_at ON inventory_history(created_at);
-- Category indexes
CREATE INDEX idx_category_parent ON category(parent_id);
CREATE INDEX idx_category_status ON category(status);
CREATE INDEX idx_category_identifier ON category(identifier);
-- User indexes
CREATE INDEX idx_users_status ON users(status);
-- Sales channel indexes
CREATE INDEX idx_sales_channel_status ON sales_channel(status);