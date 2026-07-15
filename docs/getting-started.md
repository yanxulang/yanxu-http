# yanxu-http 入门

`yanxu-http`既可以离线解析已经分离的请求首部与正文，也可以从言序套接字读取一个完整请求。先用离线 API 测试应用逻辑，再在需要时接入 TCP。

## 1. 添加依赖

```sh
yanbao add http --version '^0.1'
yanbao install
```

言包负责下载 Git 源码并在`言序.lock`固定精确提交；重新选择远端版本时使用`yanbao update`，无需 submodule。

`yanxu-http`需要回环地址的 TCP 监听权限。应用的`言序.toml`也应按实际地址声明最小权限：

```toml
[权限]
TCP监听 = ["127.0.0.1", "::1", "localhost"]
```

## 2. 离线解析

`解析请求头`接收不包含末尾空行的首部文字，适合无正文请求：

```yanxu
引「包:http」为 HTTP；

定 请求 为 HTTP.解析请求头（
    「GET /articles?page=1 HTTP/1.1\r\nHost: localhost\r\nCookie: theme=dark」
）；

言 请求.方法；
言 请求.路径；
言 请求.查询值（「page」）；
言 请求.Cookie值（「theme」）；
```

有正文时使用`解析请求（首部原文，正文字节）`。正文长度必须与请求中的`Content-Length`完全一致。

## 3. 选择响应工厂

```yanxu
HTTP.文字响应（「ok」）；
HTTP.HTML响应（「<h1>可信 HTML</h1>」）；
HTTP.JSON响应（{「ok」：真}）；
HTTP.言据响应（「据【「ok」：真】」）；
HTTP.字节响应（所字节）；
HTTP.状态响应（404，「Not Found」）；
HTTP.重定向响应（「/new-location」，302）；
```

`HTTP.HTML响应`接收已经生成的 HTML 文字，不做 HTML 转义。应用代码应使用`yanxu-html`生成节点，并通过`yanxu-web`的`Web.HTML响应`完成安全渲染。

## 4. 设置首部与 Cookie

```yanxu
定 响应 为 HTTP.文字响应（「已登录」）；
响应.设首部（「cache-control」，「no-store」）；
响应.添Cookie（
    HTTP.Cookie（「session」，「abc123」）
        .设路径（「/」）
        .设安全（真）
        .设仅HTTP（真）
        .设同站（「Lax」）
）；
```

Cookie 默认`Path=/`、`HttpOnly`、`SameSite=Lax`。生产 HTTPS 会话还应显式启用`Secure`；`SameSite=None`若未同时启用`Secure`会被拒绝。

## 5. 单次 TCP 服务器

```yanxu
引「包:http」为 HTTP；
引「标准:套接字」为 套接字；

定 监听器：套接字 为 套接字.TCP监听（「127.0.0.1:8080」）；
定 已接受：典 为 套接字.接受（监听器，5000）；
定 连接：套接字 为 已接受【「套接字」】；

试 则
    定 请求 为 HTTP.读取请求（连接）；
    HTTP.发送响应（连接，HTTP.JSON响应（{
        「method」：请求.方法，
        「path」：请求.路径
    }））；
救 所误 则
    HTTP.发送响应（连接，HTTP.状态响应（400，「Bad Request」））；
终

套接字.关闭（连接）；
套接字.关闭（监听器）；
```

需要路由、中间件、静态文件和持续接受连接时，改用[`yanxu-web`](https://github.com/yanxulang/yanxu-web)。
