# Lucid Lang

[![语言版本](https://img.shields.io/badge/language-Lucid_v0.1-blueviolet.svg)](https://github.com/your-username/lucid)
[![构建状态](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-username/lucid/actions)
[![许可证](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

> 一门追求极致清晰与表达力的现代化编程语言。

`Lucid` 是一个全新的编程语言项目，旨在摆脱传统语言的历史包袱，吸收近二十年来的语言设计精华。我们的目标是创造一种语法极简、行为可预测、开发体验一流的语言，让编程回归其简单而强大的本质。

## 设计哲学 (Core Principles)

`Lucid` 的设计遵循以下核心原则，这是我们语言的灵魂：

1.  **一切皆为表达式 (Everything is an Expression)**: `if/else`、代码块等所有结构都返回值，使代码组合性更强，逻辑更连贯。

2.  **简洁至上 (Simplicity First)**: 废除分号，简化不必要的括号。代码即思想，不应被语法噪音所淹没。

3.  **默认不可变 (Immutability by Default)**: 使用 `let` 声明的变量天生不可变，从根本上提高代码的安全性和可预测性。可变性需要通过 `var` 关键字明确声明。

4.  **优雅的管道操作 (`|>`)**: 管道操作符是语言的一等公民，鼓励编写清晰、线性的数据处理流。

5.  **明确的错误处理 (Explicit Error Handling)**: 摒弃隐式的 `try/catch`，采用 `Result<T, E>` 类型，强制开发者正视并处理每一个潜在的错误。

## 当前状态 (Current Status)

**版本: `v0.1` - 架构设计与规划阶段**

项目目前处于初始设计阶段。我们已经确定了语言的核心哲学、技术路线和项目结构。下一步将是实现核心解释器的原型。

## 路线图 (Roadmap)

- [x] **v0.1**: 架构设计与规划
  - [x] 确定核心设计哲学
  - [x] 设计项目目录结构
  - [x] 制定开发路线图
- [ ] **v0.2 (当前目标)**: 核心原型实现
  - [ ] 实现词法分析器 (Lexer) 和语法分析器 (Parser)
  - [ ] 构建基础算术运算和`let`赋值的解释器 (Interpreter)
- [ ] **v0.3**: 现代化核心功能
  - [ ] 实现表达式驱动的 `if/then/else`
  - [ ] 引入 `var` 关键字以支持可变性
- [ ] **v0.4**: 函数与管道
  - [ ] 实现函数定义与调用、闭包
  - [ ] 实现管道操作符 `|>` 的完整功能
- [ ] **v1.0**: 迈向可用
  - [ ] 基础标准库 (字符串处理, 集合操作)
  - [ ] 模块系统

## 目录结构 (Directory Structure)

为了保证项目的清晰、可维护和可扩展性，我们采用以下专业目录结构。每一个文件和目录都有其明确的职责。

```

lucid-lang/
├── .gitignore          \# Git 忽略文件配置，避免提交不必要的文件
├── LICENSE             \# 项目许可证文件 (例如 MIT)，定义他人如何使用你的代码
├── README.md           \# 就是你正在看的这个项目总览文件
├── pyproject.toml      \# (可选) Python 项目配置文件，用于管理依赖和打包
│
├── src/                \# 存放所有核心源代码的根目录
│   └── lucid/          \# 语言核心源代码的主包 (Package)
│       ├── init.py   \# 声明该目录为一个 Python 包
│       ├── main.py   \# REPL (交互式环境) 的入口，使 `python -m lucid` 可运行
│       ├── ast.py        \# 定义抽象语法树 (AST) 的所有节点结构
│       ├── core\_types.py \# 定义核心数据结构，如 Token, Result 等
│       ├── interpreter.py\# 解释器，负责执行 AST
│       ├── lexer.py      \# 词法分析器，将代码字符串转换为令牌 (Token)
│       └── parser.py     \# 语法分析器，将令牌流构建成 AST
│
├── tests/              \# 存放所有测试文件的目录，与源代码分离
│   ├── init.py
│   ├── test\_lexer.py     \# 针对词法分析器的单元测试
│   ├── test\_parser.py    \# 针对语法分析器的单元测试
│   └── test\_interpreter.py \# 针对解释器和完整流程的集成测试
│
├── examples/           \# 存放 Lucid 语言的示例代码，展示语言特性
│   ├── hello\_world.lucid
│   └── fibonacci.lucid
│
└── docs/               \# 存放所有文档的目录
├── spec.md         \# Lucid 语言的官方技术规范 (非常重要！)
└── tutorial.md     \# Lucid 语言的入门教程

```

## 如何开始 (Getting Started)

当项目进入开发阶段后，贡献者和用户可以遵循以下步骤来运行 `Lucid`：

1.  **克隆仓库**: `git clone https://github.com/your-username/lucid-lang.git`
2.  **进入目录**: `cd lucid-lang`
3.  **运行 REPL (交互式环境)**: `python -m src.lucid`
4.  **运行测试**: `pytest tests/` (需要安装 `pytest` 框架)

## 贡献指南 (Contributing)

我们欢迎任何形式的贡献！无论是代码实现、文档编写、还是提出新的想法。请遵循标准的 Fork & Pull Request 流程。所有讨论都应围绕我们的核心设计哲学展开。
