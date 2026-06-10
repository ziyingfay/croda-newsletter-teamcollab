# output 目录说明

Croda 项目的运行输出根目录。程序之间共享的公共结果交接区是：

```text
product/output/result/
```

## 公共目录规则

```text
product/output/result/
├── spider/YYYYMM/
├── tagging/YYYYMM/
└── report/YYYYMM/
```

严禁下游程序跨目录读取其他组件的私有空间。

## RSS Clean JSON

```text
product/output/result/spider/YYYYMM/YYYYMMDD-HHMMSS-rss-clean.json
product/output/待打标.json
```

两份文件创建时必须完全一致。时间戳文件用于归档，`product/output/待打标.json` 供打标程序固定读取，打标成功后删除。
