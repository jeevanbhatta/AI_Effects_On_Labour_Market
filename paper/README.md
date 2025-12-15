# Paper Directory

This folder contains the LaTeX source files for the SS154 Final Project paper.

## Files

- `main.tex` - Main LaTeX document with all sections
- `references.bib` - BibTeX bibliography file
- `figures/` - Directory containing exported figures
- `tables/` - Directory for R-exported regression tables

## Generated Figures (from Python)

The following figures have been exported from `analysis/preliminary_analysis.ipynb`:

| Figure | Description |
|--------|-------------|
| `parallel_trends.pdf` | Main parallel trends visualization |
| `did_visualization.pdf` | DiD design illustration |
| `covid_impact.pdf` | COVID-19 impact by industry |
| `correlation_matrix.pdf` | Control variable correlations |
| `employment_trends_normalized.pdf` | Normalized employment trends |
| `employment_trends_raw.pdf` | Raw employment levels |

## R Analysis Script

Run `analysis/did_analysis.R` to generate:
- Regression tables (`tables/main_results.tex`, `tables/robustness.tex`)
- Event study figure (`figures/event_study.pdf`)
- Additional parallel trends plot (`figures/parallel_trends_R.pdf`)

```r
# In RStudio, set working directory to analysis/
setwd("analysis")
source("did_analysis.R")
```

## Compilation

### Using Overleaf (Recommended)
1. Create a new project on [Overleaf](https://www.overleaf.com)
2. Upload `main.tex` and `references.bib`
3. Set the compiler to pdfLaTeX
4. Click "Recompile"

### Using Local LaTeX Installation
```bash
# Navigate to paper directory
cd paper

# Compile with bibliography
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use `latexmk`:
```bash
latexmk -pdf main.tex
```

## Adding Figures

1. Export figures from R using `ggsave()`:
```r
ggsave("figures/parallel_trends.pdf", plot, width = 10, height = 6)
```

2. Include in LaTeX:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{figures/parallel_trends.pdf}
\caption{Your Caption}
\label{fig:your_label}
\end{figure}
```

## Adding Tables

Use the `stargazer` package in R to export regression tables:
```r
library(stargazer)
stargazer(model1, model2, model3,
          type = "latex",
          out = "tables/main_results.tex",
          title = "Main Results",
          label = "tab:main_results")
```

Then include in LaTeX:
```latex
\input{tables/main_results.tex}
```

## Checklist Before Submission

- [ ] All author names in alphabetical order
- [ ] Abstract under 250 words
- [ ] All sections numbered
- [ ] All figures and tables have captions and labels
- [ ] All figures and tables referenced in text
- [ ] Bibliography compiles correctly
- [ ] Links to GitHub/data are accessible
- [ ] Grammarly check completed
- [ ] PDF is readable and properly formatted
