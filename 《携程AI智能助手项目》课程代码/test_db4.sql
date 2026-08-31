/*
 Navicat Premium Data Transfer

 Source Server         : sdf
 Source Server Type    : MySQL
 Source Server Version : 80021
 Source Host           : localhost:3306
 Source Schema         : test_db4

 Target Server Type    : MySQL
 Target Server Version : 80021
 File Encoding         : 65001

 Date: 03/06/2025 14:15:46
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('d9b6a4596e48');

-- ----------------------------
-- Table structure for t_applicationmodel
-- ----------------------------
DROP TABLE IF EXISTS `t_applicationmodel`;
CREATE TABLE `t_applicationmodel`  (
  `applicant_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '申请人',
  `days` int(0) NOT NULL COMMENT '请假天数',
  `category` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '休假类型',
  `start_date` date NULL DEFAULT NULL COMMENT '请假开始时间',
  `end_date` date NULL DEFAULT NULL COMMENT '请假结束时间',
  `approvers` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '审批人的用户名，多个采用逗号隔开',
  `now_approver` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '当前的审批人',
  `status` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '状态',
  `reasons` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '请假原因',
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_applicationmodel
-- ----------------------------
INSERT INTO `t_applicationmodel` VALUES ('ff', 1, '1', '2024-04-28', '2024-04-29', 'dd,cc,zs', NULL, '4', '1dsfs', 1, '2024-04-28 20:34:06', '2024-04-28 22:42:49');
INSERT INTO `t_applicationmodel` VALUES ('dd', 1, '1', '2024-04-28', '2024-04-29', 'lisi,cc,zs', NULL, '2', '有事情', 3, '2024-04-28 20:38:19', '2024-04-29 17:53:14');
INSERT INTO `t_applicationmodel` VALUES ('dd', 2, '2', '2024-05-02', '2024-05-04', 'lisi,cc,zs', NULL, '4', '感冒了', 4, '2024-04-29 16:13:58', '2024-04-29 17:52:29');
INSERT INTO `t_applicationmodel` VALUES ('dd', 12, '1', '2024-04-26', '2024-05-08', 'lisi,cc,zs', 'lisi', '3', '水电费', 5, '2024-04-29 17:59:23', '2024-04-29 17:59:23');

-- ----------------------------
-- Table structure for t_approverecodemodel
-- ----------------------------
DROP TABLE IF EXISTS `t_approverecodemodel`;
CREATE TABLE `t_approverecodemodel`  (
  `approver_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '审批人的用户名',
  `approve` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '审批意见',
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '审批备注',
  `app_id` int(0) NULL DEFAULT NULL,
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `app_id`(`app_id`) USING BTREE,
  CONSTRAINT `t_approverecodemodel_ibfk_1` FOREIGN KEY (`app_id`) REFERENCES `t_applicationmodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_approverecodemodel
-- ----------------------------
INSERT INTO `t_approverecodemodel` VALUES ('dd', '1', '完全同意', 1, 4, '2024-04-28 22:39:04', '2024-04-28 22:39:04');
INSERT INTO `t_approverecodemodel` VALUES ('cc', '1', 'cc完全同意', 1, 5, '2024-04-28 22:41:08', '2024-04-28 22:41:08');
INSERT INTO `t_approverecodemodel` VALUES ('zs', '1', 'zs完全同意', 1, 6, '2024-04-28 22:42:26', '2024-04-28 22:42:26');
INSERT INTO `t_approverecodemodel` VALUES ('lisi', '1', '我可以同意你的请求！', 4, 7, '2024-04-29 17:49:27', '2024-04-29 17:49:27');
INSERT INTO `t_approverecodemodel` VALUES ('cc', '1', NULL, 4, 8, '2024-04-29 17:51:27', '2024-04-29 17:51:27');
INSERT INTO `t_approverecodemodel` VALUES ('zs', '1', NULL, 4, 9, '2024-04-29 17:52:29', '2024-04-29 17:52:29');
INSERT INTO `t_approverecodemodel` VALUES ('lisi', '2', '我看你不爽', 3, 10, '2024-04-29 17:53:14', '2024-04-29 17:53:14');

-- ----------------------------
-- Table structure for t_deptmodel
-- ----------------------------
DROP TABLE IF EXISTS `t_deptmodel`;
CREATE TABLE `t_deptmodel`  (
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `city` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pid` int(0) NULL DEFAULT NULL,
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  `leader_id` int(0) NULL DEFAULT NULL,
  `leader_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE,
  INDEX `pid`(`pid`) USING BTREE,
  CONSTRAINT `t_deptmodel_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `t_deptmodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_deptmodel
-- ----------------------------
INSERT INTO `t_deptmodel` VALUES ('北京总公司', '北京', NULL, 1, '2024-02-22 17:02:14', '2024-02-22 17:02:16', 3, 'zs');
INSERT INTO `t_deptmodel` VALUES ('行政部', '北京', 1, 2, '2024-02-22 17:02:58', '2024-02-22 17:02:59', 17, 'cc');
INSERT INTO `t_deptmodel` VALUES ('总技术部', '北京', 1, 3, '2024-02-22 17:03:15', '2024-02-22 17:03:16', 14, 'lisi');
INSERT INTO `t_deptmodel` VALUES ('后端开发组', '上海', 3, 4, '2024-02-22 17:04:00', '2024-02-22 17:04:01', 15, 'sunliu');
INSERT INTO `t_deptmodel` VALUES ('Java开发组', '长沙', 3, 6, '2024-04-20 18:20:01', '2024-04-20 18:20:01', 16, 'dd');
INSERT INTO `t_deptmodel` VALUES ('财务部', '的风', 1, 7, '2024-04-28 20:32:48', '2024-04-28 20:32:48', 3, 'zs');

-- ----------------------------
-- Table structure for t_menumodel
-- ----------------------------
DROP TABLE IF EXISTS `t_menumodel`;
CREATE TABLE `t_menumodel`  (
  `number` int(0) NOT NULL COMMENT '排序数字',
  `url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '前端路由访问地址，可以没有',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '菜单显示的名称',
  `is_parent` tinyint(1) NOT NULL COMMENT '是否为顶级菜单',
  `pid` int(0) NULL DEFAULT NULL,
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `pid`(`pid`) USING BTREE,
  CONSTRAINT `t_menumodel_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `t_menumodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_menumodel
-- ----------------------------
INSERT INTO `t_menumodel` VALUES (6, NULL, '系统管理', 1, NULL, 4, '2024-03-20 20:27:47', '2024-03-20 20:27:47');
INSERT INTO `t_menumodel` VALUES (4, '/users', '用户管理', 0, 4, 6, '2024-03-20 20:29:54', '2024-03-20 21:52:17');
INSERT INTO `t_menumodel` VALUES (1, '/men', '菜单管理', 0, 4, 8, '2024-03-20 21:33:57', '2024-03-20 21:52:35');
INSERT INTO `t_menumodel` VALUES (1, '/permissions', '权限管理', 0, 4, 9, '2024-03-20 21:34:23', '2024-03-20 21:34:23');
INSERT INTO `t_menumodel` VALUES (2, NULL, '审批管理', 1, NULL, 10, '2024-03-20 21:45:48', '2024-03-20 21:45:48');
INSERT INTO `t_menumodel` VALUES (1, '/roles', '角色管理', 0, 4, 11, '2024-03-20 21:52:59', '2024-03-20 21:52:59');
INSERT INTO `t_menumodel` VALUES (4, '/depts', '部门管理', 0, 4, 12, '2024-04-20 19:47:50', '2024-04-20 19:47:50');
INSERT INTO `t_menumodel` VALUES (1, '/applications', '我的休假', 0, 10, 14, '2024-04-20 19:50:01', '2024-04-29 11:40:57');
INSERT INTO `t_menumodel` VALUES (1, '/approve', '待我审批', 0, 10, 16, '2024-04-20 19:52:30', '2024-04-29 11:41:22');

-- ----------------------------
-- Table structure for t_permissionmodel
-- ----------------------------
DROP TABLE IF EXISTS `t_permissionmodel`;
CREATE TABLE `t_permissionmodel`  (
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '权限名字',
  `is_interface` tinyint(1) NOT NULL COMMENT '是否为接口',
  `url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '接口访问地址，可以没有',
  `method` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '接口的请求方法，可以没有',
  `menu_id` int(0) NULL DEFAULT NULL,
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  `pid` int(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `menu_id`(`menu_id`) USING BTREE,
  INDEX `pid`(`pid`) USING BTREE,
  CONSTRAINT `t_permissionmodel_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `t_menumodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `t_permissionmodel_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `t_permissionmodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_permissionmodel
-- ----------------------------
INSERT INTO `t_permissionmodel` VALUES ('系统管理', 0, NULL, NULL, 4, 3, '2024-03-20 20:27:47', '2024-03-20 20:27:47', NULL);
INSERT INTO `t_permissionmodel` VALUES ('用户管理', 0, '/users', NULL, 6, 5, '2024-03-20 20:29:54', '2024-03-20 20:29:54', 3);
INSERT INTO `t_permissionmodel` VALUES ('菜单管理', 0, '/menus', NULL, 8, 7, '2024-03-20 21:33:57', '2024-03-20 21:33:57', 3);
INSERT INTO `t_permissionmodel` VALUES ('权限管理', 0, '/permissions', NULL, 9, 8, '2024-03-20 21:34:23', '2024-03-20 21:34:23', 3);
INSERT INTO `t_permissionmodel` VALUES ('审批管理', 0, NULL, NULL, 10, 9, '2024-03-20 21:45:48', '2024-03-20 21:45:48', NULL);
INSERT INTO `t_permissionmodel` VALUES ('角色管理', 0, '/roles', NULL, 11, 10, '2024-03-20 21:52:59', '2024-03-20 21:52:59', 3);
INSERT INTO `t_permissionmodel` VALUES ('查用户列表', 1, '/users', 'GET', 6, 11, '2024-03-22 20:52:43', '2024-03-22 22:09:20', 5);
INSERT INTO `t_permissionmodel` VALUES ('修改用户', 1, '/users', 'PATCH', 6, 14, '2024-03-22 22:24:16', '2024-03-22 22:24:16', 5);
INSERT INTO `t_permissionmodel` VALUES ('添加用户', 1, '/users', 'POST', 6, 15, '2024-03-24 13:25:13', '2024-03-24 13:25:13', 5);
INSERT INTO `t_permissionmodel` VALUES ('批量删除', 1, '/users/delete', 'POST', 6, 16, '2024-03-24 13:25:40', '2024-03-24 13:25:40', 5);
INSERT INTO `t_permissionmodel` VALUES ('添加菜单', 1, '/menus', 'POST', 8, 17, '2024-03-24 13:27:17', '2024-03-24 13:27:17', 7);
INSERT INTO `t_permissionmodel` VALUES ('修改菜单', 1, '/menus', 'PATCH', 8, 18, '2024-03-24 13:27:50', '2024-03-24 13:27:50', 7);
INSERT INTO `t_permissionmodel` VALUES ('权限列表', 1, '/menus', 'GET', 8, 19, '2024-03-24 13:28:15', '2024-03-24 13:28:15', 7);
INSERT INTO `t_permissionmodel` VALUES ('批量删除', 1, '/menus/delete', 'POST', 8, 20, '2024-03-24 13:28:39', '2024-03-24 13:28:39', 7);
INSERT INTO `t_permissionmodel` VALUES ('新增权限', 1, '/permissions', 'POST', 9, 21, '2024-03-24 13:29:02', '2024-03-24 13:29:02', 8);
INSERT INTO `t_permissionmodel` VALUES ('权限列表', 1, '/permissions', 'GET', 9, 22, '2024-03-24 13:29:17', '2024-03-24 13:29:17', 8);
INSERT INTO `t_permissionmodel` VALUES ('修改权限', 1, '/permissions', 'PATCH', 9, 23, '2024-03-24 13:29:46', '2024-03-24 13:29:46', 8);
INSERT INTO `t_permissionmodel` VALUES ('删除权限', 1, '/permissions', 'DELETE', 9, 24, '2024-03-24 13:30:32', '2024-03-24 13:30:32', 8);
INSERT INTO `t_permissionmodel` VALUES ('角色列表', 1, '/roles', 'GET', 11, 25, '2024-03-24 13:30:52', '2024-03-24 13:30:52', 10);
INSERT INTO `t_permissionmodel` VALUES ('部门管理', 0, '/depts', NULL, 12, 26, '2024-04-20 19:47:50', '2024-04-20 19:47:50', 3);
INSERT INTO `t_permissionmodel` VALUES ('查询部门', 1, '/dept', 'GET', 12, 27, '2024-04-20 19:48:17', '2024-04-20 19:48:29', 26);
INSERT INTO `t_permissionmodel` VALUES ('添加部门', 1, '/dept', 'POST', 12, 28, '2024-04-20 19:48:51', '2024-04-20 19:48:51', 26);
INSERT INTO `t_permissionmodel` VALUES ('我的休假', 0, '/applications', NULL, 14, 29, '2024-04-20 19:50:01', '2024-04-20 19:50:01', 9);
INSERT INTO `t_permissionmodel` VALUES ('待我审批', 0, '/approve', NULL, 16, 32, '2024-04-20 19:52:30', '2024-04-20 19:52:30', 9);
INSERT INTO `t_permissionmodel` VALUES ('查询休假列表', 1, '/applications', 'GET', 14, 34, '2024-04-29 11:42:12', '2024-04-29 11:42:12', 29);
INSERT INTO `t_permissionmodel` VALUES ('休假申请', 1, '/applications', 'POST', 14, 35, '2024-04-29 11:42:30', '2024-04-29 11:42:30', 29);
INSERT INTO `t_permissionmodel` VALUES ('休假作废', 1, '/applications', 'PATCH', 14, 36, '2024-04-29 11:42:45', '2024-04-29 11:42:45', 29);
INSERT INTO `t_permissionmodel` VALUES ('我的审批列表', 1, '/approve', 'GET', 16, 37, '2024-04-29 11:43:02', '2024-04-29 11:43:02', 32);

-- ----------------------------
-- Table structure for t_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `t_role_permission`;
CREATE TABLE `t_role_permission`  (
  `permission_id` int(0) NOT NULL,
  `role_id` int(0) NOT NULL,
  PRIMARY KEY (`permission_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id`) USING BTREE,
  CONSTRAINT `t_role_permission_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `t_permissionmodel` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `t_role_permission_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `t_rolemodel` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_role_permission
-- ----------------------------
INSERT INTO `t_role_permission` VALUES (3, 1);
INSERT INTO `t_role_permission` VALUES (5, 1);
INSERT INTO `t_role_permission` VALUES (7, 1);
INSERT INTO `t_role_permission` VALUES (8, 1);
INSERT INTO `t_role_permission` VALUES (9, 1);
INSERT INTO `t_role_permission` VALUES (10, 1);
INSERT INTO `t_role_permission` VALUES (11, 1);
INSERT INTO `t_role_permission` VALUES (14, 1);
INSERT INTO `t_role_permission` VALUES (15, 1);
INSERT INTO `t_role_permission` VALUES (16, 1);
INSERT INTO `t_role_permission` VALUES (17, 1);
INSERT INTO `t_role_permission` VALUES (18, 1);
INSERT INTO `t_role_permission` VALUES (19, 1);
INSERT INTO `t_role_permission` VALUES (20, 1);
INSERT INTO `t_role_permission` VALUES (21, 1);
INSERT INTO `t_role_permission` VALUES (22, 1);
INSERT INTO `t_role_permission` VALUES (23, 1);
INSERT INTO `t_role_permission` VALUES (24, 1);
INSERT INTO `t_role_permission` VALUES (25, 1);
INSERT INTO `t_role_permission` VALUES (26, 1);
INSERT INTO `t_role_permission` VALUES (27, 1);
INSERT INTO `t_role_permission` VALUES (28, 1);
INSERT INTO `t_role_permission` VALUES (29, 1);
INSERT INTO `t_role_permission` VALUES (32, 1);
INSERT INTO `t_role_permission` VALUES (34, 1);
INSERT INTO `t_role_permission` VALUES (35, 1);
INSERT INTO `t_role_permission` VALUES (36, 1);
INSERT INTO `t_role_permission` VALUES (37, 1);
INSERT INTO `t_role_permission` VALUES (3, 2);
INSERT INTO `t_role_permission` VALUES (5, 2);
INSERT INTO `t_role_permission` VALUES (7, 2);
INSERT INTO `t_role_permission` VALUES (8, 2);
INSERT INTO `t_role_permission` VALUES (9, 2);
INSERT INTO `t_role_permission` VALUES (11, 2);
INSERT INTO `t_role_permission` VALUES (14, 2);
INSERT INTO `t_role_permission` VALUES (15, 2);
INSERT INTO `t_role_permission` VALUES (16, 2);
INSERT INTO `t_role_permission` VALUES (17, 2);
INSERT INTO `t_role_permission` VALUES (18, 2);
INSERT INTO `t_role_permission` VALUES (19, 2);
INSERT INTO `t_role_permission` VALUES (20, 2);
INSERT INTO `t_role_permission` VALUES (21, 2);
INSERT INTO `t_role_permission` VALUES (22, 2);
INSERT INTO `t_role_permission` VALUES (23, 2);
INSERT INTO `t_role_permission` VALUES (24, 2);
INSERT INTO `t_role_permission` VALUES (29, 2);
INSERT INTO `t_role_permission` VALUES (32, 2);
INSERT INTO `t_role_permission` VALUES (34, 2);
INSERT INTO `t_role_permission` VALUES (35, 2);
INSERT INTO `t_role_permission` VALUES (36, 2);
INSERT INTO `t_role_permission` VALUES (37, 2);
INSERT INTO `t_role_permission` VALUES (3, 3);
INSERT INTO `t_role_permission` VALUES (5, 3);
INSERT INTO `t_role_permission` VALUES (7, 3);
INSERT INTO `t_role_permission` VALUES (9, 3);
INSERT INTO `t_role_permission` VALUES (11, 3);
INSERT INTO `t_role_permission` VALUES (17, 3);
INSERT INTO `t_role_permission` VALUES (18, 3);
INSERT INTO `t_role_permission` VALUES (19, 3);
INSERT INTO `t_role_permission` VALUES (20, 3);
INSERT INTO `t_role_permission` VALUES (29, 3);
INSERT INTO `t_role_permission` VALUES (34, 3);
INSERT INTO `t_role_permission` VALUES (35, 3);
INSERT INTO `t_role_permission` VALUES (36, 3);

-- ----------------------------
-- Table structure for t_rolemodel
-- ----------------------------
DROP TABLE IF EXISTS `t_rolemodel`;
CREATE TABLE `t_rolemodel`  (
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色的名字',
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色的备注',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_rolemodel
-- ----------------------------
INSERT INTO `t_rolemodel` VALUES ('系统管理员', 1, '2024-02-22 17:01:06', '2024-02-22 17:01:08', '');
INSERT INTO `t_rolemodel` VALUES ('部门经理', 2, '2024-02-22 17:01:49', '2024-02-22 17:01:51', '');
INSERT INTO `t_rolemodel` VALUES ('普通员工', 3, '2024-02-23 17:17:30', '2024-03-24 19:11:13', '一般员工');

-- ----------------------------
-- Table structure for t_user_role
-- ----------------------------
DROP TABLE IF EXISTS `t_user_role`;
CREATE TABLE `t_user_role`  (
  `user_id` int(0) NOT NULL COMMENT '关联xxx表的外键字段',
  `role_id` int(0) NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id`) USING BTREE,
  CONSTRAINT `t_user_role_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `t_rolemodel` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `t_user_role_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `t_usermodel` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_user_role
-- ----------------------------
INSERT INTO `t_user_role` VALUES (3, 1);
INSERT INTO `t_user_role` VALUES (3, 2);
INSERT INTO `t_user_role` VALUES (14, 2);
INSERT INTO `t_user_role` VALUES (15, 2);
INSERT INTO `t_user_role` VALUES (16, 2);
INSERT INTO `t_user_role` VALUES (17, 2);
INSERT INTO `t_user_role` VALUES (3, 3);
INSERT INTO `t_user_role` VALUES (14, 3);
INSERT INTO `t_user_role` VALUES (15, 3);
INSERT INTO `t_user_role` VALUES (16, 3);
INSERT INTO `t_user_role` VALUES (17, 3);
INSERT INTO `t_user_role` VALUES (18, 3);

-- ----------------------------
-- Table structure for t_usermodel
-- ----------------------------
DROP TABLE IF EXISTS `t_usermodel`;
CREATE TABLE `t_usermodel`  (
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的手机号码',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的邮箱地址',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的真实名字',
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的展示头像',
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL COMMENT '记录的创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '记录的最后一次修改时间',
  `dept_id` int(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  INDEX `dept_id`(`dept_id`) USING BTREE,
  FULLTEXT INDEX `xxx`(`username`),
  CONSTRAINT `t_usermodel_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `t_deptmodel` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_usermodel
-- ----------------------------
INSERT INTO `t_usermodel` VALUES ('zs', '$2b$12$QnQ2XQ7ikdH1MfGMNtgpve38ti.rxRKZW7p6Nc8yGHK2HKj4EQW2a', '18788889999', 'gold@126.com', '老肖肖', '/static/user_icon/default.jpg', 3, '2024-01-29 15:44:49', '2024-02-21 11:53:16', 4);
INSERT INTO `t_usermodel` VALUES ('lisi', '$2b$12$QgWj49yUn6kvizWrnEDauOwz5B0fjA09GmnPrFGeA6Tl72fZm0BUi', '19889899900', 'lisi@126.com@126.com', '李四', '/static/user_icon/default.jpg', 14, '2024-03-02 18:17:28', '2024-03-02 19:31:11', 4);
INSERT INTO `t_usermodel` VALUES ('sunliu', '$2b$12$o/IGx4kRnOruHHAho2bySO7Q6FWMi0UDC2Kug2a3Nufbvf99DvoFO', '188999997777', 'sunliu@126.com@126.com@126.com', '孙六', '/static/user_icon/default.jpg', 15, '2024-03-02 19:35:30', '2024-03-02 19:36:45', 4);
INSERT INTO `t_usermodel` VALUES ('dd', '$2b$12$4cEKDpvy9NXxNlCR6xNaKORN4mU3wpoSsjDVN/54xFTKzLNZa/sP2', '19877776666', 'ddd@126.com', NULL, '/static/user_icon/default.jpg', 16, '2024-04-28 20:25:31', '2024-04-28 20:25:31', 6);
INSERT INTO `t_usermodel` VALUES ('cc', '$2b$12$e24TwPvftZRaTwxPYWv3YuUKABctGRbst19qVsgnEJ/wWjx29TJrW', '19877776666', 'cc@126.com', 'cc', '/static/user_icon/default.jpg', 17, '2024-04-28 20:26:48', '2024-04-28 20:26:48', 2);
INSERT INTO `t_usermodel` VALUES ('ff', '$2b$12$QOSD7VZcqr/8NO.PK9Ax3OMPJkMPifq4rC5OpdYRtLIqiq.7SikfS', '19877776666', 'ff@126.com', 'ffff', '/static/user_icon/default.jpg', 18, '2024-04-28 20:27:49', '2024-04-28 20:27:49', 6);

SET FOREIGN_KEY_CHECKS = 1;
