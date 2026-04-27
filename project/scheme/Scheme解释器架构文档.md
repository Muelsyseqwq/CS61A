# Scheme 解释器架构文档

> 本文档详细描述了 CS61A Scheme 解释器的完整实现逻辑，从输入一条语句到输出结果的全部流程，以及所有定义的类和方法的说明。

---

## 一、整体架构概览

本解释器用 Python 实现了一个 **Scheme 语言的解释器**，采用经典的 **Read-Eval-Print Loop (REPL)** 架构。核心模块及其职责如下：

| 模块文件 | 职责 |
|---------|------|
| `scheme.py` | 主入口，REPL 循环 |
| `scheme_tokens.py` | 词法分析（Lexing）：字符串 → Token 列表 |
| `buffer.py` | 缓冲区管理：统一多行 Token 流的逐个访问接口 |
| `scheme_reader.py` | 语法解析（Parsing）：Token 流 → Link 链表（AST） |
| `link.py` | 链表数据结构：Scheme 列表的底层表示 |
| `scheme_classes.py` | 核心类定义：环境帧、过程类 |
| `scheme_eval_apply.py` | 求值引擎（Eval/Apply）：递归求值 AST |
| `scheme_forms.py` | 特殊形式处理：define、if、lambda、and、or 等 |
| `scheme_builtins.py` | 内置过程：+、-、*、/、cons、car、cdr 等 |
| `scheme_utils.py` | 工具函数：类型检查、参数验证 |
| `schememon.py` | Web GUI 求值器 |

---

## 二、从输入到输出的完整流程

输入一条 Scheme 语句（如 `(+ 1 2)`），经历以下 **5 个阶段**：

```
用户输入 " (+ 1 2) "
    │
    ▼
[1. 词法分析] scheme_tokens.py
    字符串 → Token 列表: ['(', '+', 1, 2, ')']
    │
    ▼
[2. 缓冲管理] buffer.py
    Token 列表 → Buffer 对象（支持逐个 pop/peek）
    │
    ▼
[3. 语法解析] scheme_reader.py
    Token 流 → Link 链表 (AST): Link('+', Link(1, Link(2)))
    │
    ▼
[4. 求值] scheme_eval_apply.py + scheme_forms.py
    递归求值 AST → 结果值: 3
    │
    ▼
[5. 输出] scheme.py REPL
    repl_str(3) → 打印 "3"
```

### 2.1 阶段一：词法分析（Lexing）

**入口**：`scheme_tokens.tokenize_line(line)` 或 `tokenize_lines(inp)`

将一行字符串拆分为 Token 列表。Token 类型包括：

- **数字**：`int` 或 `float`（如 `42`, `3.14`）
- **布尔**：`True` / `False`（对应 Scheme 的 `#t` / `#f`）
- **符号**：`str`（如 `+`, `define`, `x`，全部转为小写）
- **分隔符**：`(`, `)`, `'`, `` ` ``, `.`, `,`, `,@`
- **字符串**：以 `"` 包裹的 `str`（如 `"hello"`）

**核心流程**：

1. `next_candidate_token(line, k)` 从位置 k 开始扫描，跳过空白和注释（`;` 开头），识别下一个候选 Token
2. `tokenize_line(line)` 反复调用 `next_candidate_token`，对候选 Token 进行分类验证：
   - 分隔符直接加入
   - `#t`/`true` → `True`，`#f`/`false` → `False`
   - `nil` → 字符串 `"nil"`
   - 数字开头 → 尝试 `int()` → 尝试 `float()` → 否则当符号
   - 符号 → 验证合法性后转小写加入
   - 字串 → 直接加入
3. `tokenize_lines(inp)` 是生成器版本，对输入的每一行调用 `tokenize_line`

**示例**：

```python
tokenize_line('(+ 1 2)')  # → ['(', '+', 1, 2, ')']
tokenize_line('(define x #t)')  # → ['(', 'define', 'x', True, ')']
```

### 2.2 阶段二：缓冲管理（Buffering）

**入口**：`buffer_input()` 或 `buffer_lines(lines)`

`Buffer` 类将多行 Token 流统一为逐个访问的接口，供语法解析器使用。

**构造流程**：

```
用户输入/文件行 → InputReader/LineReader (迭代器)
    → tokenize_lines() (每行生成 token 列表)
    → Buffer(迭代器) (统一逐个访问)
```

- **交互模式**：`buffer_input()` → `Buffer(tokenize_lines(InputReader('scm> ')))`
  - `InputReader` 每次调用 `input()` 获取一行
- **文件模式**：`buffer_lines(lines)` → `Buffer(tokenize_lines(LineReader(lines)))`
  - `LineReader` 逐行弹出文件内容

### 2.3 阶段三：语法解析（Parsing）

**入口**：`scheme_read(src)`

