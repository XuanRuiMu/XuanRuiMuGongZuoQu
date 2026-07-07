---
name: "资源包制作"
description:
  'Minecraft Java版资源包制作技能。涵盖1.21.4+新版Item
  Model系统和传统CustomModelData系统。触发场景：制作资源包、创建材质包、插件自定义物品纹理、item_model、CustomModelData。当用户说"制作资源包"、"创建材质包"、"自定义物品纹理"、"item_model"、"CustomModelData"、"资源包不生效"、"材质包不显示"时触发此技能。'
---

# Minecraft Java版资源包制作技能

## 核心概念：两套模型系统

Minecraft存在两套为插件物品自定义纹理的系统，选择哪套取决于服务端版本和插件实现方式。

### 系统对比

| 对比项         | 新版Item Model系统（1.21.4+）         | 传统CustomModelData系统（1.21.3-） |
| -------------- | ------------------------------------- | ---------------------------------- |
| 触发方式       | `setItemModel(NamespacedKey)`         | `setCustomModelData(int)`          |
| 客户端组件     | `minecraft:item_model`                | `minecraft:custom_model_data`      |
| 资源包声明位置 | `assets/<命名空间>/items/<路径>.json` | `基物品模型 overrides`             |
| 覆盖范围       | 仅影响指定物品                        | 影响所有同类基物品                 |
| 冲突风险       | 极低（命名空间隔离）                  | 高（不同插件可能使用相同CMD值）    |
| 推荐版本       | 1.21.4+                               | 1.21.3及以下                       |

---

## 第一步：确定使用哪套系统

### 判断逻辑

1. 服务器Minecraft版本 ≥ 1.21.4 → **优先使用Item Model系统**
2. 插件代码中使用 `setItemModel` → **必须使用Item Model系统**
3. 插件代码中使用 `setCustomModelData` → **必须使用CustomModelData系统**
4. 服务器版本 < 1.21.4 → **只能使用CustomModelData系统**

### 禁止混用

- 使用 `setItemModel` 的物品**不能**用CustomModelData资源包覆盖
- 使用 `setCustomModelData` 的物品**不能**用Item Model资源包覆盖
- 同一物品只能选择其中一套系统

---

## 第二步：创建资源包基础结构

### 目录结构

```text
资源包根目录/
├── pack.mcmeta          ← 必需，资源包元数据
├── pack.png             ← 可选，资源包图标（64×64 PNG）
└── assets/              ← 必需，资源目录
    └── <命名空间>/      ← 插件的命名空间（如 mulan）
        ├── items/       ← Item Model系统专用（1.21.4+）
        ├── models/      ← 模型定义
        │   └── item/    ← 物品模型
        └── textures/    ← 纹理图片
            └── item/    ← 物品纹理
```

### pack.mcmeta 格式

#### 基础格式（pack_format < 65）

```json
{
    "pack": {
        "pack_format": <版本号>,
        "description": "资源包描述",
        "supported_formats": [<最低版本>, <最高版本>]
    }
}
```

#### 基础格式（pack_format ≥ 65，即1.21.9+）

```json
{
    "pack": {
        "pack_format": <版本号>,
        "description": "资源包描述"
    }
}
```

**⚠️ 关键变更**：从 pack_format 65 开始，`supported_formats`
字段已被废弃。在 NeoForge 客户端上使用此字段会导致资源包显示为"已损坏或不兼容"甚至崩溃。对于 pack_format ≥
65 的资源包，**只使用 `pack_format` 和 `description` 两个字段**。

#### pack_format 版本对照表

| Minecraft版本    | pack_format | Data Pack格式 |
| ---------------- | ----------- | ------------- |
| 1.21 ~ 1.21.1    | 34          | 48            |
| 1.21.2 ~ 1.21.3  | 42          | 57            |
| 1.21.4           | 46          | 61            |
| 1.21.5           | 55          | 70            |
| 1.21.6 ~ 1.21.7  | 63          | 78            |
| 1.21.8           | 64          | 79            |
| 1.21.9 25w31a    | 65          | 80            |
| 1.21.11          | 75          | 92            |
| 26.1-snapshot-10 | 82          | 99            |
| 26.1 ~ 26.1.2    | 84          | 101           |

**注意**：不确定时必须联网搜索确认最新版本的pack_format值。自65起pack_format使用浮点数存储，但在pack.mcmeta中写整数即可。

#### pack.mcmeta 关键规则

1. `pack_format` 写整数即可（如 `84`），游戏内部会自动处理浮点数版本
2. **pack_format < 65 时**：`supported_formats` 是可选字段，格式为 `[min, max]`
3. **pack_format ≥ 65 时**：`supported_formats` 已废弃，**禁止使用**，否则NeoForge会崩溃或报错
4. **禁止使用** `min_format`、`max_format` 等非标准字段
5. `description` 支持旧版 `§` 颜色码或JSON文本组件

