DROP DATABASE IF EXISTS makeup;

CREATE DATABASE makeup;

\c makeup

CREATE TABLE products
(
    id SERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    NAME TEXT NOT NULL,
    photo_url TEXT,
    price INT,
    review TEXT,
    available BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO products
(brand, name,photo_url,price,review,available)

VALUES
('nailColor','Sally Hansen','https://i5.walmartimages.com/asr/ca6e2c88-4323-4ddd-8513-3215d4e62a88.0bc0e4c09f09b255ea144c1b4a2cc76f.jpeg?odnWidth=undefined&odnHeight=undefined&odnBg=ffffff',5,'quick dry and no chip nail color','t'),
('mascara','Maybelline','https://images.beautybay.com/eoaaqxyywn6o/MAYB0017F_1.jpg_s3.lmb_el3tnl/113d2e19283e54471a938a628eeeaf8f/MAYB0017F_1.jpg?w=1000&fm=jpg&fl=progressive&q=70',11,'amazing for volumanizing lashes','t'),
('lipstick','Mac','https://belk.scene7.com/is/image/Belk?layer=0&src=5900090_SK6M_A_500&$DWP_PRODUCT_PDP_LARGE$',24,'long lasting adorable color','t'),
( 'foundation','Covergirl','https://cdn11.bigcommerce.com/s-z4n81jv/images/stencil/1280x1280/attribute_rule_images/40128_source_1536178554.jpg',11,' smooth skin ,stays 24 hours full coverage for your face','t'),
('brushes', 'Dr.brushes',null,null,null,'t');




Create TABLE
CREATE TABLE users(
	id serial PRIMARY KEY,
	fullname VARCHAR ( 100 ) NOT NULL,
	username VARCHAR ( 50 ) NOT NULL,
	password VARCHAR ( 255 ) NOT NULL,
	email VARCHAR ( 50 ) NOT NULL
);



