-- =====================================================================
-- Ola Ride Insights | 10 required SQL questions (MySQL 8 / ANSI; also runs on SQLite)
-- Table: ola_rides (cleaned).  Booking_Status in: Success | Canceled by Customer |
--        Canceled by Driver | Driver Not Found
-- =====================================================================

-- Q1. Retrieve all successful bookings
-- name: Q1 - All successful bookings
SELECT * FROM ola_rides WHERE Booking_Status = 'Success';

-- Q2. Average ride distance for each vehicle type (successful rides; cancelled rides have 0 km by definition)
-- name: Q2 - Avg ride distance by vehicle type
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_ride_distance_km
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY avg_ride_distance_km DESC;

-- Q3. Total number of rides cancelled by customers
-- name: Q3 - Total rides cancelled by customers
SELECT COUNT(*) AS cancelled_by_customer
FROM ola_rides WHERE Booking_Status = 'Canceled by Customer';

-- Q4. Top 5 customers by number of rides
-- name: Q4 - Top 5 customers by number of rides
SELECT Customer_ID, COUNT(*) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC, Customer_ID
LIMIT 5;

-- Q5. Rides cancelled by drivers due to personal & car related issues
-- name: Q5 - Driver cancellations: personal and car related issue
SELECT COUNT(*) AS driver_cancel_personal_car_issue
FROM ola_rides
WHERE Booking_Status = 'Canceled by Driver'
  AND Cancel_Reason_Driver = 'Personal & Car related issue';

-- Q6. Max and min driver ratings for Prime Sedan bookings
-- name: Q6 - Max/Min driver rating for Prime Sedan
SELECT MAX(Driver_Ratings) AS max_driver_rating, MIN(Driver_Ratings) AS min_driver_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Ratings IS NOT NULL;

-- Q7. All rides where payment was made via UPI
-- name: Q7 - Rides paid via UPI
SELECT * FROM ola_rides WHERE Payment_Method = 'UPI';

-- Q8. Average customer rating per vehicle type
-- name: Q8 - Avg customer rating by vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Ratings), 2) AS avg_customer_rating
FROM ola_rides
WHERE Customer_Ratings IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

-- Q9. Total booking value of rides completed successfully
-- name: Q9 - Total booking value of successful rides
SELECT SUM(Booking_Value) AS total_success_booking_value
FROM ola_rides WHERE Booking_Status = 'Success';

-- Q10. All incomplete rides along with the reason
-- name: Q10 - Incomplete rides with reason
SELECT Booking_ID, Customer_ID, Vehicle_Type, Booking_Status, Ride_Distance, Booking_Value, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes'
ORDER BY Incomplete_Rides_Reason, Booking_ID;
