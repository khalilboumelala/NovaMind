SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Create the novamind database (handled by MYSQL_DATABASE, but included for clarity)
-- CREATE DATABASE IF NOT EXISTS novamind;
USE novamind;

-- Table structure for `user`
CREATE TABLE `user` (
  `username` varchar(20) NOT NULL,
  `email` varchar(50) DEFAULT NULL,
  `join_date` date NOT NULL, -- Removed DEFAULT current_timestamp() due to MySQL 8.0 restriction
  `password` varchar(20) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert data into `user`
INSERT INTO `user` (`username`, `email`, `join_date`, `password`, `id`) VALUES
('username', NULL, '2025-04-23', 'username', 1);

-- Table structure for `conversation_threads`
CREATE TABLE `conversation_threads` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `conversation_threads_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert data into `conversation_threads`
INSERT INTO `conversation_threads` (`id`, `user_id`, `title`, `created_at`) VALUES
(2, 1, 'New Conversation', '2025-04-29 20:24:15'),
(3, 1, 'New Conversation', '2025-05-06 13:09:17'),
(4, 1, 'New Conversation', '2025-05-06 13:19:43'),
(5, 1, 'New Conversation', '2025-05-06 13:46:22'),
(6, 1, 'New Conversation', '2025-05-06 13:47:16'),
(7, 1, 'New Conversation', '2025-05-06 14:04:15'),
(8, 1, 'New Conversation', '2025-05-06 14:18:57'),
(9, 1, 'New Conversation', '2025-05-06 15:09:38'),
(10, 1, 'New Conversation', '2025-05-06 15:13:44'),
(11, 1, 'New Conversation', '2025-05-07 09:32:49'),
(12, 1, 'New Conversation', '2025-05-07 09:32:53'),
(13, 1, 'New Conversation', '2025-05-07 09:41:00'),
(14, 1, 'New Conversation', '2025-05-07 09:41:08'),
(15, 1, 'New Conversation', '2025-05-07 09:50:22'),
(16, 1, 'New Conversation', '2025-05-07 09:55:23'),
(17, 1, 'New Conversation', '2025-05-07 09:58:58'),
(18, 1, 'New Conversation', '2025-05-07 10:16:35'),
(19, 1, 'New Conversation', '2025-05-07 10:17:18');

-- Table structure for `enterprise_info`
CREATE TABLE `enterprise_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `enterprise_name` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `sector` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `founded_year` int(11) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `other_notes` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `enterprise_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for `messages`
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thread_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `role` enum('user','assistant') NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `thread_id` (`thread_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`thread_id`) REFERENCES `conversation_threads` (`id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert data into `messages`
INSERT INTO `messages` (`id`, `thread_id`, `user_id`, `message`, `role`, `created_at`) VALUES
(1, 3, 1, 'aCreate a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:17:54'),
(2, 3, 1, 'aCreate a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:19:17'),
(3, 4, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:20:16'),
(4, 4, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:24:41'),
(5, 5, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:46:31'),
(6, 6, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 13:47:18'),
(7, 6, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 14:02:54'),
(8, 7, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 14:04:17'),
(9, 8, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 14:19:02'),
(10, 8, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 14:55:06'),
(11, 8, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 15:08:57'),
(12, 9, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-06 15:09:43'),
(13, 11, 1, 'Create a vibrant social media post for a new eco-friendly coffee shop called \"Green Brew Cafe.\" Highlight its sustainable practices, cozy atmosphere, and specialty organic coffee. Include a call-to-action to visit this weekend.', 'user', '2025-05-07 09:32:49');

-- Table structure for `products`
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `product_description` text DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `launch_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

COMMIT;