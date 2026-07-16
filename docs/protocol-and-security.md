# yanxu-http 协议与安全边界

1.0 实现严格、有预算、可确定验证的 HTTP/1.1 服务端子集。未实现能力显式失败，不做宽松猜测。

## 请求行与目标

- 请求行必须正好包含方法、目标和`HTTP/1.1`，并受 8192 字节硬上限约束；
- 方法必须是 HTTP token；目标只接受 origin-form或`*`；
- 拒绝绝对 URI、authority-form、片段、控制字符和无效百分号编码；
- 路径与查询保留原文，并提供解码后的路径段和重复查询值；
- HTTP/1.1 必须包含且只包含一个 Host；支持域名、IPv4 和方括号 IPv6，可选端口必须在 1–65535。

IPvFuture Host 不属于 1.0。应用若需要代理形式的绝对 URI，应在可信网关完成规范化，而不是放宽源站解析器。

## 首部和消息边界

- 首部区必须使用 CRLF；裸 LF、折叠行、NUL、非法名称和值控制字符被拒绝；
- 普通重复首部保留为值列；Host、Content-Length 和 WebSocket 关键首部有更严格唯一性；
- `Content-Length`只接受一项规范十进制，实际正文必须精确匹配；
- `Transfer-Encoding`只接受单一`chunked`，不能与 Content-Length 并存；
- 分块大小、扩展、数据后 CRLF、终止块和尾部逐项验证；
- 尾部禁止 framing、Host、连接、升级、Cookie 和认证等敏感字段，并受独立预算约束。

这些规则防止解析器对消息边界产生不同解释。任何 framing 错误后都应关闭连接。

## 连接状态机

`HTTP连接`使用有界缓冲处理分片读取和流水线超前字节。请求与最终响应计数必须保持顺序；临时`1xx`（除 101）不完成请求。连接在以下情况不可复用：

- 请求或响应声明`Connection: close`；
- 达到每连接请求预算；
- 对端在请求之间结束；
- 读取、解析或发送失败；
- 成功升级到其他协议；
- 调用方显式关闭。

普通套接字助手保留一次请求并关闭的兼容模型。需要 keep-alive、流水线、分块请求或升级时必须使用会话 API。

## 响应编码

`HTTP响应`验证状态码、方法语义、首部和值。1xx、204、205 与 304 禁止正文；HEAD 编码不发送正文。定长响应生成实际字节长度，分块响应生成规范块与终止块。调用方不能直接设置 framing、连接或 Set-Cookie 首部。

101 只能由 WebSocket 升级边界生成；普通编码返回`YANXUN_UPGRADE_REQUIRED`，避免套接字所有权仍留在 HTTP 会话。

## Cookie

请求 Cookie 保留重复项，并提供首值、全部值和快照。响应 Cookie 使用保守 ASCII cookie-octet；默认`Path=/`、`HttpOnly`、`SameSite=Lax`，`Secure`默认关闭以支持回环开发。

- `SameSite=None`必须配合`Secure`；
- `Partitioned`必须配合`Secure`；
- `__Secure-`要求`Secure`；
- `__Host-`要求`Secure`、`Path=/`且不能有 Domain；
- `删除（）`产生`Max-Age=0`和过期日期。

本库不生成、签名或加密会话标识。敏感 Cookie 必须来自安全随机源并由上层认证系统保护。

## 表单与 Multipart

URL 编码表单执行严格百分号解码并保留重复字段。Multipart 要求规范 boundary、CRLF 分隔、合法 Content-Disposition 和唯一受控项首部；总项数、单项首部和总正文受预算约束。

解析器不自动写文件。`安全文件名`只移除客户端路径成分与危险字符，不替代内容嗅探、病毒扫描、配额、随机存储名和目录权限。

## WebSocket 升级

握手必须使用 GET / HTTP/1.1，包含`Connection: Upgrade`、唯一`Upgrade: websocket`、规范 16 字节 Base64 密钥和唯一版本 13，且不得有 HTTP 正文或 close token。接受值按 RFC 6455 计算。

Origin 不自动信任；浏览器场景应调用精确允许列表。子协议只能从客户端提供列表中按服务器偏好选择。扩展首部只保留原文。成功发送 101 后，套接字和已缓冲字节原子式移交给`HTTP升级通道`。

本库不实现帧掩码、消息重组、控制帧、关闭握手、ping/pong、压缩或每消息预算。调用方必须在升级通道之上提供完整且受测的协议实现。

## 部署

本库没有 TLS、代理信任、并发调度、速率限制、慢连接全局治理、访问日志轮转或优雅进程重启。面向公网的服务应使用受维护的 TLS 反向代理和上层框架，并显式配置可信代理、并发、身份认证、超时、日志脱敏和关停流程。

完整威胁模型见 [SECURITY_MODEL.md](SECURITY_MODEL.md)，资源模型见 [PERFORMANCE.md](PERFORMANCE.md)。
