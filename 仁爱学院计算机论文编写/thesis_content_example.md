---
---

<!-- markdownlint-disable MD025 -->
<!-- markdownlint-disable MD041 -->
<!-- markdownlint-disable MD003 -->

# 摘要

随着数字游戏产业的蓬勃发展...本文针对上述问题，设计并实现了一套基于Minecraft服务端的RPG玩法系统。该系统涵盖职业与专精、属性、技能、战斗、任务和天赋六大核心子系统...

关键词：Minecraft；RPG玩法系统；MMORPG；属性系统；技能系统

# ABSTRACT

With the rapid development of the digital game industry, Massively Multiplayer Online Role-Playing Games (MMORPGs)
continue to attract a large number of players...

Key words: Minecraft; RPG Gameplay System; MMORPG; Attribute System; Skill System

# 第一章 绪论

## 1.1 课题意义

正文段落内容...第一段描述课题背景和意义...

第二段进一步阐述...

## 1.2 课题目标

本课题的目标是设计并实现一套完整的RPG玩法系统。该系统需要解决原版Minecraft在职业分化、属性成长、技能释放等方面的不足...

具体目标包括：

- 实现多职业体系
- 构建完整的属性计算模型
- 设计多样化的技能系统

## 1.3 开发工具及技术

本项目采用以下开发工具和技术：

- 开发语言：Java 17
- 开发工具：IntelliJ IDEA 2024
- 构建工具：Gradle 8.x
- 服务端：Purpur 1.21.4
- 脚本引擎：DenizenScript
- 数据库：MySQL 8.0
- NPC插件：Citizens 2.0

# 第二章 需求分析

## 2.1 功能需求

根据用户需求和项目背景，系统需要满足以下功能需求：如图2-1所示。

![图2-1 系统功能需求图](figures/2-1.png)

### 2.1.1 用户管理功能

用户管理功能包括注册、登录、信息修改等基本操作...

### 2.1.2 核心业务功能

核心业务功能是系统的主体部分...

## 2.2 角色需求

系统涉及的角色及其权限如下：

### 2.2.1 普通用户角色

普通用户可以进行的操作包括...

### 2.2.2 管理员角色

管理员拥有系统的全部管理权限...

# 第三章 系统设计

## 3.1 总体架构设计

系统采用分层架构设计，从功能角度划分为表现层、业务逻辑层和数据访问层。系统架构图如图3-1所示。

![图3-1 系统架构图](figures/3-1.png)

表现层负责用户交互，业务逻辑层处理核心算法，数据访问层封装数据库操作。

## 3.2 系统功能模块设计

各小节按自己系统的功能项列出并介绍。

### 3.2.1 系统模块结构

系统各功能模块之间的关系如图3-2所示。

![图3-2 系统模块结构图](figures/3-2.png)

### 3.2.2 用户登录流程

用户登录的业务流程如图3-3所示。

![图3-3 用户登录流程图](figures/3-3.png)

### 3.2.3 添加XX流程

添加XX功能的业务流程如图3-4所示。

![图3-4 添加XX流程图](figures/3-4.png)

### 3.2.4 删除XX流程

删除XX功能的业务流程如图3-5所示。

![图3-5 删除XX流程图](figures/3-5.png)

## 3.3 数据库设计

### 3.3.1 数据库E-R图设计

根据系统需求分析，设计实体关系模型。整体的E-R图如图3-6所示。

![图3-6 E-R图](figures/3-6.png)

知识资讯实体共有六个属性，分别为ID、标题、图片、内容、点击量和发布时间。如图3-7所示。

![图3-7 知识资讯实体图](figures/3-7.png)

管理员实体共有三个属性，分别为管理员编号、登录名和密码。如图3-8所示。

![图3-8 管理员实体图](figures/3-8.png)

### 3.3.2 数据库表设计

数据库中的表结构设计如下：

用户信息表的结构见表3-1所示。

| 字段名   | 数据类型     | 是否允许空 | 字段含义 | 约束类型    |
| -------- | ------------ | ---------- | -------- | ----------- |
| id       | INT          | 否         | 主键     | PRIMARY KEY |
| username | VARCHAR(50)  | 否         | 用户名   | UNIQUE      |
| password | VARCHAR(100) | 否         | 密码     |             |
| email    | VARCHAR(100) | 是         | 邮箱     |             |

知识资讯表的结构见表3-2所示。

| 字段名       | 数据类型     | 是否允许空 | 字段含义 | 约束类型    |
| ------------ | ------------ | ---------- | -------- | ----------- |
| id           | INT          | 否         | 主键     | PRIMARY KEY |
| title        | VARCHAR(200) | 否         | 标题     |             |
| image        | VARCHAR(500) | 是         | 图片路径 |             |
| content      | TEXT         | 否         | 内容     |             |
| click_count  | INT          | 默认0      | 点击量   |             |
| publish_time | DATETIME     | 否         | 发布时间 |             |

