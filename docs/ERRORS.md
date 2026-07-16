# 稳定错误

所有库主动产生的错误以`YANXUN_`开头。`HTTP.错误详情（所误）`返回：

| 键 | 含义 |
| --- | --- |
| `代码` | 稳定、可供程序判断的代码 |
| `消息` | 面向人的说明，不承诺逐字稳定 |
| `源代码` | 言序运行时错误代码 |
| `类别` | 运行时错误类别 |
| `位置` | 源位置（若可用） |
| `踪迹` | 运行时踪迹 |

非本库错误会归一为`YANXUN_RUNTIME`，同时保留运行时字段。

## 主要错误族

| 前缀或代码 | 场景 | 调用方策略 |
| --- | --- | --- |
| `YANXUN_LIMIT_*` | 超时、首部、正文、分块、表单或会话预算越界 | 返回 413/414/431 或关闭连接，不放宽为无限值 |
| `YANXUN_REQUEST_*`、`YANXUN_METHOD`、`YANXUN_TARGET` | 请求行或目标非法 | 400 后关闭连接 |
| `YANXUN_HEADER_*`、`YANXUN_HOST_*` | 首部语法、Host 或重复关键首部非法 | 400 后关闭连接 |
| `YANXUN_FRAMING_CONFLICT` | 长度与传输编码冲突 | 立即关闭，不能继续解析流水线 |
| `YANXUN_TRANSFER_ENCODING`、`YANXUN_CHUNK_*` | 分块编码或尾部非法 | 400 后关闭连接 |
| `YANXUN_FORM_*`、`YANXUN_MULTIPART_*` | 表单媒体类型、边界、项首部或内容非法 | 400 或 413 |
| `YANXUN_COOKIE_*` | Cookie 名、值、属性或安全前缀非法 | 拒绝写入或请求 |
| `YANXUN_RESPONSE_*`、`YANXUN_STATUS` | 响应状态、正文或 framing 冲突 | 修复服务端代码，不向客户端重试相同响应 |
| `YANXUN_CONNECTION_*`、`YANXUN_RESPONSE_ORDER` | 会话已关闭、已升级或响应顺序错误 | 停止使用旧会话所有者 |
| `YANXUN_WEBSOCKET_*`、`YANXUN_UPGRADE_*` | 握手、Origin、子协议或所有权转换非法 | 版本错误可发 426，其余按策略拒绝 |

错误恢复必须考虑 framing 是否仍可信。请求行、首部、正文或分块解码失败后，默认关闭当前连接；不要尝试从任意后续字节重新同步。