将 Token 流解析为 `Link` 链表结构，即 Scheme 的 S-表达式（也是 AST）。

**核心函数**：

- `scheme_read(src)`：读取下一个表达式
  - 遇到原子（数字/布尔/符号）→ 直接返回
  - 遇到 `nil` → 返回 `nil`（空链表）
  - 遇到 `(` → 调用 `read_tail(src)` 读取列表
  - 遇到引号标记（`'`, `` ` ``, `,`, `,@`）→ 转换为 `(quote expr)` 等形式
  - 遇到其他分隔符 → 抛语法错误

- `read_tail(src)`：读取列表的剩余部分（递归）
  - 遇到 `)` → 返回 `nil`（列表结束）
  - 否则 → `first = scheme_read(src)`, `rest = read_tail(src)`, 返回 `Link(first, rest)`

**示例**：

```python
# 输入: (+ 1 2)
# Token 流: '(', '+', 1, 2, ')'
# 解析结果:
# Link('+', Link(1, Link(2, nil)))
# 即 Scheme 列表 (+ 1 2)

# 输入: (define (f x) (+ x 2))
# 解析结果:
# Link('define', Link(Link('f', Link('x', nil)), Link(Link('+', Link('x', Link(2, nil))), nil)))
```

**嵌套列表的解析过程**（以 `(define x (+ 1 2))` 为例）：

1. `scheme_read` 读到 `(` → 调用 `read_tail`
2. `read_tail` 中 `first = scheme_read(src)` → 读到 `define`（符号）
3. `read_tail` 递归 → `first = scheme_read(src)` → 读到 `x`（符号）
4. `read_tail` 递归 → `first = scheme_read(src)` → 读到 `(` → 再次进入 `scheme_read` → 调用 `read_tail`
   - 内层 `read_tail` 读到 `+`, `1`, `2`, `)` → 返回 `Link('+', Link(1, Link(2)))`
5. 外层 `read_tail` 继续读到 `)` → 返回 `nil`
6. 最终结果：`Link('define', Link('x', Link(Link('+', Link(1, Link(2))), nil)))`

### 2.4 阶段四：求值（Evaluation）

**入口**：`scheme_eval(expr, env)`

这是解释器的核心，采用递归求值策略。

#### `scheme_eval` 的求值逻辑

```python
def scheme_eval(expr, env):
    # 1. 原子表达式
    if scheme_symbolp(expr):       # 符号 → 在环境中查找绑定值
        return env.lookup(expr)
    elif self_evaluating(expr):    # 自求值（数字/布尔/nil/None）→ 直接返回
        return expr

    # 2. 列表表达式（组合式）
    first, rest = expr.first, expr.rest

    # 2a. 特殊形式
    if scheme_symbolp(first) and first in SPECIAL_FORMS:
        return SPECIAL_FORMS[first](rest, env)

    # 2b. 过程调用
    else:
        procedure = scheme_eval(first, env)          # 求值操作符
        args = map_link(lambda x: scheme_eval(x, env), rest)  # 求值所有参数
        return scheme_apply(procedure, args, env)    # 应用过程
```

#### `scheme_apply` 的应用逻辑

根据过程类型分三种情况：

1. **BuiltinProcedure**（内置过程）：
   - 将 Link 参数列表转为 Python 列表
   - 如果 `need_env=True`，追加 `env` 到参数列表末尾
   - 调用 `procedure.py_func(*l)`

2. **LambdaProcedure**（词法作用域用户过程）：
   - 在 **定义时的环境** (`procedure.env`) 上创建子帧，绑定形参和实参
   - 用 `eval_all` 依次求值函数体中的所有表达式，返回最后一个的值

3. **MuProcedure**（动态作用域用户过程）：
   - 在 **调用时的环境** (`env`) 上创建子帧，绑定形参和实参
   - 求值函数体

#### 特殊形式求值

特殊形式不遵循"先求值所有参数"的规则，由 `SPECIAL_FORMS` 字典分发：

| 特殊形式 | 处理函数 | 行为 |
|---------|---------|------|
| `define` | `do_define_form` | 定义变量绑定或命名过程 |
| `quote` | `do_quote_form` | 不求值，直接返回表达式本身 |
| `lambda` | `do_lambda_form` | 创建 LambdaProcedure 对象（不立即求值函数体） |
| `if` | `do_if_form` | 条件分支：求值条件，选择分支求值 |
| `and` | `do_and_form` | 短路求值：遇 `#f` 立即返回，否则返回最后一个值 |
| `or` | `do_or_form` | 短路求值：遇非 `#f` 立即返回，否则返回 `#f` |
| `begin` | `do_begin_form` | 顺序求值所有表达式，返回最后一个 |
| `cond` | `do_cond_form` | 多路条件分支 |
| `let` | `do_let_form` | 局部绑定：创建子帧求值 |
| `mu` | `do_mu_form` | 创建 MuProcedure 对象（动态作用域） |
| `quasiquote` | `do_quasiquote_form` | 准引用：允许部分求值 |
| `unquote` | `do_unquote` | 反引用（仅在 quasiquote 内有效，否则报错） |

