-- ========================================================
-- Seed Data for Customer Feedback Analysis System
-- ========================================================

USE `customer_feedback_db`;

-- 1. Seed Categories
INSERT INTO `categories` (`name`, `description`, `is_active`) VALUES
('Product Quality', 'Feedbacks about product durability, build, and specifications', 1),
('Customer Support', 'Feedbacks about help desk responsiveness and agent courtesy', 1),
('Billing/Pricing', 'Feedbacks concerning subscriptions, charges, invoices, and pricing', 1),
('Delivery/Speed', 'Feedbacks on delivery turnaround time, logistics, and tracking', 1),
('Usability/UI', 'Feedbacks regarding website/app user interface and UX workflow', 1),
('General', 'General customer feedback, comments, and inquiries', 1)
ON DUPLICATE KEY UPDATE `description` = VALUES(`description`);

-- 2. Seed Users
-- Passwords:
-- Admin: AdminPassword123!
-- Customer: Customer123!
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `phone`, `bio`) VALUES
(1, 'System Administrator', 'admin@feedbackai.com', 'scrypt:32768:8:1$W3BlMsnI6OmmLmWr$6db9d38c281c41b77d71dc521763f040e5dacc51448f563bedb403c1621f38faefd9c178ef531ae9d112ea8f885a62dd1f06d950eb305eecc1cf404e67e9844a', 'admin', '+91 9876543210', 'Lead operations and feedback analyst.'),
(2, 'John Doe', 'john.doe@example.com', 'scrypt:32768:8:1$4HN0YhqgJtRcZGws$673ec000293d55eae8370c789f6e80e7bd00ffc33e9636d91447027fa1eaee247a7b6fbfb25cbd86eb5e8c6870775272ac6c71912c7f8d0716d1b41eb9e3f376', 'customer', '+91 9811122233', 'Verified Enterprise Customer.'),
(3, 'Priya Sundaram', 'priya.s@example.com', 'scrypt:32768:8:1$4HN0YhqgJtRcZGws$673ec000293d55eae8370c789f6e80e7bd00ffc33e9636d91447027fa1eaee247a7b6fbfb25cbd86eb5e8c6870775272ac6c71912c7f8d0716d1b41eb9e3f376', 'customer', '+91 9844455566', 'Frequent user from Chennai.')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- 3. Seed Feedbacks (Diverse Real-world samples: English, Tamil, Tanglish)
INSERT INTO `feedbacks` 
(`id`, `user_id`, `customer_name`, `customer_email`, `rating`, `feedback_text`, `category`, `status`, `priority`, `sentiment`, `sentiment_score`, `emotion`, `aspect`, `aspect_sentiment`, `spam_probability`, `is_spam`, `language`, `summary`, `recommendation`, `admin_notes`, `created_at`) 
VALUES
(1, 2, 'John Doe', 'john.doe@example.com', 5, 
'The latest update is outstanding! The user interface is so clean, intuitive, and navigation is buttery smooth. Kudos to the engineering team.', 
'Usability/UI', 'resolved', 'low', 'positive', 0.92, 'joy', 'UI/UX', 'positive', 0.02, 0, 'English', 
'Customer loved the newest UI update highlighting speed and smooth navigation.', 
'Document UI design patterns used in this release as best practices for future releases.', 
'Shared praise with frontend dev lead.', 
NOW() - INTERVAL 10 DAY),

(2, 3, 'Priya Sundaram', 'priya.s@example.com', 1, 
'Money deducted twice during checkout and still got no confirmation email! Support team is not answering calls. Horrible experience, refund my money immediately!', 
'Billing/Pricing', 'under_review', 'critical', 'negative', -0.95, 'anger', 'Pricing', 'negative', 0.05, 0, 'English', 
'Double billing during checkout with unresponsive support helpline, customer demanding immediate refund.', 
'Initiate instant reconciliation with the payment gateway and contact customer via phone within 1 hour.', 
'Investigating payment gateway log reference #TXN992.', 
NOW() - INTERVAL 8 DAY),

(3, 2, 'John Doe', 'john.doe@example.com', 4, 
'Delivery was super fast within 24 hours. The packaging was neat, but please provide real-time GPS tracking on the mobile app.', 
'Delivery/Speed', 'resolved', 'medium', 'positive', 0.75, 'joy', 'Delivery/Speed', 'positive', 0.03, 0, 'English', 
'Fast 24-hour delivery appreciated, requested real-time GPS delivery tracking feature.', 
'Prioritize real-time driver tracking milestone in the mobile app product roadmap.', 
'Forwarded feature request to logistics product squad.', 
NOW() - INTERVAL 7 DAY),