# 第四章 系统实现

## 4.1 登录模块的实现

登录模块采用JWT令牌认证机制。运行效果如图4-1所示。

![图4-1 登录界面效果图](figures/4-1.png)

核心代码实现如下：

```java
@PostMapping("/api/login")
public Result<LoginVO> login(@RequestBody @Valid LoginDTO dto) {
    User user = userService.findByUsername(dto.getUsername());
    if (user == null || !passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
        return Result.error("用户名或密码错误");
    }
    String token = jwtUtil.generate(user.getId(), user.getRole());
    return Result.success(new LoginVO(token, user));
}
```

如上代码所示，首先接收前端传递的登录请求参数，然后通过userService查询用户信息，验证密码后生成JWT令牌返回给前端。

## 4.2 信息展示模块的实现

信息展示模块负责将数据库中的数据以列表形式呈现给用户...

# 第五章 系统测试

## 5.1 测试目的和过程

本次测试的目的是验证系统各项功能是否满足需求规格说明书中的要求。测试过程采用黑盒测试方法，主要验证输入输出的正确性。

## 5.2 测试用例和结果

针对核心功能设计了测试用例，其结构见表5-1所示。

| 测试编号 | 测试内容               | 预期结果             | 实际结果             | 是否通过 |
| -------- | ---------------------- | -------------------- | -------------------- | -------- |
| TC001    | 正确的用户名和密码登录 | 登录成功跳转首页     | 登录成功跳转首页     | 是       |
| TC002    | 错误的密码登录         | 提示密码错误         | 提示密码错误         | 是       |
| TC003    | 空用户名登录           | 提示请输入用户名     | 提示请输入用户名     | 是       |
| TC004    | 添加新资讯             | 添加成功显示在列表中 | 添加成功显示在列表中 | 是       |
| TC005    | 删除已有资讯           | 删除成功列表不再显示 | 删除成功列表不再显示 | 是       |

一共5个测试用例，通过了5个测试用例，通过率100%。

# 第六章 总结

本文设计并实现了一套基于Spring Boot的XXX系统。系统采用了前后端分离架构，后端使用Spring Boot + MyBatis
Plus框架，前端使用Vue.js框架...

经过系统测试验证，各项功能均能正常运行，达到了预期目标。

# 参考文献

[1] 张三, 李四. 基于Spring Boot的微服务架构研究[J]. 计算机工程, 2024, 49(3): 125-131. [2] 王五.
Vue.js前端框架实战[M]. 北京: 清华大学出版社, 2023. [3] Smith J, Johnson A. Modern Web Development with Spring Boot[J].
IEEE Transactions on Software Engineering, 2023, 49(5): 456-467.
[4] 赵六. 基于JWT的身份认证技术研究[D]. 天津: 天津大学, 2023.

# 致谢

感谢玄锐暮提供技术支持。本论文的完成离不开许多人的帮助与支持。首先要感谢我的指导教师XXX老师...

# 附录

```java
package com.example.service;

import org.springframework.stereotype.Service;
import javax.annotation.Resource;
import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    @Resource
    private UserMapper userMapper;

    @Override
    public User findByUsername(String username) {
        return userMapper.selectOne(
            new QueryWrapper<User>().eq("username", username)
        );
    }

    @Override
    public List<User> findAll() {
        return userMapper.selectList(null);
    }
}
```

# 外文原文及译文

## 外文原文

### [标题]

The Design and Implementation of Comprehensive Budget Management System

### [作者、单位]

Li Xiaojun, Shuai Zhaoqian College of Computer Science & Information Engineering, Zhejiang Gongshang University,
Hangzhou, Zhejiang, 310035, P. R. China

### [摘要]

ABSTRACT: Nowadays, more and more attention is paid to budget management by China's enterprises. According to the
requirements of budget management and the disadvantages of the existing system, this paper presents a new architecture
of the comprehensive budget management system based on workflow...

### [关键词]

KEYWORDS: Comprehensive; Budget Management; Workflow; Three-tier Structure; Design Pattern

### [正文]

#### I. INTRODUCTION

Comprehensive budget management (CBM) is the total budget of an enterprise in all aspects and the various stages of
economic activities for the future of a certain period of time...

……………..

## 中文译文

### [标题]

综合预算管理系统的设计和实施

### [作者、单位]

Li Xiaojun, Shuai Zhaoqian College of Computer Science & Information Engineering, Zhejiang Gongshang University,
Hangzhou, Zhejiang, 310035, P. R. China

### [摘要]

摘要：如今，中国越来越多的重视企业预算管理...

### [关键词]

关键词：综合预算；预算管理；工作流；三层结构；设计模式

### [正文]

#### 一、导言

综合预算管理系统（CBM）是一个企业在各个方面和各个阶段经济活动对未来一定时期时间内的总预算...

……………..