### 2.5 阶段五：输出（Printing）

在 REPL 循环中：

```python
result = scheme_eval(expression, env)
if not quiet and result is not None:
    print(repl_str(result))
```

`repl_str(val)` 将 Scheme 值转为显示字符串：
- `True` → `#t`
- `False` → `#f`
- `None` → `undefined`
- 字符串 → 带引号显示
- 其他 → `str(val)`（Link 的 `__str__` 会输出 Scheme 列表格式如 `(1 2 3)`）

---

## 三、完整示例追踪

以 `(define (square x) (* x x))` 然后 `(square 5)` 为例：

### 步骤 1：词法分析

```
"(define (square x) (* x x))" → ['(', 'define', '(', 'square', 'x', ')', '(', '*', 'x', 'x', ')', ')']
"(square 5)"                  → ['(', 'square', 5, ')']
```

### 步骤 2：语法解析

```
第一行 → Link('define',
           Link(Link('square', Link('x', nil)),
             Link(Link('*', Link('x', Link('x', nil))),
               nil)))

第二行 → Link('square', Link(5, nil))
```

### 步骤 3：求值 `(define (square x) (* x x))`

1. `scheme_eval` 发现 `first='define'` 是特殊形式
2. 调用 `do_define_form(rest, env)`
3. `signature = Link('square', Link('x', nil))`，是 Link 且 `signature.first='square'` 是符号
4. 进入"定义命名过程"分支：
   - `body = expressions.rest` = `Link(Link('*', Link('x', Link('x', nil))), nil)`
   - `formals = signature.rest` = `Link('x', nil)`
   - 创建 `LambdaProcedure(Link('x', nil), body, env)`
   - `env.define('square', LambdaProcedure对象)`
5. 返回 `'square'`

### 步骤 4：求值 `(square 5)`

1. `scheme_eval` 发现 `first='square'` 不是特殊形式
2. 求值操作符：`scheme_eval('square', env)` → 找到 `LambdaProcedure` 对象
3. 求值参数：`map_link(lambda x: scheme_eval(x, env), Link(5, nil))` → `Link(5, nil)`
4. `scheme_apply(LambdaProcedure, Link(5, nil), env)`：
   - `procedure.env.make_child_frame(Link('x', nil), Link(5, nil))` → 创建子帧 `{x: 5}`
   - `eval_all(body, child)` → 求值 `(* x x)`
     - `scheme_eval(Link('*', Link('x', Link('x', nil))), child)`
     - 求值 `*` → 内置乘法过程
     - 求值 `x` → 5, 求值 `x` → 5
     - `scheme_apply(BuiltinProcedure(*), Link(5, Link(5, nil)), child)` → `5 * 5 = 25`
5. 返回 `25`

### 步骤 5：输出

```
repl_str(25) → "25" → 打印 25
```

---

## 四、所有类及方法详解

### 4.1 `Link` — 链表（Scheme 列表的底层表示）

**文件**：`link.py`

Scheme 中一切列表结构都用 `Link` 表示，它是本解释器最核心的数据结构。

| 方法/属性 | 签名 | 作用 |
|----------|------|------|
| `Link.empty` | 类属性 | 空链表哨兵值，等于 `()`，即 `nil` |
| `__init__` | `(self, first, rest=empty)` | 创建链表节点，`first` 存储当前元素，`rest` 指向剩余链表 |
| `__repr__` | `(self)` | 返回 Python 风格表示，如 `Link(1, Link(2))`；空 rest 省略 |
| `__str__` | `(self)` | 返回 Scheme 风格表示，如 `(1 2)`；非标准尾用点对表示如 `(1 . 2)` |
| `__eq__` | `(self, other)` | 结构性相等判断：类型相同且 `first` 和 `rest` 都相等 |

**模块级函数**：

| 函数 | 签名 | 作用 |
|------|------|------|
| `repl_str` | `(val)` | 将 Scheme 值转为 REPL 显示字符串：`True→"#t"`, `False→"#f"`, `None→"undefined"`, 字符串带引号，其他用 `str()` |
| `len_link` | `(s)` | 计算链表长度，遍历计数 |
| `map_link` | `(f, s)` | 对链表每个元素映射函数 `f`，返回新链表（递归实现） |

---

### 4.2 `Buffer` — Token 缓冲区

**文件**：`buffer.py`

将多行 Token 流统一为逐个访问的接口，供 `scheme_read` 使用。