(4, NULL, 'Karthik Raja', 'karthik.raja@testmail.com', 2, 
'App romba slow-va irukku. Login panna 2 minutes aaguthu. Please fix this bug quickly.', 
'Usability/UI', 'new', 'high', 'negative', -0.65, 'sadness', 'Features/Performance', 'negative', 0.04, 0, 'Tanglish', 
'App takes over 2 minutes to log in and exhibits severe latency.', 
'Inspect auth endpoint latency and optimize database index queries on login authentication.', 
NULL, 
NOW() - INTERVAL 6 DAY),

(5, NULL, 'Anitha Murugan', 'anitha.m@testmail.com', 5, 
'வாடிக்கையாளர் சேவை மிகவும் அருமை. என் பிரச்சனைக்கு உடனடியாக தீர்வு கிடைத்தது. நன்றி!', 
'Customer Support', 'resolved', 'low', 'positive', 0.95, 'joy', 'Customer Support', 'positive', 0.01, 0, 'Tamil', 
'Customer expressed gratitude for exceptionally swift and helpful support resolution.', 
'Reward the support associate on duty for exceptional multilingual customer satisfaction.', 
'Handled by agent Sneha.', 
NOW() - INTERVAL 5 DAY),

(6, 3, 'Priya Sundaram', 'priya.s@example.com', 3, 
'Pricing is reasonable compared to competitors, but customer support takes too long to respond to chat tickets. Fair service overall.', 
'Customer Support', 'new', 'medium', 'neutral', 0.10, 'neutral', 'Customer Support', 'neutral', 0.02, 0, 'English', 
'Good pricing structure, but customer support chat response SLA needs improvement.', 
'Implement automated chatbot routing during peak hours to reduce initial response wait times.', 
NULL, 
NOW() - INTERVAL 4 DAY),

(7, NULL, 'Spam Bot', 'freegift247@xyzmarketing.ru', 1, 
'CLICK HERE NOW TO WIN FREE 50000 CASH PRIZE $$$ http://spamlink.xyz/win BUY CHEAP BITCOIN FAST', 
'General', 'spam', 'low', 'neutral', 0.00, 'neutral', 'General', 'neutral', 0.99, 1, 'English', 
'Promotional spam attempt with malicious URLs.', 
'Block sender domain and blacklist IP from feedback submission portal.', 
'Automatically flagged as spam.', 
NOW() - INTERVAL 3 DAY),

(8, NULL, 'Suresh Kumar', 'suresh.k@testmail.com', 4, 
'Product quality super-ah irukku. Romba nalla build quality. Delivery mattum konjam fast panna nalla irukkum.', 
'Product Quality', 'new', 'medium', 'positive', 0.68, 'joy', 'Product Quality', 'positive', 0.03, 0, 'Tanglish', 
'Pleased with solid build and product quality, requested faster delivery turnaround.', 
'Maintain high quality manufacturing while auditing regional courier delivery times.', 
NULL, 
NOW() - INTERVAL 2 DAY),

(9, NULL, 'Meenakshi Raman', 'meenakshi.r@testmail.com', 1, 
'பொருளின் தரம் மிக மோசம். இரண்டு நாட்களிலேயே உடைந்துவிட்டது. பணத்தை திருப்பித் தரவும்.', 
'Product Quality', 'under_review', 'critical', 'negative', -0.91, 'anger', 'Product Quality', 'negative', 0.02, 0, 'Tamil', 
'Product broke within two days of receipt; customer is demanding immediate return and refund.', 
'Process immediate product replacement/refund and raise quality alert with OEM vendor.', 
'Replacement dispatch pending approval.', 
NOW() - INTERVAL 1 DAY),

(10, 2, 'John Doe', 'john.doe@example.com', 5, 
'Customer support agent Rahul was very courteous and resolved my billing discrepancy in minutes. Amazing service!', 
'Customer Support', 'resolved', 'low', 'positive', 0.88, 'joy', 'Customer Support', 'positive', 0.01, 0, 'English', 
'Agent Rahul provided swift and courteous resolution for billing discrepancy.', 
'Recognize Rahul in weekly team shoutout for exemplary customer care.', 
'Resolved with 5-star customer CSAT.', 
NOW())
ON DUPLICATE KEY UPDATE `rating` = VALUES(`rating`);

-- 4. Seed Granular Aspects
INSERT INTO `feedback_aspects` (`feedback_id`, `aspect_name`, `sentiment`, `confidence`) VALUES
(1, 'UI/UX', 'positive', 0.95),
(2, 'Pricing', 'negative', 0.98),
(2, 'Customer Support', 'negative', 0.92),
(3, 'Delivery/Speed', 'positive', 0.89),
(3, 'UI/UX', 'neutral', 0.60),
(4, 'Features/Performance', 'negative', 0.85),
(5, 'Customer Support', 'positive', 0.97),
(6, 'Pricing', 'positive', 0.70),
(6, 'Customer Support', 'negative', 0.65),
(8, 'Product Quality', 'positive', 0.90),
(8, 'Delivery/Speed', 'neutral', 0.55),
(9, 'Product Quality', 'negative', 0.95),
(10, 'Customer Support', 'positive', 0.94);
