# yanxu-http

[![CI](https://github.com/yanxulang/yanxu-http/actions/workflows/ci.yml/badge.svg)](https://github.com/yanxulang/yanxu-http/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Yanxu 1.1.5](https://img.shields.io/badge/言序-1.1.5-b33.svg)](https://github.com/yanxulang/yanxu)

`yanxu-http` 是言序的 HTTP/1.1 服务端协议基础库。它负责把 TCP 字节转换为有边界的请求对象，再把状态、首部、Cookie 和正文编码为响应；路由、模板和应用生命周期留给上层库。

## 0.1 能力

- 解析 HTTP/1.1 请求行、请求首部和 origin-form 请求目标；
- 按`Content-Length`读取文字或二进制正文；
- 解析重复查询参数和请求 Cookie；
- 构造状态码、响应首部和安全默认 Cookie；
- 提供 HTML、JSON、言据、文字、字节、状态和重定向响应；
- 默认限制首部为 64 KiB、正文为 4 MiB、读写超时为 5 秒；
- 拒绝首部注入、重复关键首部、正文长度不一致和当前不支持的传输模式。

0.1 采用刻意简单的连接模型：请求首部使用 UTF-8 和 CRLF，响应固定`Connection: close`，每个 TCP 连接只处理一个请求。它适合教学、本地开发和上层框架的首版实现，不应直接作为面向公网的生产服务器。

## 快速开始

使用官方包管理器[言包](https://github.com/yanxulang/yanbao)添加并锁定依赖：

```sh
yanbao add http --version '^0.1'
```

`http`会自动解析为 GitHub 上的`yanxulang/yanxu-http`。`言序.lock`固定精确提交和内容校验；项目不需要维护 submodule。

解析一条请求：

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
```

构造响应：

```yanxu
定 响应 为 HTTP.JSON响应（{「ok」：真}）；
响应.设首部（「x-powered-by」，「yanxu-http」）；
响应.添Cookie（
    HTTP.Cookie（「sid」，「abc123」）.设安全（真）.设同站（「Lax」）
）；

定 响应字节 为 响应.编码（）；
```

`编码`会补充按实际字节计算的`Content-Length`与`Connection: close`。调用者不能覆盖`content-length`、`connection`或`set-cookie`，以免破坏编码器的不变量。

## 协议边界

| 项目 | 0.1 行为 |
| --- | --- |
| 协议 | 仅`HTTP/1.1`，请求必须含非空`Host`。 |
| 请求目标 | 仅 origin-form（`/path?query`）与`*`。 |
| 首部 | 严格 CRLF、UTF-8，不支持折叠；关键首部不可重复。 |
| 正文 | 仅单一十进制`Content-Length`，最多 4 MiB。 |
| 传输编码 | 出现`Transfer-Encoding`即拒绝。 |
| 连接 | 一连接一请求，响应后关闭。 |
| 响应首部 | 名称按 token 校验，值拒绝 NUL、CR、LF。 |

更完整的拒绝规则和代理部署注意事项见[协议与安全边界](docs/protocol-and-security.md)。

## 言据响应

HTTP 层不复制言据序列化器。调用方先用[`yanju`](https://github.com/yanxulang/yanju)得到文字，再交给`言据响应`；本库只负责`application/vnd.yanxu.yanju; charset=utf-8`媒体类型与传输编码。

## 文档

- [入门与单次服务器](docs/getting-started.md)
- [公开 API 参考](docs/api.md)
- [协议与安全边界](docs/protocol-and-security.md)
- [言序文档站：HTTP/1.1 基础](https://docs.yanxu.dev/web/http/)

`examples/`包含离线解析、响应编码和单次 TCP 服务器；`tests/解析与响应.yx`覆盖核心协议不变量。

## 开发与验收

始终从言序总工作区根目录运行：

```sh
yanxu-language-new/target/debug/yanxu 查 yanxu-http/src/言序HTTP.yx
yanxu-language-new/target/debug/yanxu 试 yanxu-http/tests --json
yanxu-language-new/target/debug/yanxu 执 yanxu-http/examples/解析请求.yx
```

## 演进方向

当前版本是 `0.1.1`。计划按独立里程碑逐步加入请求分块传输、持久连接复用、Multipart 文件上传、WebSocket、HTTP/2 和 HTTP/3；每项能力都需要在解析预算、超时、背压和安全测试完成后才会进入稳定接口。详见[Web 栈安全与路线图](https://docs.yanxu.dev/web/security-roadmap/)。

按 [MIT License](LICENSE) 发布。