| 方法 | 签名 | 作用 |
|------|------|------|
| `__init__` | `(self, source)` | 初始化缓冲区，`source` 是迭代器（每次 `next()` 返回一行 token 列表）。初始化时调用 `current()` 预加载第一行 |
| `pop_first` | `(self)` | 弹出并返回当前 token，指针后移一位。若已耗尽返回 `None` |
| `current` | `(self)` | 返回当前 token（不移动指针）。若当前行耗尽，自动从 `source` 拉取下一行；若 `source` 也耗尽，返回 `None` |
| `more_on_line` | `(self)` | 当前行是否还有未消费的 token（`index < len(current_line)`） |
| `end_of_line` | `(self)` | 是否已到全部数据的末尾（`current() is None`） |

---

### 4.3 `InputReader` — 交互式输入迭代器

**文件**：`buffer.py`

| 方法 | 签名 | 作用 |
|------|------|------|
| `__init__` | `(self, prompt)` | 设置 REPL 提示符（如 `'scm> '`） |
| `__iter__` | `(self)` | 无限循环 `yield input(prompt)`，首次后提示符变为空格占位 |

---

### 4.4 `LineReader` — 文件行迭代器

**文件**：`buffer.py`

| 方法 | 签名 | 作用 |
|------|------|------|
| `__init__` | `(self, lines, prompt, comment=";")` | 接收行列表、提示符、注释符号 |
| `__iter__` | `(self)` | 逐行 `yield`，打印非空非注释行（带提示符），读完后抛 `EOFError` |

---

### 4.5 `SchemeError` — Scheme 错误异常

**文件**：`scheme_classes.py`

继承 `Exception`，用于所有 Scheme 运行时错误和语法错误的统一异常类型。

---

### 4.6 `Frame` — 环境帧（变量绑定的核心）

**文件**：`scheme_classes.py`

环境帧实现了 Scheme 的词法作用域。多个 Frame 通过 `parent` 链形成环境链。

| 方法 | 签名 | 作用 |
|------|------|------|
| `__init__` | `(self, parent)` | 创建空帧，`bindings` 为空字典，`parent` 指向父帧（全局帧的 parent 为 `None`） |
| `__repr__` | `(self)` | 显示帧内容。全局帧显示 `<Global Frame>`，其他帧显示 `<{绑定} -> 父帧>` |
| `define` | `(self, symbol, value)` | 在当前帧中绑定 `symbol → value`（直接写入 `self.bindings` 字典） |
| `lookup` | `(self, symbol)` | 查找符号值：先查当前帧的 `bindings`，找不到则沿 `parent` 链逐帧向上查找，全部找不到抛 `SchemeError('unknown identifier')` |
| `make_child_frame` | `(self, formals, vals)` | 创建子帧：将形参 Link 列表与实参 Link 列表一一绑定到新帧，新帧的 `parent` 为 `self`。参数数量不匹配则抛错 |

**环境链示意**：

```
Global Frame: {x: 1, +: BuiltinProcedure, ...}
    │
    ├── Child Frame (f 被调用时): {a: 3, b: 4} → parent → Global Frame
    │       │
    │       └── Child Frame (g 被调用时): {c: 5} → parent → Child Frame
    │
    └── Child Frame (h 被调用时): {y: 2} → parent → Global Frame
```

---

### 4.7 `Procedure` — 过程基类

**文件**：`scheme_classes.py`

空基类，仅用于 `isinstance(x, Procedure)` 类型判断，区分"是否为可调用过程"。

---

### 4.8 `BuiltinProcedure` — 内置过程

**文件**：`scheme_classes.py`

封装 Python 函数为 Scheme 可调用的内置过程。

| 方法/属性 | 签名 | 作用 |
|----------|------|------|
| `__init__` | `(self, py_func, need_env=False, name='builtin')` | `py_func` 是对应的 Python 函数；`need_env` 为 `True` 时，`scheme_apply` 会将当前环境 `env` 追加到参数列表末尾再调用；`name` 是 Scheme 中的显示名称 |
| `__str__` | `(self)` | 返回 `#[name]` 格式，如 `#[+]`, `#[cons]` |

---

### 4.9 `LambdaProcedure` — 用户定义过程（词法作用域）

**文件**：`scheme_classes.py`

由 `(lambda ...)` 或 `(define (f ...) ...)` 创建，**捕获定义时的环境**形成闭包。

| 方法/属性 | 签名 | 作用 |
|----------|------|------|
| `__init__` | `(self, formals, body, env)` | `formals`：形参列表（Link，如 `Link('x', nil)`）；`body`：函数体（Link，可包含多条表达式，如 `Link(Link('+', ...), nil)`）；`env`：定义时的环境帧（闭包捕获） |
| `__str__` | `(self)` | 返回 `(lambda (formals) body)` 格式 |
| `__repr__` | `(self)` | 返回 `LambdaProcedure(formals, body, env)` 格式 |

**调用时**：在 `procedure.env`（定义时环境）上创建子帧，绑定形参实参，用 `eval_all` 求值函数体。

