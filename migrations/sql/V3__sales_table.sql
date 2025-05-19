CREATE TABLE sales (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID NOT NULL,
  order_item_id UUID NOT NULL,
  product_id UUID NOT NULL,
  category_id UUID,
  channel_id UUID,
  sale_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  amount DECIMAL(10, 4) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_sales_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_sales_order_item FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE,
  CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
  CONSTRAINT fk_sales_category FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE
  SET NULL,
    CONSTRAINT fk_sales_channel FOREIGN KEY (channel_id) REFERENCES sales_channel(id) ON DELETE
  SET NULL
);
create TABLE sales_snapshot(
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  snapshot_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_sales INTEGER NOT NULL,
  total_revenue DECIMAL(14, 4) NOT NULL,
  average_sales DECIMAL(14, 4) NOT NULL,
  average_revenue DECIMAL(14, 4) NOT NULL,
  total_quantity INTEGER NOT NULL,
  total_products INTEGER NOT NULL,
  total_tax DECIMAL(14, 4) NOT NULL,
  total_shipping DECIMAL(14, 4) NOT NULL,
  total_discount DECIMAL(14, 4) NOT NULL,
  interval VARCHAR(20) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);