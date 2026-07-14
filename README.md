# yanxu-http

`yanxu-http` 为言序提供首版 HTTP/1.1 服务端基础：请求行与首部解析、`Content-Length` 正文读取、状态码、响应首部、Cookie、查询参数，以及 HTML、JSON、言据、文字和字节响应。

## 0.1 协议模型

- HTTP/1.1；请求行与首部必须是 UTF-8。
- 每个 TCP 连接只处理一个请求，响应固定 `Connection: close`。
- 请求正文只接受单一合法 `Content-Length`。
- 明确拒绝请求 `Transfer-Encoding`；分块请求将在后续版本加入。
- 请求首部默认最多 64 KiB，正文最多 4 MiB，读写默认超时 5 秒。
- 响应 `Content-Length` 按 UTF-8/二进制字节数计算，首部值拒绝 CR/LF 注入。

## 示例

```yanxu
引「包:yanxu-http」为 HTTP；
引「标准:字节」为 字节；

定 请求 为 HTTP.解析请求（
    「GET /?q=yanxu HTTP/1.1\r\nHost: localhost」，
    字节.从文字（「」）
）；

言 请求.查询值（「q」）；
定 响应 为 HTTP.JSON响应（据【「ok」：真】）；
```

言据响应接受已经由 `yanju` 序列化的文字，HTTP 层负责 `application/vnd.yanxu.yanju` 媒体类型，不复制数据格式实现。

本地验收（从总工作区根目录执行）：

```sh
yanxu-language-new/target/debug/yanxu 查 yanxu-http/src/言序HTTP.yx
yanxu-language-new/target/debug/yanxu 试 yanxu-http/tests --json
```

当前版本是 `0.1.0`，按 MIT License 发布。
