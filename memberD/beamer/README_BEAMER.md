# Beamer 版汇报稿

文件：

- `RAG_security_beamer.tex`

## Overleaf 编译方式

1. 新建 Overleaf 项目。
2. 上传 `RAG_security_beamer.tex`。
3. 上传图表目录里的四张图片：
   - `D_member/charts/asr.png`
   - `D_member/charts/lrate.png`
   - `D_member/charts/utility_orr.png`
   - `D_member/charts/score.png`
4. 在 Overleaf 中保持目录结构为：

```text
main project/
├── beamer/
│   └── RAG_security_beamer.tex
└── charts/
    ├── asr.png
    ├── lrate.png
    ├── utility_orr.png
    └── score.png
```

或者直接把 `.tex` 放在项目根目录时，把正文里的图片路径从 `../charts/...` 改成 `charts/...`。如果 Overleaf 报 `File '../charts/asr.png' not found`，基本就是这个路径问题。

如果报 `Package PGF Math Error: Unknown function 'of'`，说明旧版本 tex 没有加载 TikZ positioning 库；当前版本已经加入：

```tex
\usetikzlibrary{positioning}
```

## 编译器

请选择 `XeLaTeX`，因为文档使用了中文 `ctex`。

## 注意

第 10 页结果图表目前是样例/mock 数据。等 A 成员接口和 B 成员正式数据到位后，先重新运行：

```bash
cd D_member
python eval/run_eval.py
python eval/aggregate_metrics.py
python eval/plot_results.py
```

然后再把新的四张图上传到 Overleaf。