---

### 4.10 `MuProcedure` — 动态作用域过程

**文件**：`scheme_classes.py`

由 `(mu ...)` 创建，**不捕获环境**，调用时在调用点环境中求值。

| 方法/属性 | 签名 | 作用 |
|----------|------|------|
| `__init__` | `(self, formals, body)` | `formals`：形参列表（Link）；`body`：函数体（单个 Scheme 表达式，Link） |
| `__str__` | `(self)` | 返回 `(mu (formals) body)` 格式 |
| `__repr__` | `(self)` | 返回 `MuProcedure(formals, body)` 格式 |

**调用时**：在 `env`（调用时环境）上创建子帧，绑定形参实参，用 `scheme_eval` 求值函数体。

**Lambda vs Mu 的区别**：

```
(define (f x) (mu (y) (+ x y)))  ; f 内部定义了 mu 过程

(f 3)  ; 调用 f，x=3 在 f 的帧中
       ; 返回 MuProcedure

; 假设全局有 (define z 10)
; 调用 mu 过程时：
;   Lambda: 会在 f 的帧中查找 x → 找到 x=3
;   Mu:     会在调用时的帧中查找 x → 取决于调用点环境
```

---

### 4.11 `Unevaluated` — 尾调用优化辅助类

**文件**：`scheme_eval_apply.py`

| 方法/属性 | 签名 | 作用 |
|----------|------|------|
| `__init__` | `(self, expr, env)` | 包装一个待求值的表达式和环境，用于尾调用优化 |

尾调用优化的核心思想：当表达式处于尾位置时，不立即递归求值，而是返回 `Unevaluated` 对象，由外层循环统一求值，从而避免栈帧增长。当前代码中 `optimize_tail_calls` 函数体未实现（标记为 `OPTIONAL PROBLEM`）。

---

### 4.12 `SchemeEvaluator` — Web GUI 求值器

**文件**：`schememon.py`

为 Web 界面（schememon）提供 Scheme 代码求值能力。

| 方法 | 签名 | 作用 |
|------|------|------|
| `__init__` | `(self)` | 创建全局环境帧 `self.env = create_global_frame()` |
| `evaluate` | `(self, filenames, code)` | 先加载 `filenames` 中的 .scm 文件内容，拼接 `code`，逐行 tokenize → parse → eval，返回所有结果的列表 |

---

## 五、核心函数详解

### 5.1 词法分析函数（`scheme_tokens.py`）

| 函数 | 作用 |
|------|------|
| `valid_symbol(s)` | 检查字符串 `s` 是否为合法 Scheme 符号（所有字符都在 `_SYMBOL_CHARS` 中） |
| `next_candidate_token(line, k)` | 从位置 k 扫描行，返回下一个候选 Token 及其结束位置。跳过空白和注释，识别单字符 Token、布尔 `#t`/`#f`、字符串字面量、逗号相关 Token、多字符符号/数字 |
| `tokenize_line(line)` | 将一行字符串转为 Token 列表。反复调用 `next_candidate_token`，对候选 Token 分类（分隔符/布尔/数字/符号/字符串） |
| `tokenize_lines(inp)` | 生成器版本，对输入的每一行调用 `tokenize_line` |
| `check_token_length_warning(token, length)` | Token 长度超过 50 时发出警告 |
| `chain(*iters)` | 连接多个迭代器 |

### 5.2 语法解析函数（`scheme_reader.py`）

| 函数 | 作用 |
|------|------|
| `scheme_read(src)` | 从 Buffer 中读取下一个 Scheme 表达式，返回原子值或 Link 链表 |
| `read_tail(src)` | 递归读取列表剩余部分，构建 Link 链表。读到 `)` 返回 nil，否则 `Link(scheme_read(src), read_tail(src))` |
| `buffer_input(prompt)` | 创建交互式 Buffer（用于 REPL） |
| `buffer_lines(lines, prompt, show_prompt)` | 创建文件行 Buffer（用于加载文件） |
| `read_line(line)` | 将单个字符串解析为 Scheme 表达式（用于测试和内部调用） |

### 5.3 求值函数（`scheme_eval_apply.py`）

| 函数 | 作用 |
|------|------|
| `scheme_eval(expr, env)` | 核心求值函数。原子：符号查环境，自求值直接返回；列表：特殊形式走特殊路径，否则求值操作符和参数后 `scheme_apply` |
| `scheme_apply(procedure, args, env)` | 核心应用函数。按过程类型分发：Builtin → 转 Python 列表调用；Lambda → 定义时环境创建子帧 + eval_all；Mu → 调用时环境创建子帧 + scheme_eval |
| `eval_all(expressions, env)` | 顺序求值链表中的所有表达式，返回最后一个的值。空列表返回 `None` |
| `complete_apply(procedure, args, env)` | 应用过程并确保结果不是 `Unevaluated`（如果是则继续求值），用于尾调用优化场景 |
| `optimize_tail_calls(unoptimized_scheme_eval)` | 尾调用优化装饰器（未实现），返回优化后的 eval 函数 |

