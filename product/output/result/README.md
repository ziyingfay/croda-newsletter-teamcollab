# product/output/result 公共输出目录

这是 Croda 项目各程序之间共享的公共交接区。

规则：

- 爬虫结果写入 `product/output/result/spider/YYYYMM/`。
- 打标程序从 `product/output/待打标.json` 读取。
- 打标结果写入 `product/output/result/tagging/YYYYMM/`。
- 报告生成从公共结果目录读取，写入 `product/output/result/report/YYYYMM/`。
- 严禁下游程序跨目录读取其他组件的私有空间。

RSS clean JSON 每次生成两份：

```text
product/output/result/spider/YYYYMM/YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
```

两份文件创建时必须完全一致。
打标成功后删除 `product/output/待打标.json`。
