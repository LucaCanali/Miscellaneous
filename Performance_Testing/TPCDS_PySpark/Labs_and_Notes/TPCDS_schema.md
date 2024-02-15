# TPCDS Schema

## Data

This describes the tables used in the TPCDS benchmark.
For convenience the TPCDS benchmark data at scale 10G and 100G have been made available for downloading  
See also [TPCDS_PySpark README](../README.md) for details on how to download the data and on how to create the schema at any scale.
```
# Get TPCDS data at scale 10G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

# Get TPCDS data at scale 100G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_100.zip
unzip tpcds_100.zip
You can download the TPCDS benchmark data from:
```

## List of the TPCDS tables

```
tpcds_tables = [
        "catalog_returns", "catalog_sales", "inventory", "store_returns",
        "store_sales", "web_returns", "web_sales", "call_center",
        "catalog_page", "customer", "customer_address",
        "customer_demographics", "date_dim", "household_demographics",
        "income_band", "item", "promotion", "reason", "ship_mode",
        "store", "time_dim", "warehouse", "web_page", "web_site"
    ]
```

The description of the tables is:
```
data_path = "./tpcds_10"
for table in tpcds_tables:
    print(table)
    df = spark.read.parquet(f"{data_path}/{table}")
    df.printSchema()
```

```
catalog_returns
root
 |-- cr_returned_date_sk: integer (nullable = true)
 |-- cr_returned_time_sk: integer (nullable = true)
 |-- cr_item_sk: integer (nullable = true)
 |-- cr_refunded_customer_sk: integer (nullable = true)
 |-- cr_refunded_cdemo_sk: integer (nullable = true)
 |-- cr_refunded_hdemo_sk: integer (nullable = true)
 |-- cr_refunded_addr_sk: integer (nullable = true)
 |-- cr_returning_customer_sk: integer (nullable = true)
 |-- cr_returning_cdemo_sk: integer (nullable = true)
 |-- cr_returning_hdemo_sk: integer (nullable = true)
 |-- cr_returning_addr_sk: integer (nullable = true)
 |-- cr_call_center_sk: integer (nullable = true)
 |-- cr_catalog_page_sk: integer (nullable = true)
 |-- cr_ship_mode_sk: integer (nullable = true)
 |-- cr_warehouse_sk: integer (nullable = true)
 |-- cr_reason_sk: integer (nullable = true)
 |-- cr_order_number: long (nullable = true)
 |-- cr_return_quantity: integer (nullable = true)
 |-- cr_return_amount: decimal(7,2) (nullable = true)
 |-- cr_return_tax: decimal(7,2) (nullable = true)
 |-- cr_return_amt_inc_tax: decimal(7,2) (nullable = true)
 |-- cr_fee: decimal(7,2) (nullable = true)
 |-- cr_return_ship_cost: decimal(7,2) (nullable = true)
 |-- cr_refunded_cash: decimal(7,2) (nullable = true)
 |-- cr_reversed_charge: decimal(7,2) (nullable = true)
 |-- cr_store_credit: decimal(7,2) (nullable = true)
 |-- cr_net_loss: decimal(7,2) (nullable = true)

catalog_sales
root
 |-- cs_sold_date_sk: integer (nullable = true)
 |-- cs_sold_time_sk: integer (nullable = true)
 |-- cs_ship_date_sk: integer (nullable = true)
 |-- cs_bill_customer_sk: integer (nullable = true)
 |-- cs_bill_cdemo_sk: integer (nullable = true)
 |-- cs_bill_hdemo_sk: integer (nullable = true)
 |-- cs_bill_addr_sk: integer (nullable = true)
 |-- cs_ship_customer_sk: integer (nullable = true)
 |-- cs_ship_cdemo_sk: integer (nullable = true)
 |-- cs_ship_hdemo_sk: integer (nullable = true)
 |-- cs_ship_addr_sk: integer (nullable = true)
 |-- cs_call_center_sk: integer (nullable = true)
 |-- cs_catalog_page_sk: integer (nullable = true)
 |-- cs_ship_mode_sk: integer (nullable = true)
 |-- cs_warehouse_sk: integer (nullable = true)
 |-- cs_item_sk: integer (nullable = true)
 |-- cs_promo_sk: integer (nullable = true)
 |-- cs_order_number: long (nullable = true)
 |-- cs_quantity: integer (nullable = true)
 |-- cs_wholesale_cost: decimal(7,2) (nullable = true)
 |-- cs_list_price: decimal(7,2) (nullable = true)
 |-- cs_sales_price: decimal(7,2) (nullable = true)
 |-- cs_ext_discount_amt: decimal(7,2) (nullable = true)
 |-- cs_ext_sales_price: decimal(7,2) (nullable = true)
 |-- cs_ext_wholesale_cost: decimal(7,2) (nullable = true)
 |-- cs_ext_list_price: decimal(7,2) (nullable = true)
 |-- cs_ext_tax: decimal(7,2) (nullable = true)
 |-- cs_coupon_amt: decimal(7,2) (nullable = true)
 |-- cs_ext_ship_cost: decimal(7,2) (nullable = true)
 |-- cs_net_paid: decimal(7,2) (nullable = true)
 |-- cs_net_paid_inc_tax: decimal(7,2) (nullable = true)
 |-- cs_net_paid_inc_ship: decimal(7,2) (nullable = true)
 |-- cs_net_paid_inc_ship_tax: decimal(7,2) (nullable = true)
 |-- cs_net_profit: decimal(7,2) (nullable = true)

inventory
root
 |-- inv_date_sk: integer (nullable = true)
 |-- inv_item_sk: integer (nullable = true)
 |-- inv_warehouse_sk: integer (nullable = true)
 |-- inv_quantity_on_hand: integer (nullable = true)

store_returns
root
 |-- sr_returned_date_sk: integer (nullable = true)
 |-- sr_return_time_sk: integer (nullable = true)
 |-- sr_item_sk: integer (nullable = true)
 |-- sr_customer_sk: integer (nullable = true)
 |-- sr_cdemo_sk: integer (nullable = true)
 |-- sr_hdemo_sk: integer (nullable = true)
 |-- sr_addr_sk: integer (nullable = true)
 |-- sr_store_sk: integer (nullable = true)
 |-- sr_reason_sk: integer (nullable = true)
 |-- sr_ticket_number: long (nullable = true)
 |-- sr_return_quantity: integer (nullable = true)
 |-- sr_return_amt: decimal(7,2) (nullable = true)
 |-- sr_return_tax: decimal(7,2) (nullable = true)
 |-- sr_return_amt_inc_tax: decimal(7,2) (nullable = true)
 |-- sr_fee: decimal(7,2) (nullable = true)
 |-- sr_return_ship_cost: decimal(7,2) (nullable = true)
 |-- sr_refunded_cash: decimal(7,2) (nullable = true)
 |-- sr_reversed_charge: decimal(7,2) (nullable = true)
 |-- sr_store_credit: decimal(7,2) (nullable = true)
 |-- sr_net_loss: decimal(7,2) (nullable = true)

store_sales
root
 |-- ss_sold_date_sk: integer (nullable = true)
 |-- ss_sold_time_sk: integer (nullable = true)
 |-- ss_item_sk: integer (nullable = true)
 |-- ss_customer_sk: integer (nullable = true)
 |-- ss_cdemo_sk: integer (nullable = true)
 |-- ss_hdemo_sk: integer (nullable = true)
 |-- ss_addr_sk: integer (nullable = true)
 |-- ss_store_sk: integer (nullable = true)
 |-- ss_promo_sk: integer (nullable = true)
 |-- ss_ticket_number: long (nullable = true)
 |-- ss_quantity: integer (nullable = true)
 |-- ss_wholesale_cost: decimal(7,2) (nullable = true)
 |-- ss_list_price: decimal(7,2) (nullable = true)
 |-- ss_sales_price: decimal(7,2) (nullable = true)
 |-- ss_ext_discount_amt: decimal(7,2) (nullable = true)
 |-- ss_ext_sales_price: decimal(7,2) (nullable = true)
 |-- ss_ext_wholesale_cost: decimal(7,2) (nullable = true)
 |-- ss_ext_list_price: decimal(7,2) (nullable = true)
 |-- ss_ext_tax: decimal(7,2) (nullable = true)
 |-- ss_coupon_amt: decimal(7,2) (nullable = true)
 |-- ss_net_paid: decimal(7,2) (nullable = true)
 |-- ss_net_paid_inc_tax: decimal(7,2) (nullable = true)
 |-- ss_net_profit: decimal(7,2) (nullable = true)

web_returns
root
 |-- wr_returned_date_sk: integer (nullable = true)
 |-- wr_returned_time_sk: integer (nullable = true)
 |-- wr_item_sk: integer (nullable = true)
 |-- wr_refunded_customer_sk: integer (nullable = true)
 |-- wr_refunded_cdemo_sk: integer (nullable = true)
 |-- wr_refunded_hdemo_sk: integer (nullable = true)
 |-- wr_refunded_addr_sk: integer (nullable = true)
 |-- wr_returning_customer_sk: integer (nullable = true)
 |-- wr_returning_cdemo_sk: integer (nullable = true)
 |-- wr_returning_hdemo_sk: integer (nullable = true)
 |-- wr_returning_addr_sk: integer (nullable = true)
 |-- wr_web_page_sk: integer (nullable = true)
 |-- wr_reason_sk: integer (nullable = true)
 |-- wr_order_number: long (nullable = true)
 |-- wr_return_quantity: integer (nullable = true)
 |-- wr_return_amt: decimal(7,2) (nullable = true)
 |-- wr_return_tax: decimal(7,2) (nullable = true)
 |-- wr_return_amt_inc_tax: decimal(7,2) (nullable = true)
 |-- wr_fee: decimal(7,2) (nullable = true)
 |-- wr_return_ship_cost: decimal(7,2) (nullable = true)
 |-- wr_refunded_cash: decimal(7,2) (nullable = true)
 |-- wr_reversed_charge: decimal(7,2) (nullable = true)
 |-- wr_account_credit: decimal(7,2) (nullable = true)
 |-- wr_net_loss: decimal(7,2) (nullable = true)

web_sales
root
 |-- ws_sold_date_sk: integer (nullable = true)
 |-- ws_sold_time_sk: integer (nullable = true)
 |-- ws_ship_date_sk: integer (nullable = true)
 |-- ws_item_sk: integer (nullable = true)
 |-- ws_bill_customer_sk: integer (nullable = true)
 |-- ws_bill_cdemo_sk: integer (nullable = true)
 |-- ws_bill_hdemo_sk: integer (nullable = true)
 |-- ws_bill_addr_sk: integer (nullable = true)
 |-- ws_ship_customer_sk: integer (nullable = true)
 |-- ws_ship_cdemo_sk: integer (nullable = true)
 |-- ws_ship_hdemo_sk: integer (nullable = true)
 |-- ws_ship_addr_sk: integer (nullable = true)
 |-- ws_web_page_sk: integer (nullable = true)
 |-- ws_web_site_sk: integer (nullable = true)
 |-- ws_ship_mode_sk: integer (nullable = true)
 |-- ws_warehouse_sk: integer (nullable = true)
 |-- ws_promo_sk: integer (nullable = true)
 |-- ws_order_number: long (nullable = true)
 |-- ws_quantity: integer (nullable = true)
 |-- ws_wholesale_cost: decimal(7,2) (nullable = true)
 |-- ws_list_price: decimal(7,2) (nullable = true)
 |-- ws_sales_price: decimal(7,2) (nullable = true)
 |-- ws_ext_discount_amt: decimal(7,2) (nullable = true)
 |-- ws_ext_sales_price: decimal(7,2) (nullable = true)
 |-- ws_ext_wholesale_cost: decimal(7,2) (nullable = true)
 |-- ws_ext_list_price: decimal(7,2) (nullable = true)
 |-- ws_ext_tax: decimal(7,2) (nullable = true)
 |-- ws_coupon_amt: decimal(7,2) (nullable = true)
 |-- ws_ext_ship_cost: decimal(7,2) (nullable = true)
 |-- ws_net_paid: decimal(7,2) (nullable = true)
 |-- ws_net_paid_inc_tax: decimal(7,2) (nullable = true)
 |-- ws_net_paid_inc_ship: decimal(7,2) (nullable = true)
 |-- ws_net_paid_inc_ship_tax: decimal(7,2) (nullable = true)
 |-- ws_net_profit: decimal(7,2) (nullable = true)

call_center
root
 |-- cc_call_center_sk: integer (nullable = true)
 |-- cc_call_center_id: string (nullable = true)
 |-- cc_rec_start_date: date (nullable = true)
 |-- cc_rec_end_date: date (nullable = true)
 |-- cc_closed_date_sk: integer (nullable = true)
 |-- cc_open_date_sk: integer (nullable = true)
 |-- cc_name: string (nullable = true)
 |-- cc_class: string (nullable = true)
 |-- cc_employees: integer (nullable = true)
 |-- cc_sq_ft: integer (nullable = true)
 |-- cc_hours: string (nullable = true)
 |-- cc_manager: string (nullable = true)
 |-- cc_mkt_id: integer (nullable = true)
 |-- cc_mkt_class: string (nullable = true)
 |-- cc_mkt_desc: string (nullable = true)
 |-- cc_market_manager: string (nullable = true)
 |-- cc_division: integer (nullable = true)
 |-- cc_division_name: string (nullable = true)
 |-- cc_company: integer (nullable = true)
 |-- cc_company_name: string (nullable = true)
 |-- cc_street_number: string (nullable = true)
 |-- cc_street_name: string (nullable = true)
 |-- cc_street_type: string (nullable = true)
 |-- cc_suite_number: string (nullable = true)
 |-- cc_city: string (nullable = true)
 |-- cc_county: string (nullable = true)
 |-- cc_state: string (nullable = true)
 |-- cc_zip: string (nullable = true)
 |-- cc_country: string (nullable = true)
 |-- cc_gmt_offset: decimal(5,2) (nullable = true)
 |-- cc_tax_percentage: decimal(5,2) (nullable = true)

catalog_page
root
 |-- cp_catalog_page_sk: integer (nullable = true)
 |-- cp_catalog_page_id: string (nullable = true)
 |-- cp_start_date_sk: integer (nullable = true)
 |-- cp_end_date_sk: integer (nullable = true)
 |-- cp_department: string (nullable = true)
 |-- cp_catalog_number: integer (nullable = true)
 |-- cp_catalog_page_number: integer (nullable = true)
 |-- cp_description: string (nullable = true)
 |-- cp_type: string (nullable = true)

customer
root
 |-- c_customer_sk: integer (nullable = true)
 |-- c_customer_id: string (nullable = true)
 |-- c_current_cdemo_sk: integer (nullable = true)
 |-- c_current_hdemo_sk: integer (nullable = true)
 |-- c_current_addr_sk: integer (nullable = true)
 |-- c_first_shipto_date_sk: integer (nullable = true)
 |-- c_first_sales_date_sk: integer (nullable = true)
 |-- c_salutation: string (nullable = true)
 |-- c_first_name: string (nullable = true)
 |-- c_last_name: string (nullable = true)
 |-- c_preferred_cust_flag: string (nullable = true)
 |-- c_birth_day: integer (nullable = true)
 |-- c_birth_month: integer (nullable = true)
 |-- c_birth_year: integer (nullable = true)
 |-- c_birth_country: string (nullable = true)
 |-- c_login: string (nullable = true)
 |-- c_email_address: string (nullable = true)
 |-- c_last_review_date: string (nullable = true)

customer_address
root
 |-- ca_address_sk: integer (nullable = true)
 |-- ca_address_id: string (nullable = true)
 |-- ca_street_number: string (nullable = true)
 |-- ca_street_name: string (nullable = true)
 |-- ca_street_type: string (nullable = true)
 |-- ca_suite_number: string (nullable = true)
 |-- ca_city: string (nullable = true)
 |-- ca_county: string (nullable = true)
 |-- ca_state: string (nullable = true)
 |-- ca_zip: string (nullable = true)
 |-- ca_country: string (nullable = true)
 |-- ca_gmt_offset: decimal(5,2) (nullable = true)
 |-- ca_location_type: string (nullable = true)

customer_demographics
root
 |-- cd_demo_sk: integer (nullable = true)
 |-- cd_gender: string (nullable = true)
 |-- cd_marital_status: string (nullable = true)
 |-- cd_education_status: string (nullable = true)
 |-- cd_purchase_estimate: integer (nullable = true)
 |-- cd_credit_rating: string (nullable = true)
 |-- cd_dep_count: integer (nullable = true)
 |-- cd_dep_employed_count: integer (nullable = true)
 |-- cd_dep_college_count: integer (nullable = true)

date_dim
root
 |-- d_date_sk: integer (nullable = true)
 |-- d_date_id: string (nullable = true)
 |-- d_date: date (nullable = true)
 |-- d_month_seq: integer (nullable = true)
 |-- d_week_seq: integer (nullable = true)
 |-- d_quarter_seq: integer (nullable = true)
 |-- d_year: integer (nullable = true)
 |-- d_dow: integer (nullable = true)
 |-- d_moy: integer (nullable = true)
 |-- d_dom: integer (nullable = true)
 |-- d_qoy: integer (nullable = true)
 |-- d_fy_year: integer (nullable = true)
 |-- d_fy_quarter_seq: integer (nullable = true)
 |-- d_fy_week_seq: integer (nullable = true)
 |-- d_day_name: string (nullable = true)
 |-- d_quarter_name: string (nullable = true)
 |-- d_holiday: string (nullable = true)
 |-- d_weekend: string (nullable = true)
 |-- d_following_holiday: string (nullable = true)
 |-- d_first_dom: integer (nullable = true)
 |-- d_last_dom: integer (nullable = true)
 |-- d_same_day_ly: integer (nullable = true)
 |-- d_same_day_lq: integer (nullable = true)
 |-- d_current_day: string (nullable = true)
 |-- d_current_week: string (nullable = true)
 |-- d_current_month: string (nullable = true)
 |-- d_current_quarter: string (nullable = true)
 |-- d_current_year: string (nullable = true)

household_demographics
root
 |-- hd_demo_sk: integer (nullable = true)
 |-- hd_income_band_sk: integer (nullable = true)
 |-- hd_buy_potential: string (nullable = true)
 |-- hd_dep_count: integer (nullable = true)
 |-- hd_vehicle_count: integer (nullable = true)

income_band
root
 |-- ib_income_band_sk: integer (nullable = true)
 |-- ib_lower_bound: integer (nullable = true)
 |-- ib_upper_bound: integer (nullable = true)

item
root
 |-- i_item_sk: integer (nullable = true)
 |-- i_item_id: string (nullable = true)
 |-- i_rec_start_date: date (nullable = true)
 |-- i_rec_end_date: date (nullable = true)
 |-- i_item_desc: string (nullable = true)
 |-- i_current_price: decimal(7,2) (nullable = true)
 |-- i_wholesale_cost: decimal(7,2) (nullable = true)
 |-- i_brand_id: integer (nullable = true)
 |-- i_brand: string (nullable = true)
 |-- i_class_id: integer (nullable = true)
 |-- i_class: string (nullable = true)
 |-- i_category_id: integer (nullable = true)
 |-- i_category: string (nullable = true)
 |-- i_manufact_id: integer (nullable = true)
 |-- i_manufact: string (nullable = true)
 |-- i_size: string (nullable = true)
 |-- i_formulation: string (nullable = true)
 |-- i_color: string (nullable = true)
 |-- i_units: string (nullable = true)
 |-- i_container: string (nullable = true)
 |-- i_manager_id: integer (nullable = true)
 |-- i_product_name: string (nullable = true)

promotion
root
 |-- p_promo_sk: integer (nullable = true)
 |-- p_promo_id: string (nullable = true)
 |-- p_start_date_sk: integer (nullable = true)
 |-- p_end_date_sk: integer (nullable = true)
 |-- p_item_sk: integer (nullable = true)
 |-- p_cost: decimal(15,2) (nullable = true)
 |-- p_response_target: integer (nullable = true)
 |-- p_promo_name: string (nullable = true)
 |-- p_channel_dmail: string (nullable = true)
 |-- p_channel_email: string (nullable = true)
 |-- p_channel_catalog: string (nullable = true)
 |-- p_channel_tv: string (nullable = true)
 |-- p_channel_radio: string (nullable = true)
 |-- p_channel_press: string (nullable = true)
 |-- p_channel_event: string (nullable = true)
 |-- p_channel_demo: string (nullable = true)
 |-- p_channel_details: string (nullable = true)
 |-- p_purpose: string (nullable = true)
 |-- p_discount_active: string (nullable = true)

reason
root
 |-- r_reason_sk: integer (nullable = true)
 |-- r_reason_id: string (nullable = true)
 |-- r_reason_desc: string (nullable = true)

ship_mode
root
 |-- sm_ship_mode_sk: integer (nullable = true)
 |-- sm_ship_mode_id: string (nullable = true)
 |-- sm_type: string (nullable = true)
 |-- sm_code: string (nullable = true)
 |-- sm_carrier: string (nullable = true)
 |-- sm_contract: string (nullable = true)

store
root
 |-- s_store_sk: integer (nullable = true)
 |-- s_store_id: string (nullable = true)
 |-- s_rec_start_date: date (nullable = true)
 |-- s_rec_end_date: date (nullable = true)
 |-- s_closed_date_sk: integer (nullable = true)
 |-- s_store_name: string (nullable = true)
 |-- s_number_employees: integer (nullable = true)
 |-- s_floor_space: integer (nullable = true)
 |-- s_hours: string (nullable = true)
 |-- s_manager: string (nullable = true)
 |-- s_market_id: integer (nullable = true)
 |-- s_geography_class: string (nullable = true)
 |-- s_market_desc: string (nullable = true)
 |-- s_market_manager: string (nullable = true)
 |-- s_division_id: integer (nullable = true)
 |-- s_division_name: string (nullable = true)
 |-- s_company_id: integer (nullable = true)
 |-- s_company_name: string (nullable = true)
 |-- s_street_number: string (nullable = true)
 |-- s_street_name: string (nullable = true)
 |-- s_street_type: string (nullable = true)
 |-- s_suite_number: string (nullable = true)
 |-- s_city: string (nullable = true)
 |-- s_county: string (nullable = true)
 |-- s_state: string (nullable = true)
 |-- s_zip: string (nullable = true)
 |-- s_country: string (nullable = true)
 |-- s_gmt_offset: decimal(5,2) (nullable = true)
 |-- s_tax_precentage: decimal(5,2) (nullable = true)

time_dim
root
 |-- t_time_sk: integer (nullable = true)
 |-- t_time_id: string (nullable = true)
 |-- t_time: integer (nullable = true)
 |-- t_hour: integer (nullable = true)
 |-- t_minute: integer (nullable = true)
 |-- t_second: integer (nullable = true)
 |-- t_am_pm: string (nullable = true)
 |-- t_shift: string (nullable = true)
 |-- t_sub_shift: string (nullable = true)
 |-- t_meal_time: string (nullable = true)

warehouse
root
 |-- w_warehouse_sk: integer (nullable = true)
 |-- w_warehouse_id: string (nullable = true)
 |-- w_warehouse_name: string (nullable = true)
 |-- w_warehouse_sq_ft: integer (nullable = true)
 |-- w_street_number: string (nullable = true)
 |-- w_street_name: string (nullable = true)
 |-- w_street_type: string (nullable = true)
 |-- w_suite_number: string (nullable = true)
 |-- w_city: string (nullable = true)
 |-- w_county: string (nullable = true)
 |-- w_state: string (nullable = true)
 |-- w_zip: string (nullable = true)
 |-- w_country: string (nullable = true)
 |-- w_gmt_offset: decimal(5,2) (nullable = true)

web_page
root
 |-- wp_web_page_sk: integer (nullable = true)
 |-- wp_web_page_id: string (nullable = true)
 |-- wp_rec_start_date: date (nullable = true)
 |-- wp_rec_end_date: date (nullable = true)
 |-- wp_creation_date_sk: integer (nullable = true)
 |-- wp_access_date_sk: integer (nullable = true)
 |-- wp_autogen_flag: string (nullable = true)
 |-- wp_customer_sk: integer (nullable = true)
 |-- wp_url: string (nullable = true)
 |-- wp_type: string (nullable = true)
 |-- wp_char_count: integer (nullable = true)
 |-- wp_link_count: integer (nullable = true)
 |-- wp_image_count: integer (nullable = true)
 |-- wp_max_ad_count: integer (nullable = true)

web_site
root
 |-- web_site_sk: integer (nullable = true)
 |-- web_site_id: string (nullable = true)
 |-- web_rec_start_date: date (nullable = true)
 |-- web_rec_end_date: date (nullable = true)
 |-- web_name: string (nullable = true)
 |-- web_open_date_sk: integer (nullable = true)
 |-- web_close_date_sk: integer (nullable = true)
 |-- web_class: string (nullable = true)
 |-- web_manager: string (nullable = true)
 |-- web_mkt_id: integer (nullable = true)
 |-- web_mkt_class: string (nullable = true)
 |-- web_mkt_desc: string (nullable = true)
 |-- web_market_manager: string (nullable = true)
 |-- web_company_id: integer (nullable = true)
 |-- web_company_name: string (nullable = true)
 |-- web_street_number: string (nullable = true)
 |-- web_street_name: string (nullable = true)
 |-- web_street_type: string (nullable = true)
 |-- web_suite_number: string (nullable = true)
 |-- web_city: string (nullable = true)
 |-- web_county: string (nullable = true)
 |-- web_state: string (nullable = true)
 |-- web_zip: string (nullable = true)
 |-- web_country: string (nullable = true)
 |-- web_gmt_offset: decimal(5,2) (nullable = true)
 |-- web_tax_percentage: decimal(5,2) (nullable = true)
```