---
name: 音乐作曲
description: >
  专业AI音乐作曲与MIDI生成技能。从简单旋律到复杂管弦乐作品，支持多种作曲风格（古典/浪漫/现代电影配乐/电子）。
  内置完整MIDI文件生成能力，使用GM乐器和音乐理论，支持旋律作曲、和声生成、节奏模式和完整MIDI文件创建，包含正确的通道分配、力度和速度。
  触发场景：写歌、作曲、生成BGM、制作游戏音乐、模仿特定作曲家风格、生成MIDI文件、编曲、旋律生成。
  当用户说"作曲"、"交响乐"、"BGM"、"游戏音乐"、"电影配乐"、"写歌"、"编曲"、"管弦乐"、"生成midi"、"MIDI音乐"、"旋律生成"时触发此技能。

---

# 音乐作曲 — 创作理论 + MIDI生成

## 适用场景

当用户请求以下操作时使用此技能：

- 创作音乐、写歌、作曲
- 生成游戏BGM、电影配乐
- 模仿特定作曲家风格
- 编写交响乐、管弦乐
- 生成MIDI文件和配器文档
- 编写旋律、和声、节奏模式
- 将乐谱转换为MIDI格式

## 支持的风格

|风格|代表作曲家|特征|
|---|---|---|
|古典|莫扎特、海顿、贝多芬|平衡乐句、奏鸣曲式、清晰终止式|
|浪漫|肖邦、柴可夫斯基、瓦格纳|表现力动态、半音和声、主导动机|
|现代电影配乐|季默、威廉姆斯、肖尔|固定音型、混合配器、情感弧线|
|电子|克拉夫特维克、范吉利斯|合成器音色、序列模式、氛围铺底|

## 作曲流程

### 第1步：理解需求

- 流派/风格偏好
- 情感弧线（平静→紧张→胜利？）
- 时长目标
- 乐器编制约束
- 使用场景（游戏场景、电影、独立作品）
- 参考曲目（如有）

### 第2步：设计结构

将作品映射到曲式结构：

|曲式|段落|典型时长|
|---|---|---|
|二部曲式|A-B|1-2分钟|
|三部曲式|A-B-A|2-3分钟|
|奏鸣曲式|呈示部-展开部-再现部|5-10分钟|
|回旋曲式|A-B-A-C-A|3-5分钟|
|通谱体|连续发展|不定|

### 第3步：创作核心要素

1. **旋律**：具有清晰轮廓和易记音程的主题
2. **和声**：支撑旋律的和弦进行，符合风格
3. **节奏**：拍号、速度、节奏动机
4. **低音线**：根音运动、行走低音或持续音
5. **对位旋律**：提供深度的第二声部

### 第4步：配器

按照标准配器原则分配乐器：

|声部|乐器|角色|
|---|---|---|
|弦乐|小提琴I/II、中提琴、大提琴、低音提琴|旋律、和声、织体|
|木管|长笛、双簧管、单簧管、大管|音色、对位旋律、独奏|
|铜管|圆号、小号、长号、大号|力量、号角、持续和声|
|打击乐|定音鼓、小军鼓、钹、键盘打击|节奏、强调、氛围|
|键盘|钢琴、管风琴|和声、独奏、通奏低音|

### 第5步：生成MIDI

输出为标准MIDI文件，包含：

- 正确的GM乐器分配
- 适当的力度表现动态
- 速度和拍号元事件
- 每个乐器声部命名的轨道

### 第6步：生成文档

创建配器文档，包含：

- 乐器列表及音域
- 总谱布局描述
- 力度标记
- 演奏说明

## 何时加载参考文件

### 作曲理论参考

|文件|加载时机|
|---|---|
|[references/作曲家风格.md](references/作曲家风格.md)|需要模仿特定作曲家风格、风格模板、配器特点|
|[references/作曲理论.md](references/作曲理论.md)|需要音程/和弦/调性速查、和声进行、曲式结构、旋律写作|
|[references/配器规则.md](references/配器规则.md)|需要乐队编制、音域音色表、配器平衡、特殊效果|

### MIDI技术参考

|文件|加载时机|
|---|---|
|[references/MIDI技术/乐理基础.md](references/MIDI技术/乐理基础.md)|需要MIDI编号换算、基础乐理速查|
|[references/MIDI技术/和弦进行.md](references/MIDI技术/和弦进行.md)|需要和弦进行的MIDI实现细节|
|[references/MIDI技术/声部进行.md](references/MIDI技术/声部进行.md)|需要声部进行规则和MIDI实现|
|[references/MIDI技术/对位法.md](references/MIDI技术/对位法.md)|需要对位法规则和MIDI实现|
|[references/MIDI技术/节奏模式.md](references/MIDI技术/节奏模式.md)|需要节奏模式的MIDI实现|
|[references/MIDI技术/调式与音阶.md](references/MIDI技术/调式与音阶.md)|需要调式音阶的MIDI编号映射|
|[references/MIDI技术/配器法.md](references/MIDI技术/配器法.md)|需要配器法的MIDI实现细节|

