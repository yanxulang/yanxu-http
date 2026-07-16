# 贡献指南

## 改动原则

- 保持协议解析严格、确定且有显式预算；
- 新增拒绝分支时提供稳定`YANXUN_*`代码与错误路径测试；
- 不把路由调度、模板、TLS 或应用生命周期塞入协议层；
- 不以字符串拼接或宽松猜测修复互操作问题；
- 公共 API 使用自然中文命名，并同步指南、生成 API 与迁移说明；
- 每个独立可验证改动使用一个自然、专业的提交。

## 本地门禁

在包含本仓库和言序源码的总工作区根目录运行，按实际路径替换工具位置：

```sh
yanxu-language-new/target/debug/yanxu 查 yanxu-libraries-workspace/repos/yanxu-http/src/言序HTTP.yx
yanxu-language-new/target/debug/yanxu 试 yanxu-libraries-workspace/repos/yanxu-http/tests --json
yanxu-language-new/target/debug/yanxu 兼容 yanxu-libraries-workspace/repos/yanxu-http/tests --json
yanxu-language-new/target/debug/yanxu 编 yanxu-libraries-workspace/repos/yanxu-http -o /tmp/yanxu-http.yxb --release
```

还应逐个以字节码 VM 执行规格和离线示例，并运行真实 TCP 集成：

```sh
python3 -B yanxu-libraries-workspace/repos/yanxu-http/integration/持久连接.py \
  --yanxu yanxu-language-new/target/debug/yanxu \
  --backend tree
```

把`--backend`改为`vm`后再执行一次。发布改动还必须用最低言序 1.1.6 重复门禁，并让最低工具链最后生成包锁。

## 测试要求

协议特性至少覆盖正常输入、边界值、无效输入、预算耗尽、稳定错误代码与树/VM 一致性。连接状态特性必须使用真实 TCP 字节验证超前读取、部分读写与所有权转移；不能只用离线对象代替网络边界。

性能改动应运行`benchmarks/解析负载.yx`，记录相同工具链和硬件上的前后结果。基准必须校验计算结果，不能只输出耗时。

## Pull Request

说明兼容性、破坏性变化、测试命令、权限变化和迁移方式。不得提交凭据、真实用户数据、生成的二进制或临时测试输出。合并前要求格式、静态检查、规格、集成、文档、包锁、权限和发布构建全部通过。
