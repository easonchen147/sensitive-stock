## 1. OpenSpec 与主规格收口

- [x] 1.1 完成 proposal、design、spec delta，覆盖运行态状态语言、正式 workbench 语义与文档收口范围。
- [x] 1.2 同步主 OpenSpec 规格与当前生效文档，移除 placeholder endpoint 和 `migrated / skeleton / planned` 残留表述。

## 2. 后端展示文案与 OpenAPI 对齐

- [x] 2.1 将回测预设、回测 assumptions / insights、预测 backtest handoff 的用户可见文案改为中文产品语言。
- [x] 2.2 调整 `backend/app/openapi.py` 摘要与标签说明并重新生成根目录 `openapi.json`。
- [x] 2.3 更新受影响的后端测试断言，确保展示文案与契约变更被覆盖。

## 3. 验证、归档与知识沉淀

- [x] 3.1 运行 targeted tests、full backend checks、frontend checks、OpenSpec strict 与 diff check，并修复发现的问题。
- [x] 3.2 归档 `remove-runtime-migration-state-residue` change，并新增一篇 solutions 文档沉淀这次“规格真实化”模式。
