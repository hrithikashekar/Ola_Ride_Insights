-- Ola Ride Insights | MySQL 8 schema + load (cleaned CSV produced by scripts/01_clean_and_eda.py)
CREATE DATABASE IF NOT EXISTS ola_project;
USE ola_project;

DROP TABLE IF EXISTS ola_rides;
CREATE TABLE ola_rides (
  Booking_ID              VARCHAR(20) PRIMARY KEY,
  Booking_Datetime        DATETIME,
  Date                    DATE,
  Time                    TIME,
  Year_Month              CHAR(7),
  Day                     TINYINT,
  Day_Name                VARCHAR(10),
  Week_Number             TINYINT,
  Hour                    TINYINT,
  Time_Slot               VARCHAR(20),
  Is_Weekend              VARCHAR(8),
  Customer_ID             VARCHAR(12),
  Vehicle_Type            VARCHAR(15),
  Pickup_Location         VARCHAR(40),
  Drop_Location           VARCHAR(40),
  Booking_Status          VARCHAR(25),
  Is_Success              TINYINT,
  Cancelled_By            VARCHAR(20),
  Cancel_Reason_Customer  VARCHAR(60),
  Cancel_Reason_Driver    VARCHAR(60),
  Incomplete_Rides        VARCHAR(15),
  Incomplete_Rides_Reason VARCHAR(30),
  V_TAT                   DECIMAL(6,1) NULL,
  C_TAT                   DECIMAL(6,1) NULL,
  Booking_Value           INT,
  Success_Revenue         INT,
  Payment_Method          VARCHAR(15),
  Ride_Distance           INT,
  Distance_Band           VARCHAR(15),
  Fare_per_Km             DECIMAL(8,2) NULL,
  Driver_Ratings          DECIMAL(2,1) NULL,
  Customer_Ratings        DECIMAL(2,1) NULL,
  Rating_Gap              DECIMAL(3,1) NULL,
  INDEX ix_status (Booking_Status), INDEX ix_vehicle (Vehicle_Type), INDEX ix_customer (Customer_ID), INDEX ix_date (Date)
);

-- Load (enable local_infile). Empty CSV cells -> NULL for the numeric columns.
LOAD DATA LOCAL INFILE 'data/ola_cleaned.csv' INTO TABLE ola_rides
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES
(Booking_ID, Booking_Datetime, Date, Time, Year_Month, Day, Day_Name, Week_Number, Hour, Time_Slot, Is_Weekend,
 Customer_ID, Vehicle_Type, Pickup_Location, Drop_Location, Booking_Status, Is_Success, Cancelled_By,
 Cancel_Reason_Customer, Cancel_Reason_Driver, Incomplete_Rides, Incomplete_Rides_Reason,
 @v_tat, @c_tat, Booking_Value, Success_Revenue, Payment_Method, Ride_Distance, Distance_Band,
 @fare, @dr, @cr, @gap)
SET V_TAT = NULLIF(@v_tat,''), C_TAT = NULLIF(@c_tat,''), Fare_per_Km = NULLIF(@fare,''),
    Driver_Ratings = NULLIF(@dr,''), Customer_Ratings = NULLIF(@cr,''), Rating_Gap = NULLIF(@gap,'');

-- Sanity check: expect 103,024 rows
SELECT COUNT(*) AS total_rows FROM ola_rides;