---

## 第三步A：Item Model系统（1.21.4+）

### 工作原理（Item Model）

当插件调用 `setItemModel(new NamespacedKey("mulan", "quest_book"))` 时：

1. 服务端在物品NBT中添加 `minecraft:item_model` 组件，值为 `mulan:quest_book`
2. 客户端收到物品后，查找资源包中 `assets/mulan/items/quest_book.json`
3. 该JSON文件声明模型路径，客户端加载对应模型和纹理

### 文件编写（Item Model）

#### 1. Item声明文件

路径：`assets/<命名空间>/items/<路径>.json`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<命名空间>:item/<模型名>"
  }
}
```

示例：`assets/mulan/items/quest_book.json`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "mulan:item/quest_book"
  }
}
```

#### 2. 模型文件

路径：`assets/<命名空间>/models/item/<模型名>.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "<命名空间>:item/<纹理名>",
    "layer1": "<命名空间>:item/<叠加层纹理名>"
  }
}
```

常用parent值：

- `minecraft:item/generated` — 2D平面物品（食物、书本、工具等）
- `minecraft:item/handheld` — 手持3D物品（剑、镐等）

示例：`assets/mulan/models/item/quest_book.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "mulan:item/quest_book",
    "layer1": "mulan:item/quest_book_overlay"
  }
}
```

#### 3. 纹理文件（Item Model）

路径：`assets/<命名空间>/textures/item/<纹理名>.png`

- 必须是正方形PNG图片（推荐16×16或32×32）
- `layer0` 是主纹理
- `layer1` 是叠加层（通常用于附魔光效等效果）
- 叠加层是可选的

### 插件代码示例（Item Model）

```java
ItemStack 物品 = new ItemStack(Material.ENCHANTED_BOOK);
ItemMeta 元数据 = 物品.getItemMeta();

// 设置Item Model（1.21.4+ API）
元数据.setItemModel(new NamespacedKey("mulan", "quest_book"));

物品.setItemMeta(元数据);
```

### 命名空间对应关系

- `new NamespacedKey("mulan", "quest_book")`
  - Item声明文件：`assets/mulan/items/quest_book.json`
  - 模型查找路径：由 `items/quest_book.json` 中的 `model` 字段指定
- `new NamespacedKey("myplugin", "items/sword")`
  - Item声明文件：`assets/myplugin/items/sword.json`
  - 模型查找路径：由 `items/sword.json` 中的 `model` 字段指定

---

## 第三步B：CustomModelData系统（1.21.3-）

### 工作原理（CustomModelData）

当插件调用 `setCustomModelData(2200001)` 时：

1. 服务端在物品NBT中添加 `minecraft:custom_model_data` 组件，值为 `2200001`
2. 客户端收到物品后，查找基物品（如 `gold_nugget`）的模型文件
3. 模型文件中的 `overrides` 数组根据 `custom_model_data` 值选择对应模型

### 文件编写（CustomModelData）

#### 1. 基物品模型覆盖文件

路径：`assets/minecraft/models/item/<基物品id>.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/<基物品id>"
  },
  "overrides": [
    {
      "predicate": { "custom_model_data": 2200001 },
      "model": "<命名空间>:item/<模型名1>"
    },
    {
      "predicate": { "custom_model_data": 2200002 },
      "model": "<命名空间>:item/<模型名2>"
    }
  ]
}
```

示例：`assets/minecraft/models/item/gold_nugget.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/gold_nugget"
  },
  "overrides": [
    {
      "predicate": { "custom_model_data": 2200001 },
      "model": "slimefun:item/portable_crafter"
    },
    {
      "predicate": { "custom_model_data": 2200002 },
      "model": "slimefun:item/fortune_cookie"
    }
  ]
}
```

#### 2. 自定义模型文件

路径：`assets/<命名空间>/models/item/<模型名>.json`

格式与Item Model系统的模型文件相同。

#### 3. 纹理文件（CustomModelData）

与Item Model系统相同。

### CustomModelData分配规则

- 每个插件应使用独立的ID范围，避免冲突
- 推荐范围分配示例：

| 插件/附加 | CMD范围           |
| --------- | ----------------- |
| 主插件    | 2200001 - 2200600 |
| 附加1     | 2200601 - 2200679 |
| 附加2     | 2200800 - 2200809 |

### 插件代码示例

```java
ItemStack 物品 = new ItemStack(Material.GOLD_NUGGET);
ItemMeta 元数据 = 物品.getItemMeta();

// 设置CustomModelData
元数据.setCustomModelData(2200001);

物品.setItemMeta(元数据);
```

