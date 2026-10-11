# 全球制裁与出口管制清单 · 官方源索引

> 一份**结构化、可机读的官方制裁 / 出口管制清单数据源索引**，覆盖中、美、欧、联合国及主要亚太管辖区。
> 作为 [`cn-sanctions-screening`](https://github.com/nixiaofen/cn-sanctions-screening) 筛查工具的**数据源地图**而维护——工具负责"怎么筛"，本仓库负责"筛什么源"。

## 这是什么

- 不是清单正文，而是**清单的官方入口索引**：每个源都给出管辖区、管理机关、法律依据、查询网址、可直接下载/检索的数据文件地址（`download_url`）、数据格式与最近核验日期。
- 纯公开信息整理，**零保密风险**；只索引官方源，不中转、不仓储任何受制裁主体数据。
- 配套 `verify.py` 可一键校验所有 `download_url` 是否仍然可达，并由 GitHub Actions **每月自动跑一次**，链接失效会自动开 issue。

## 文件结构

```
sources.csv                 # 制裁清单数据源（25 项，含中/美/欧/联合国/英/瑞/澳/加/世行/日/新/韩/新）
export-control-sources.csv  # 出口管制清单（单列，5 项：美 BIS Entity List/MEU/UVL、中国两用物项、欧盟双重用途）
verify.py                   # 链接可用性校验脚本（仅依赖 Python 标准库）
.github/workflows/link-check.yml  # 每月定时跑 verify.py，失效自动开 issue
```

## 字段说明

`sources.csv` 字段：

| 字段 | 含义 |
|------|------|
| `jurisdiction` / `jurisdiction_en` | 管辖区（中文 / 英文） |
| `list_name` / `list_name_en` | 清单名称（中文 / 英文） |
| `authority` / `authority_en` | 管理机关 |
| `legal_basis` | 法律依据 |
| `official_url` | 官方查询入口 |
| `download_url` | 可直接下载 / 检索的数据文件地址（脚本校验对象） |
| `format` | 数据格式：csv / xml / json / html 等 |
| `update_freq` | 更新频率 |
| `last_verified` | 最近核验日期（YYYY-MM-DD） |
| `scope` | 覆盖范围简述 |
| `notes` | 备注（含子集关系、时效提醒等） |

`export-control-sources.csv` 字段略少（无 `legal_basis`、`jurisdiction_en`），其余含义相同。
**制裁清单与出口管制清单性质不同，故分表存放。**

## 使用方法

本地校验所有链接：

```bash
python verify.py                 # 校验全部，输出汇总表
python verify.py --fail-only     # 只显示不可达项
python verify.py --csv out.csv   # 额外把结果写出到 out.csv
```

退出码 `0` = 全部可达；`1` = 存在不可达项（供 CI 判定）。

> 注意：部分 `download_url` 是官网**检索/着陆页**（格式标注为 `html`）而非直接数据文件，这类页面能打开即视为可达；真正的数据文件（csv/xml）会被校验内容类型是否吻合。

## 数据时效与免责声明

- 清单数据**变动频繁**。每源均带 `last_verified` 字段，本仓库数据截至 **2026-10-11**；用时请以官方最新发布为准。
- 本仓库为**信息整理与工程实践示例**，**不构成法律意见、合规结论或制裁建议**。是否列入清单、是否触发制裁，请以各国官方发布与专业法律意见为准。
- 中国"恶意实体清单"首批名单截至建表日尚未公布，已在 `notes` 中标注。

## 贡献

欢迎 PR：补充遗漏管辖区、修正失效链接、更新 `last_verified`。改动 `download_url` 后跑一遍 `verify.py` 确认可达即可。

## 许可

- 数据（CSV）：[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)（事实性整理，进入公共领域）
- 代码（`verify.py`、CI）：MIT