### 5.4 特殊形式处理函数（`scheme_forms.py`）

| 函数 | 作用 |
|------|------|
| `do_define_form(expressions, env)` | 处理 `define`。两种形式：`(define x val)` 绑定变量；`(define (f x) body)` 创建命名 LambdaProcedure |
| `do_quote_form(expressions, env)` | 处理 `quote`。直接返回表达式不求值，如 `(quote (+ 1 2))` → `Link('+', Link(1, Link(2)))` |
| `do_lambda_form(expressions, env)` | 处理 `lambda`。创建 `LambdaProcedure(formals, body, env)`，不立即求值函数体 |
| `do_if_form(expressions, env)` | 处理 `if`。求值条件：为真求值第二表达式；为假且有第三表达式则求值第三表达式 |
| `do_and_form(expressions, env)` | 处理 `and`。短路求值：从左到右求值，遇 `#f` 立即返回；全部为真返回最后一个值；空参数返回 `#t` |
| `do_or_form(expressions, env)` | 处理 `or`。短路求值：从左到右求值，遇非 `#f` 立即返回；全部为 `#f` 返回 `#f` |
| `do_begin_form(expressions, env)` | 处理 `begin`。顺序求值所有表达式，返回最后一个值（调用 `eval_all`） |
| `do_cond_form(expressions, env)` | 处理 `cond`。逐个子句判断：`else` 恒真；否则求值测试表达式；为真则求值该子句的后续表达式（`eval_all`），无后续则返回测试值本身 |
| `do_let_form(expressions, env)` | 处理 `let`。创建子帧绑定局部变量，在子帧中求值函数体 |
| `make_let_frame(bindings, env)` | 辅助 `let`：解析绑定列表，求值各绑定的值，构建子帧 |
| `do_mu_form(expressions, env)` | 处理 `mu`。创建 `MuProcedure(formals, body)`，不捕获环境 |
| `do_quasiquote_form(expressions, env)` | 处理 `quasiquote`。递归处理准引用，遇到 `unquote` 时在 level=0 处求值 |
| `do_unquote(expressions, env)` | 处理 `unquote`。直接报错（只能在 quasiquote 内使用） |

### 5.5 工具函数（`scheme_utils.py`）

#### 类型谓词

| 函数 | 作用 |
|------|------|
| `scheme_procedurep(x)` | 是否为过程（`Procedure` 的实例） |
| `scheme_listp(x)` | 是否为合法列表（遍历到 `nil` 为止，中间必须都是 `Link`） |
| `scheme_booleanp(x)` | 是否为布尔值（`x is True or x is False`） |
| `scheme_numberp(x)` | 是否为数字（`numbers.Real` 实例且非布尔） |
| `is_scheme_true(val)` | Scheme 中是否为真（一切值除 `False` 外皆为真） |
| `is_scheme_false(val)` | Scheme 中是否为假（仅 `False` 为假） |
| `scheme_stringp(x)` | 是否为 Scheme 字符串（Python `str` 且以 `"` 开头） |
| `scheme_symbolp(x)` | 是否为符号（Python `str` 且非字符串） |
| `scheme_nullp(x)` | 是否为空列表（`x == nil`） |
| `scheme_atomp(x)` | 是否为原子（布尔/数字/符号/空/字符串） |
| `self_evaluating(expr)` | 是否为自求值表达式（原子且非符号，或 `None`） |

#### 验证函数

| 函数 | 作用 |
|------|------|
| `validate_type(val, predicate, k, name)` | 验证 `val` 满足 `predicate`，否则抛 `SchemeError` 指明参数位置和类型 |
| `validate_procedure(procedure)` | 验证 `procedure` 是合法的 Scheme 过程，否则抛错 |
| `validate_form(expr, min, max)` | 验证表达式是长度在 `[min, max]` 范围内的合法列表 |
| `validate_formals(formals)` | 验证形参列表：每个元素都是符号且无重复 |

### 5.6 内置过程（`scheme_builtins.py`）

通过 `@builtin` 装饰器注册，在 `create_global_frame()` 时统一绑定到全局帧。

#### 类型判断

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `procedure?` | `scheme_procedurep` | 是否为过程 |
| `list?` | `scheme_listp` | 是否为列表 |
| `atom?` | `scheme_atomp` | 是否为原子 |
| `boolean?` | `scheme_booleanp` | 是否为布尔 |
| `number?` | `scheme_numberp` | 是否为数字 |
| `symbol?` | `scheme_symbolp` | 是否为符号 |
| `string?` | `scheme_stringp` | 是否为字符串 |
| `null?` | `scheme_nullp` | 是否为空列表 |
| `pair?` | `scheme_pairp` | 是否为序对（Link） |
| `integer?` | `scheme_integerp` | 是否为整数 |
| `promise?` | `scheme_promisep` | 是否为 Promise（流） |

