INSERT INTO bids_bid (id, name, initial_price, status, created_at) 
VALUES (1, 'Vintage Camera', 100.00,  'open', NOW()), (2, 'Antique Vase', 200.00,  'open', NOW()),  (3, 'Rare Book', 150.00,  'closed', NOW())
ON CONFLICT (id) DO NOTHING;

