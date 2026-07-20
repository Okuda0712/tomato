-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- ホスト: 127.0.0.1
-- 生成日時: 2025-12-12 07:02:50
-- サーバのバージョン： 10.4.32-MariaDB
-- PHP のバージョン: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- データベース: `farm_management_db`
--

-- --------------------------------------------------------

--
-- テーブルの構造 `alerts`
--

CREATE TABLE `alerts` (
  `id` int(11) NOT NULL,
  `timestamp` datetime NOT NULL,
  `type` varchar(50) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `confidence` decimal(4,1) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `is_pest_disease` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- テーブルのデータのダンプ `alerts`
--

INSERT INTO `alerts` (`id`, `timestamp`, `type`, `location`, `details`, `confidence`, `status`, `attachment_path`, `is_pest_disease`) VALUES
(1, '2025-12-12 06:49:25', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.842, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 274, \"y_max\": 183}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_020310_images (3).jpg', 1),
(2, '2025-12-12 06:49:28', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_020510_image.jpg', 1),
(3, '2025-12-12 06:49:30', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.842, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 274, \"y_max\": 183}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_020610_images (3).jpg', 1),
(4, '2025-12-12 06:49:32', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_020710_image.jpg', 1),
(5, '2025-12-12 06:49:37', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_020910_image.jpg', 1),
(6, '2025-12-12 06:49:39', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.862, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 697, \"y_max\": 524}}', 0.9, 'pending', '/static/alerts/cam_capture_20251211_021010_howto_yasai_tomato_img_01.jpg', 1),
(7, '2025-12-12 06:49:43', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_021210_image.jpg', 1),
(8, '2025-12-12 06:49:45', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.81, \"model_category\": \"disease\", \"box\": {\"x_min\": 6, \"y_min\": 0, \"x_max\": 259, \"y_max\": 192}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_021311_images (2).jpg', 1),
(9, '2025-12-12 06:49:48', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.862, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 697, \"y_max\": 524}}', 0.9, 'pending', '/static/alerts/cam_capture_20251211_021411_howto_yasai_tomato_img_01.jpg', 1),
(10, '2025-12-12 06:49:52', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.842, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 274, \"y_max\": 183}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_021611_images (3).jpg', 1),
(11, '2025-12-12 06:49:54', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.776, \"model_category\": \"disease\", \"box\": {\"x_min\": 5, \"y_min\": 0, \"x_max\": 300, \"y_max\": 167}}', 0.8, 'pending', '/static/alerts/cam_capture_20251211_021711_images (4).jpg', 1),
(12, '2025-12-12 11:19:49', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.776, \"model_category\": \"disease\", \"box\": {\"x_min\": 5, \"y_min\": 0, \"x_max\": 300, \"y_max\": 167}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_111946_images (4).jpg', 1),
(13, '2025-12-12 11:21:49', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.842, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 274, \"y_max\": 183}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112146_images (3).jpg', 1),
(14, '2025-12-12 11:23:49', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112346_image.jpg', 1),
(15, '2025-12-12 11:24:49', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112446_image.jpg', 1),
(16, '2025-12-12 11:25:49', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.776, \"model_category\": \"disease\", \"box\": {\"x_min\": 5, \"y_min\": 0, \"x_max\": 300, \"y_max\": 167}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112546_images (4).jpg', 1),
(17, '2025-12-12 11:27:48', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.862, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 697, \"y_max\": 524}}', 0.9, 'pending', '/static/alerts/cam_capture_20251212_112743_howto_yasai_tomato_img_01.jpg', 1),
(18, '2025-12-12 11:28:46', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.842, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 0, \"x_max\": 274, \"y_max\": 183}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112843_images (3).jpg', 1),
(19, '2025-12-12 11:29:46', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.776, \"model_category\": \"disease\", \"box\": {\"x_min\": 5, \"y_min\": 0, \"x_max\": 300, \"y_max\": 167}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_112943_images (4).jpg', 1),
(20, '2025-12-12 11:50:16', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_115013_image.jpg', 1),
(21, '2025-12-12 11:53:47', 'Tomato Early blight (disease)', 'ハウスA-エリア1', '{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.776, \"model_category\": \"disease\", \"box\": {\"x_min\": 5, \"y_min\": 0, \"x_max\": 300, \"y_max\": 167}}', 0.8, 'pending', '/static/alerts/cam_capture_20251212_115344_images (4).jpg', 1);

-- --------------------------------------------------------

--
-- テーブルの構造 `tickets`
--

CREATE TABLE `tickets` (
  `id` int(11) NOT NULL,
  `category` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `event_timestamp` datetime NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `details` text NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'open',
  `creator_user_id` int(11) DEFAULT NULL,
  `creator_name_display` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- テーブルのデータのダンプ `tickets`
--

INSERT INTO `tickets` (`id`, `category`, `title`, `event_timestamp`, `location`, `details`, `status`, `creator_user_id`, `creator_name_display`, `created_at`) VALUES
(1, 'タバココナジラミ', 'あいうえお', '2025-04-26 10:30:00', 'あいうえお', 'あいうえお', 'open', 1, '山田太郎', '2025-12-05 02:49:59'),
(2, 'Beetles', 'Beetlesの発生について', '2025-12-10 20:28:00', '自動検知エリア', '[AI検知 ID: 29 より起票]\n\n**検知タイプ:** Beetles (pest)\n**確度:** 60%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Beetles (pest)\", \"confidence\": 0.571, \"model_category\": \"pest\", \"box\": {\"x_min\": 327, \"y_min\": 446, \"x_max\": 484, \"y_max\": 693}}', 'open', 1, '山田太郎', '2025-12-10 23:43:38'),
(3, 'Tomato Early blight', '病気の発生について', '2025-12-10 20:28:00', '自動検知エリア', '[AI検知 ID: 28 より起票]\n\n**検知タイプ:** Tomato Early blight (disease)\n**確度:** 80%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 'open', 1, '山田太郎', '2025-12-10 23:46:39'),
(4, 'Tomato Early blight', '病気の発生について', '2025-12-11 01:39:00', 'ハウスA-エリア1', '[AI検知 ID: 74 より起票]\n\n**検知タイプ:** Tomato Early blight (disease)\n**確度:** 80%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 'open', 1, '山田太郎', '2025-12-11 01:40:10'),
(5, 'Tomato Early blight', 'あいうえお', '2025-12-11 22:31:00', 'ハウスA-エリア1', '[AI検知 ID: 872 より起票]\n\n**検知タイプ:** Tomato Early blight (disease)\n**確度:** 60%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.636, \"model_category\": \"disease\", \"box\": {\"x_min\": 116, \"y_min\": 28, \"x_max\": 501, \"y_max\": 395}}', 'open', 1, '山田太郎', '2025-12-11 22:32:10'),
(6, 'Tomato Early blight', 'あいうえお', '2025-12-11 23:30:00', 'ハウスA-エリア1', '[AI検知 ID: 979 より起票]\n\n**検知タイプ:** Tomato Early blight (disease)\n**確度:** 80%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Tomato Early blight (disease)\", \"confidence\": 0.795, \"model_category\": \"disease\", \"box\": {\"x_min\": 0, \"y_min\": 88, \"x_max\": 799, \"y_max\": 717}}', 'open', 1, '山田太郎', '2025-12-11 23:30:42'),
(7, 'Beetles', 'あ', '2025-12-12 00:42:00', 'ハウスA-エリア1', '[AI検知 ID: 1062 より起票]\n\n**検知タイプ:** Beetles (pest)\n**確度:** 70%\n\n--- AIログ詳細は後述 ---\n\n{\"disease\": \"Beetles (pest)\", \"confidence\": 0.678, \"model_category\": \"pest\", \"box\": {\"x_min\": 206, \"y_min\": 21, \"x_max\": 477, \"y_max\": 176}}', 'open', 1, '山田太郎', '2025-12-12 00:42:38');

-- --------------------------------------------------------

--
-- テーブルの構造 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `login_id` varchar(50) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `last_login` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- テーブルのデータのダンプ `users`
--

INSERT INTO `users` (`id`, `login_id`, `display_name`, `password_hash`, `created_at`, `last_login`) VALUES
(1, 'test', 'テスト', '$2b$12$IPcg/LJnfm9li3jVT4j0hOeyrLCrv4/tZWhuhrP1KdrQ/LE1RHrae', '2025-12-12 06:04:01', NULL);

--
-- ダンプしたテーブルのインデックス
--

--
-- テーブルのインデックス `alerts`
--
ALTER TABLE `alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_timestamp` (`timestamp`);

--
-- テーブルのインデックス `tickets`
--
ALTER TABLE `tickets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `creator_user_id` (`creator_user_id`);

--
-- テーブルのインデックス `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login_id` (`login_id`);

--
-- ダンプしたテーブルの AUTO_INCREMENT
--

--
-- テーブルの AUTO_INCREMENT `alerts`
--
ALTER TABLE `alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- テーブルの AUTO_INCREMENT `tickets`
--
ALTER TABLE `tickets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- テーブルの AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `tickets`
--
ALTER TABLE `tickets`
  ADD CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`creator_user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