#### 相等判断

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `equal?` | `scheme_equalp` | 深度结构相等（递归比较 pair、数字直接比较、其他比较类型和值） |
| `eq?` | `scheme_eqp` | 浅相等（数字/符号比较值，其他比较身份 `is`） |

#### 列表操作

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `cons` | `scheme_cons` | 构造序对 `Link(x, y)` |
| `car` | `scheme_car` | 取序对的 first |
| `cdr` | `scheme_cdr` | 取序对的 rest |
| `list` | `scheme_list` | 从多个值构造列表 |
| `length` | `scheme_length` | 列表长度 |
| `append` | `scheme_append` | 拼接多个列表 |
| `set-car!` | `scheme_set_car` | 修改序对的 first（可变操作） |
| `set-cdr!` | `scheme_set_cdr` | 修改序对的 rest（可变操作） |

#### 算术运算

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `+` | `scheme_add` | 加法（支持任意多个参数，零参数返回 0） |
| `-` | `scheme_sub` | 减法（单参数取负，多参数依次减） |
| `*` | `scheme_mul` | 乘法（支持任意多个参数，零参数返回 1） |
| `/` | `scheme_div` | 除法（单参数取倒数，多参数依次除） |
| `expt` | `scheme_expt` | 幂运算 |
| `abs` | `scheme_abs` | 绝对值 |
| `quotient` | `scheme_quo` | 整除 |
| `modulo` | `scheme_modulo` | 取模 |
| `remainder` | `scheme_remainder` | 取余 |
| math 系列 | `number_fn` 包装 | `acos`, `asin`, `atan`, `ceil`, `cos`, `floor`, `log`, `sin`, `sqrt`, `tan` 等 |

#### 比较运算

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `=` | `scheme_eq` | 数字相等 |
| `<` | `scheme_lt` | 小于 |
| `>` | `scheme_gt` | 大于 |
| `<=` | `scheme_le` | 小于等于 |
| `>=` | `scheme_ge` | 大于等于 |
| `even?` | `scheme_evenp` | 是否偶数 |
| `odd?` | `scheme_oddp` | 是否奇数 |
| `zero?` | `scheme_zerop` | 是否为零 |

#### 输入输出

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `display` | `scheme_display` | 显示值（字符串不带引号，无换行） |
| `print` | `scheme_print` | 打印值（带换行） |
| `displayln` | `scheme_displayln` | 显示后换行 |
| `newline` | `scheme_newline` | 输出空行 |
| `error` | `scheme_error` | 抛出 SchemeError |
| `exit` | `scheme_exit` | 抛出 EOFError 退出 |

#### 高阶函数

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `map` | `scheme_map` | 映射：对列表每个元素应用过程（`need_env=True`） |
| `filter` | `scheme_filter` | 过滤：保留满足谓词的元素（`need_env=True`） |
| `reduce` | `scheme_reduce` | 归约：从左到右累积（`need_env=True`） |

#### 文件加载

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `load` | `scheme_load` | 加载 .scm 文件并在指定环境中执行（`need_env=True`） |
| `load-all` | `scheme_load_all` | 加载目录下所有 .scm 文件 |

#### 流（Stream）

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `force` | `scheme_force` | 强制求值 Promise |
| `cdr-stream` | `scheme_cdr_stream` | 获取流的下一个元素 |

#### Turtle 图形

| 内置名 | 函数 | 作用 |
|--------|------|------|
| `forward`/`fd` | `tscheme_forward` | 前进 |
| `backward`/`back`/`bk` | `tscheme_backward` | 后退 |
| `left`/`lt` | `tscheme_left` | 左转 |
| `right`/`rt` | `tscheme_right` | 右转 |
| `circle` | `tscheme_circle` | 画圆 |
| `setposition`/`setpos`/`goto` | `tscheme_setposition` | 设置位置 |
| `setheading`/`seth` | `tscheme_setheading` | 设置朝向 |
| `penup`/`pu` | `tscheme_penup` | 抬笔 |
| `pendown`/`pd` | `tscheme_pendown` | 落笔 |
| `showturtle`/`st` | `tscheme_showturtle` | 显示海龟 |
| `hideturtle`/`ht` | `tscheme_hideturtle` | 隐藏海龟 |
| `clear` | `tscheme_clear` | 清除画布 |
| `color` | `tscheme_color` | 设置颜色 |
| `rgb` | `tscheme_rgb` | 从 RGB 值生成颜色 |
| `begin_fill` | `tscheme_begin_fill` | 开始填充 |
| `end_fill` | `tscheme_end_fill` | 结束填充 |
| `bgcolor` | `tscheme_bgcolor` | 设置背景色 |
| `exitonclick` | `tscheme_exitonclick` | 点击退出 |
| `speed` | `tscheme_speed` | 设置速度 |
| `pixel` | `tscheme_pixel` | 画像素 |
| `pixelsize` | `tscheme_pixelsize` | 设置像素大小 |
| `screen_width` | `tscheme_screen_width` | 屏幕宽度 |
| `screen_height` | `tscheme_screen_height` | 屏幕高度 |
| `save-to-file` | `tscheme_write_to_file` | 保存到文件 |