## MIDI技术规范

### 技术栈

|库|用途|
|---|---|
|mido|MIDI文件创建和操作|
|Python 3.10+|运行时|

### General MIDI（GM）标准

- 16个通道（通道10 = 打击乐）
- 128种音色（程序变更 0-127）
- 128个控制器（CC0-CC127）
- 键力度：0-127

### 常用GM音色

|音色编号|乐器|类别|
|---|---|---|
|0|大钢琴|钢琴|
|24|尼龙弦吉他|吉他|
|40|小提琴|合奏|
|41|中提琴|合奏|
|42|大提琴|合奏|
|48|弦乐合奏1|合奏|
|56|小号|铜管|
|60|圆号|铜管|
|73|长笛|长笛|
|80|合成主音（方波）|合成主音|

### 打击乐（通道10）

|音符号|声音|
|---|---|
|36|底鼓|
|38|小军鼓|
|42|闭合踩镲|
|46|开放踩镲|
|49|碎音钹|
|51|叮音钹|

### 音名到MIDI编号

|音名|第3八度|第4八度|第5八度|
|---|---|---|---|
|C|48|60|72|
|D|50|62|74|
|E|52|64|76|
|F|53|65|77|
|G|55|67|79|
|A|57|69|81|
|B|59|71|83|

公式：`MIDI编号 = (八度 + 1) * 12 + 半音`，其中C=0、C#=1、D=2...

### 时值换算（Tick）

|时值|Tick数（480 TPB）|
|---|---|
|全音符|1920|
|二分音符|960|
|四分音符|480|
|八分音符|240|
|十六分音符|120|
|附点四分音符|720|
|三连音四分音符|320|

### 代码模式

#### 基础MIDI文件创建

```python
from mido import MidiFile, MidiTrack, Message, MetaMessage

mid = MidiFile(ticks_per_beat=480)
track = MidiTrack()
mid.tracks.append(track)

track.append(MetaMessage('set_tempo', tempo=500000, time=0))
track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

track.append(Message('program_change', program=0, time=0))
track.append(Message('note_on', note=60, velocity=80, time=0))
track.append(Message('note_off', note=60, velocity=0, time=480))

mid.save('output.mid')
```

#### 多轨MIDI

```python
mid = MidiFile(ticks_per_beat=480)

for instrument in instruments:
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message(
        'program_change',
        program=instrument.program,
        channel=instrument.channel,
        time=0
    ))
    for note in instrument.notes:
        track.append(Message(
            'note_on',
            note=note.pitch,
            velocity=note.velocity,
            channel=instrument.channel,
            time=note.start
        ))
        track.append(Message(
            'note_off',
            note=note.pitch,
            velocity=0,
            channel=instrument.channel,
            time=note.duration
        ))
```

## 乐理参考

### 调号

大调：C、G、D、A、E、B、F#、C#、F、Bb、Eb、Ab、Db、Gb、Cb
小调：A、E、B、F#、C#、G#、D#、A#、D、G、C、F、Bb、Eb、Ab

### 常用进行

|风格|进行|示例|
|---|---|---|
|流行|I-V-vi-IV|C-G-Am-F|
|爵士|ii-V-I|Dm7-G7-Cmaj7|
|古典|I-IV-V-I|C-F-G-C|
|电影|i-VI-VII-i|Am-F-G-Am|
|浪漫|I-vi-IV-V|C-Am-F-G|

### 力度标记

|符号|意大利语|含义|
|---|---|---|
|pp|pianissimo|很弱|
|p|piano|弱|
|mp|mezzo-piano|中弱|
|mf|mezzo-forte|中强|
|f|forte|强|
|ff|fortissimo|很强|

## 约束

- MIDI输出必须符合General MIDI（GM）标准
- 所有乐器分配必须使用有效的GM音色编号（1-128）
- 速度范围：40-240 BPM（超出此范围不切实际）
- 最大同时声部：受MIDI规范限制（16通道）
- 游戏BGM：循环应无缝衔接——确保最后一小节连接到第一小节
- 每个MIDI文件最多16个通道（GM限制）
- 力度范围：0-127（0 = 音符关闭）
- 速度单位为微秒/拍（500000 = 120 BPM）
- 所有时间以Tick为单位，相对于前一事件
- 文件必须是有效的MIDI格式0或1
