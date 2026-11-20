-- Extra business-insight queries (feed the Streamlit app + Power BI validation)

-- name: B1 - Vehicle type scorecard (slide 2 table)
SELECT Vehicle_Type,
       SUM(Booking_Value)                                         AS total_booking_value,
       SUM(CASE WHEN Booking_Status='Success' THEN Booking_Value END) AS success_booking_value,
       ROUND(AVG(CASE WHEN Booking_Status='Success' THEN Ride_Distance END),2) AS avg_distance_km,
       SUM(Ride_Distance)                                         AS total_distance_km,
       ROUND(100.0*SUM(Is_Success)/COUNT(*),1)                    AS success_rate_pct
FROM ola_rides GROUP BY Vehicle_Type ORDER BY total_distance_km DESC;

-- name: B2 - Booking status breakdown
SELECT Booking_Status, COUNT(*) AS rides, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (),2) AS pct
FROM ola_rides GROUP BY Booking_Status ORDER BY rides DESC;

-- name: B3 - Peak demand hours
SELECT Hour, COUNT(*) AS bookings, SUM(Is_Success) AS successful, ROUND(100.0*SUM(Is_Success)/COUNT(*),1) AS success_rate_pct
FROM ola_rides GROUP BY Hour ORDER BY bookings DESC;

-- name: B4 - Revenue by payment method (successful rides)
SELECT Payment_Method, COUNT(*) AS rides, SUM(Booking_Value) AS revenue,
       ROUND(100.0*SUM(Booking_Value)/SUM(SUM(Booking_Value)) OVER (),1) AS revenue_pct
FROM ola_rides WHERE Booking_Status='Success' GROUP BY Payment_Method ORDER BY revenue DESC;

-- name: B5 - Top 5 customers by total booking value (successful rides)
SELECT Customer_ID, COUNT(*) AS rides, SUM(Booking_Value) AS total_booking_value
FROM ola_rides WHERE Booking_Status='Success'
GROUP BY Customer_ID ORDER BY total_booking_value DESC LIMIT 5;

-- name: B6 - Cancellation reasons (customer)
SELECT Cancel_Reason_Customer AS reason, COUNT(*) AS rides
FROM ola_rides WHERE Booking_Status='Canceled by Customer' GROUP BY 1 ORDER BY rides DESC;

-- name: B7 - Cancellation reasons (driver)
SELECT Cancel_Reason_Driver AS reason, COUNT(*) AS rides
FROM ola_rides WHERE Booking_Status='Canceled by Driver' GROUP BY 1 ORDER BY rides DESC;

-- name: B8 - Top pickup locations by cancellation rate (anomaly / ops hotspots)
SELECT Pickup_Location, COUNT(*) AS bookings,
       ROUND(100.0*SUM(CASE WHEN Is_Success=0 THEN 1 ELSE 0 END)/COUNT(*),1) AS failure_rate_pct
FROM ola_rides GROUP BY Pickup_Location HAVING COUNT(*) > 500 ORDER BY failure_rate_pct DESC LIMIT 10;

-- name: B9 - Customers with 3+ cancelled bookings (anomaly review list)
SELECT Customer_ID, COUNT(*) AS cancelled_rides FROM ola_rides
WHERE Booking_Status IN ('Canceled by Customer') GROUP BY Customer_ID HAVING COUNT(*) >= 3 ORDER BY cancelled_rides DESC;

-- name: B10 - Daily ride volume by status
SELECT Date, Booking_Status, COUNT(*) AS rides FROM ola_rides GROUP BY Date, Booking_Status ORDER BY Date;
