# yanxu-http

[![CI](https://github.com/yanxulang/yanxu-http/actions/workflows/ci.yml/badge.svg)](https://github.com/yanxulang/yanxu-http/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Yanxu 1.1.6+](https://img.shields.io/badge/言序-1.1.6%2B-b33.svg)](https://github.com/yanxulang/yanxu)

`yanxu-http` 是言序的严格 HTTP/1.1 服务端协议基础库。稳定版 `1.0.0` 负责安全解析请求、管理持久连接、编码响应，并提供表单、Cookie、路由视图和 WebSocket 握手边界；路由调度、中间件、模板与应用生命周期留给上层库。

## 主要能力

- 严格解析请求行、`Host`、首部、查询、Cookie、定长正文与分块正文；
- 防御冲突长度、重复关键首部、模糊传输编码、首部注入和常见请求走私输入；
- 通过 `HTTP限制` 控制超时、请求行、首部、正文、分块、尾部、Multipart 和连接请求数；
- 在一个 TCP 连接上顺序处理 keep-alive、流水线请求、临时 `1xx` 响应与定长/分块响应；
- 解析 `application/x-www-form-urlencoded` 与有界 `multipart/form-data`，保留重复字段和文件字节；
- 提供严格 Cookie、`__Host-` / `__Secure-` 前缀、`SameSite`、`Partitioned` 与删除语义；
- 暴露规范化 Host、原始路径/查询、路径段、方法性质和稳定路由视图；
- 验证 RFC 6455 WebSocket 握手、Origin 允许列表和子协议，并安全移交已缓冲的 TCP 字节；
- 提供 HTML、JSON、言据、文字、字节、状态和重定向响应。

## 安装

使用官方包管理器[言包](https://github.com/yanxulang/yanbao)添加并锁定稳定版本：

```sh
yanbao add http --version '^1.0'
yanbao install
```

`http`解析为 GitHub 上的`yanxulang/yanxu-http`。`言序.lock`固定精确修订和内容校验，不需要 submodule。

## 五分钟示例

离线解析适合应用单元测试：

```yanxu
引「包:http」为 HTTP；
引「标准:字节」为 字节；

定 请求 为 HTTP.解析请求（
    「POST /search?q=言序&q=web HTTP/1.1\r\nHost: localhost\r\nContent-Length: 6\r\nCookie: theme=dark」，
    字节.从文字（「正文」）
）；

言 请求.方法；                  # POST
言 请求.路径；                  # /search
言 请求.查询全部（「q」）；     # 【「言序」，「web」】
言 请求.Cookie值（「theme」）； # dark

定 响应 为 HTTP.JSON响应（{「ok」：真}）
    .设首部（「cache-control」，「no-store」）
    .添Cookie（
        HTTP.Cookie（「sid」，「abc123」）
            .设安全（真）
            .设同站（「Lax」）
    ）；

定 响应字节 为 响应.编码（）；
```

服务端应为每条已接受套接字创建 `HTTP连接`，再按顺序读取和响应：

```yanxu
定 会话 为 HTTP.连接会话（连接）；
当 真 则
    定 请求：HTTP.HTTP请求? 为 会话.读取下一请求（）；
    若 （请求 是 空） 则
        断；
    终
    会话.发送响应（请求，HTTP.JSON响应（{「path」：请求.路径}））；
终
会话.关闭（）；
```

`读取下一请求`在对端正常结束时返回`空`。会话会保留超前读取的流水线字节，并根据请求版本语义和响应选择决定是否复用连接。

## 权限

库清单只声明回环 TCP 监听：`127.0.0.1`、`::1` 与`localhost`。应用必须按实际部署地址声明自己的最小 `TCP监听` 权限。库不申请文件、任意网络、UDP、环境、进程或原生扩展权限。

## 兼容性

- 最低言序：`1.1.6`；CI 同时验证当前稳定版 `1.1.8`；
- 协议：HTTP/1.1 服务端，严格 CRLF；
- 平台：纯言序协议实现；TCP 集成在 Linux、macOS 与 Windows 的最低工具链矩阵中检查；
- WebSocket：只负责版本 13 握手和连接所有权移交，不实现帧、压缩或关闭握手。

完整矩阵见 [COMPATIBILITY.md](COMPATIBILITY.md)。

## 错误处理

协议和资源错误具有稳定的 `YANXUN_*` 代码。不要解析展示文字；使用 `HTTP.错误详情（所误）`读取`代码`、`消息`、运行时类别、位置和踪迹：

```yanxu
试 则
    HTTP.解析请求头（输入）；
救 所误 则
    定 详情 为 HTTP.错误详情（所误）；
    言 详情【「代码」】；
终
```

错误族与恢复建议见 [docs/ERRORS.md](docs/ERRORS.md)。

## 已知限制

- 不实现 TLS、HTTP/2、HTTP/3、代理头信任、并发调度、速率限制或应用级背压；
- 只接受 origin-form 与`*`请求目标；IPvFuture Host 未纳入 1.0；
- Multipart 是有界内存解析器，不自动落盘，也不解码传输编码或扩展文件名参数；
- WebSocket 扩展只作为原文暴露，调用方不得在未实现扩展语义时回显协商；
- `JSON响应`使用标准 JSON；`言据响应`接收已经由`yanju`规范序列化的文字，本库不复制言据解析器。

这些边界使库适合作为服务端协议层，而不是完整公网服务器。部署建议见 [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md)。

## 文档

- [使用指南](docs/GUIDE.md)
- [生成的公开 API](docs/API.md)
- [协议与安全边界](docs/protocol-and-security.md)
- [架构](docs/ARCHITECTURE.md)
- [性能与资源预算](docs/PERFORMANCE.md)
- [从 0.1 迁移](docs/MIGRATION_1.0.md)
- [贡献指南](CONTRIBUTING.md)

`examples/`包含离线请求、响应、表单与单次 TCP 服务器；`integration/`以真实 TCP 字节验证 keep-alive、流水线、分块、临时响应和 WebSocket 升级；`benchmarks/`提供确定性解析负载。

按 [MIT License](LICENSE) 发布。