#### 辅助函数

| 函数 | 作用 |
|------|------|
| `builtin(*names, need_env=False)` | 装饰器：将 Python 函数注册为内置过程，添加到 `BUILTINS` 列表 |
| `add_builtins(frame, funcs_and_names)` | 将内置过程列表绑定到环境帧 |
| `create_global_frame()` | 创建全局帧，绑定所有内置过程、`eval`、`apply` |
| `_check_nums(*vals)` | 检查所有参数是否为数字 |
| `_arith(fn, init, vals)` | 通用算术运算：用 `fn` 累积 `vals`，`init` 为初始值 |
| `_ensure_int(x)` | 若 `x` 等于其整数则转为 `int` |
| `_numcomp(op, x, y)` | 数字比较的通用实现 |
| `number_fn(module, name, fallback)` | 包装 math 模块函数为 Scheme 内置过程 |
| `scheme_open(filename)` | 打开 .scm 文件（尝试带/不带 .scm 后缀） |

---

## 六、主入口流程（`scheme.py`）

```
python scheme.py [file] [-load/-i]
```

1. 解析命令行参数
2. 确定输入模式：
   - 无文件 → 交互模式，`next_line = buffer_input`
   - 有文件 + `-load` → 交互模式，先加载文件
   - 有文件无 `-load` → 文件模式，`next_line = buffer_lines(lines)`
3. 调用 `read_eval_print_loop(next_line, create_global_frame_with_eval_apply(), ...)`

### `read_eval_print_loop` 的循环逻辑

```python
while True:
    src = next_line()              # 获取 Buffer
    while src.more_on_line():
        expression = scheme_read(src)    # 解析
        result = scheme_eval(expression, env)  # 求值
        if not quiet and result is not None:
            print(repl_str(result))      # 输出
```

异常处理：
- `SchemeError`/`SyntaxError`/`ValueError` → 打印错误信息继续
- `RuntimeError`（递归深度超限）→ 打印提示继续
- `KeyboardInterrupt`（Ctrl-C）→ 交互模式继续，脚本模式退出
- `EOFError`（Ctrl-D）→ 退出循环

---

## 七、模块依赖关系

```
scheme.py (主入口)
  ├── scheme_classes.py (Frame, Procedure 类)
  │     └── link.py (Link 链表)
  ├── scheme_eval_apply.py (scheme_eval, scheme_apply)
  │     ├── link.py
  │     ├── scheme_utils.py (类型检查、验证)
  │     │     └── scheme_classes.py
  │     ├── scheme_reader.py (scheme_read)
  │     │     ├── scheme_tokens.py (tokenize)
  │     │     ├── buffer.py (Buffer)
  │     │     └── link.py
  │     └── scheme_builtins.py (create_global_frame)
  │           ├── link.py
  │           ├── scheme_reader.py
  │           ├── scheme_classes.py
  │           └── scheme_utils.py
  ├── scheme_forms.py (特殊形式)
  │     ├── scheme_eval_apply.py
  │     ├── scheme_utils.py
  │     ├── scheme_classes.py
  │     └── scheme_builtins.py
  └── scheme_builtins.py
```

> 注意：`scheme_eval_apply.py` 和 `scheme_forms.py` 之间存在循环依赖，通过延迟导入（`from scheme_forms import SPECIAL_FORMS` 在函数内部）解决。

---

## 八、关键设计决策总结

1. **链表作为统一表示**：Scheme 的 S-表达式统一用 `Link` 链表表示，既是数据结构也是 AST
2. **环境链实现作用域**：`Frame` 通过 `parent` 链实现词法作用域，`lookup` 沿链向上查找
3. **Lambda 闭包 vs Mu 动态作用域**：`LambdaProcedure` 捕获定义时环境，`MuProcedure` 使用调用时环境
4. **特殊形式 vs 普通过程调用**：特殊形式（if、define 等）不预先求值参数，由 `SPECIAL_FORMS` 字典分发
5. **内置过程桥接 Python**：`BuiltinProcedure` 封装 Python 函数，`need_env` 标志决定是否传入环境
6. **尾调用优化预留**：`Unevaluated` 类和 `optimize_tail_calls` 框架已搭建，具体实现为选做题