---

## 第四步：验证与调试

### 资源包不生效排查清单

按以下顺序逐一检查：

#### 1. 资源包是否被客户端加载

- 在游戏内按 `Esc` → `选项` → `资源包`，确认资源包已启用且在正确位置
- 检查资源包是否显示红色×（格式错误），如有则 `pack.mcmeta` 有问题
- 检查 `pack_format` 是否匹配当前Minecraft版本

#### 2. item_model组件是否在物品上

- **这是最常见的失败原因**
- 使用 `/item` 命令检查物品组件：`/item modify @s weapon.mainhand` 或使用调试棒
- 如果物品缺少 `minecraft:item_model` 组件，客户端不会查找自定义模型
- **解决方法**：重新创建物品（丢弃旧物品，让插件重新发放）

#### 3. 文件路径是否正确

- Item Model系统：`setItemModel(new NamespacedKey("mulan", "quest_book"))` → `assets/mulan/items/quest_book.json`
- CustomModelData系统：基物品 `GOLD_NUGGET` → `assets/minecraft/models/item/gold_nugget.json`
- 模型文件中的纹理路径：`mulan:item/quest_book` → `assets/mulan/textures/item/quest_book.png`
- **所有路径区分大小写**

#### 4. JSON语法是否正确

- 使用JSON验证器检查所有JSON文件
- 常见错误：多余逗号、缺少引号、注释（JSON不支持注释）

#### 5. 纹理文件是否有效

- 必须是PNG格式
- 推荐正方形尺寸（16×16、32×32、64×64）
- 文件不能为0字节

### 快速测试命令

在游戏中使用以下命令直接测试Item Model系统是否工作：

```text
/give @p minecraft:enchanted_book[item_model="mulan:quest_book"]
```

如果此命令给出的物品显示了自定义纹理，说明资源包正确；如果仍然显示附魔书，说明资源包文件有问题。

---

## 第五步：部署资源包

### 方式A：客户端本地加载

1. 将资源包目录压缩为zip文件
2. **zip内部顶层必须是 `pack.mcmeta` 和 `assets/`**，不能多一层目录嵌套
3. 将zip放入客户端 `.minecraft/resourcepacks/` 目录
4. 在游戏内启用资源包

### 方式B：服务器推送

1. 将资源包zip上传到Web服务器（如GitHub Releases、自建HTTP服务器）
2. 在 `server.properties` 中配置：

   ```properties
   resource-pack=https://example.com/资源包.zip
   resource-pack-sha1=<SHA1哈希值>
   ```

3. 计算SHA1：`certutil -hashfile 资源包.zip SHA1`
4. 设置 `require-resource-pack=true` 可强制玩家使用资源包

### 压缩命令

```powershell
Compress-Archive -Path "源目录\*" -DestinationPath "输出.zip" -Force
```

**关键**：使用 `源目录\*` 而非 `源目录`，确保zip顶层是 `pack.mcmeta` 和 `assets/`。

---

## 常见陷阱与注意事项

### 🔴 致命错误

1. **pack_format使用浮点数** — 必须是整数，`84.0` 会导致某些版本无法识别
2. **zip嵌套目录** — zip内顶层必须是 `pack.mcmeta`，不能是 `资源包名/pack.mcmeta`
3. **物品缺少item_model组件** — 旧物品不会自动获得新组件，必须重新创建
4. **路径大小写错误** — Minecraft资源路径严格区分大小写

### 🟡 常见问题

1. **多个资源包冲突** — 优先级高的资源包会覆盖低优先级的同名文件
2. **CustomModelData冲突** — 不同插件使用相同CMD值会导致纹理错乱
3. **纹理分辨率不一致** — 同一模型的不同layer应使用相同分辨率
4. **NeoForge/Forge客户端** — Mod加载器可能影响资源包加载顺序

### 🟢 最佳实践

1. **使用独立命名空间** — 每个插件使用自己的命名空间（如 `mulan`、`slimefun`）
2. **版本号写入description** — 方便追踪资源包版本
3. **保留原始基物品纹理** — CustomModelData系统的overrides文件必须包含基物品的默认纹理
4. **测试时使用give命令** — 先用命令验证资源包，再通过插件发放
5. **热重载验证** — 使用 `F3+T` 在游戏内刷新资源包，无需重启客户端

---

## 参考资源

- [Minecraft Wiki - Resource Pack](https://minecraft.wiki/w/Resource_pack)
- [Minecraft Wiki - Item Model (1.21.4+)](https://minecraft.wiki/w/Item_model)
- [Minecraft Wiki - Model](https://minecraft.wiki/w/Model)
- [Slimefun Resource Pack](https://github.com/xMikux/Slimefun-Resourcepack) — CustomModelData系统参考实现
