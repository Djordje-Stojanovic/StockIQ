# Pandoc Integration Architecture

## Professional PDF Conversion System

```python
class PandocConverter:
    def __init__(self):
        self.template_dir = Path("config/pandoc_templates")
        self.output_dir = Path("tmp/reports")
        self.pandoc_executable = "pandoc"  # Assumes pandoc in PATH
    
    async def convert_to_institutional_pdf(
        self, 
        markdown_content: str, 
        expertise_level: int,
        session_id: str,
        ticker: str
    ) -> bytes:
        """Convert markdown to institutional-grade PDF"""
        
        # Select template based on expertise level
        template_name = "comprehensive_report.latex" if expertise_level <= 5 else "executive_summary.latex"
        template_path = self.template_dir / template_name
        
        # Prepare output path
        output_filename = f"{ticker}_analysis_{session_id}.pdf"
        output_path = self.output_dir / output_filename
        temp_md_path = self.output_dir / f"temp_{session_id}.md"
        
        try:
            # Write markdown to temporary file
            with open(temp_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Prepare pandoc command
            pandoc_cmd = [
                self.pandoc_executable,
                str(temp_md_path),
                "-o", str(output_path),
                "--template", str(template_path),
                "--pdf-engine", "xelatex",
                "--table-of-contents",
                "--number-sections",
                "--highlight-style", "tango",
                "--variable", f"title:Investment Analysis - {ticker}",
                "--variable", f"subtitle:Institutional Research Report",
                "--variable", f"author:StockIQ Research Team",
                "--variable", f"date:{datetime.now().strftime('%B %d, %Y')}",
                "--variable", "geometry:margin=1in",
                "--variable", "fontsize:11pt",
                "--variable", "documentclass:article",
                "--filter", "pandoc-crossref"  # For cross-references
            ]
            
            # Execute pandoc conversion
            result = await asyncio.create_subprocess_exec(
                *pandoc_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise PandocConversionError(f"Pandoc failed: {stderr.decode()}")
            
            # Read generated PDF
            with open(output_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Cleanup temporary files
            temp_md_path.unlink()
            
            return pdf_bytes
            
        except Exception as e:
            # Cleanup on error
            if temp_md_path.exists():
                temp_md_path.unlink()
            raise PandocConversionError(f"PDF conversion failed: {str(e)}")
    
    def create_institutional_template(self) -> str:
        """Create LaTeX template for institutional reports"""
        template_content = r"""
\documentclass[$if(fontsize)$$fontsize$,$endif$$if(lang)$$babel-lang$,$endif$$if(papersize)$$papersize$paper,$endif$$for(classoption)$$classoption$$sep$,$endfor$]{$documentclass$}

% Professional institutional report styling
\usepackage[margin=1in]{geometry}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{wrapfig}
\usepackage{float}
\usepackage{colortbl}
\usepackage{pdflscape}
\usepackage{tabu}
\usepackage{threeparttable}
\usepackage{threeparttablex}
\usepackage[normalem]{ulem}
\usepackage{makecell}

% Financial report color scheme
\definecolor{primaryblue}{RGB}{25, 55, 95}
\definecolor{secondaryblue}{RGB}{70, 130, 180}
\definecolor{lightgray}{RGB}{245, 245, 245}

% Custom header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textcolor{primaryblue}{\textbf{$title$}}}
\fancyhead[R]{\textcolor{secondaryblue}{Page \thepage}}
\fancyfoot[C]{\textcolor{gray}{\footnotesize Confidential - For Investment Purposes Only}}

% Title formatting
\titleformat{\section}{\color{primaryblue}\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\color{secondaryblue}\large\bfseries}{\thesubsection}{1em}{}

% Professional title page
\title{\textcolor{primaryblue}{\Huge\textbf{$title$}}\\[0.5em]
       \textcolor{secondaryblue}{\Large $subtitle$}}
\author{\textcolor{gray}{$author$}}
\date{\textcolor{gray}{$date$}}

\begin{document}

% Title page
\maketitle
\thispagestyle{empty}

\vfill

\begin{center}
\colorbox{lightgray}{
\parbox{0.8\textwidth}{
\centering
\textbf{IMPORTANT DISCLOSURES}\\[0.5em]
This research report is for informational purposes only and does not constitute investment advice. Past performance does not guarantee future results. All investments carry risk of loss.
}}
\end{center}

\newpage

% Table of contents
$if(toc)$
{
\color{primaryblue}
\tableofcontents
}
\newpage
$endif$

% Main content
$body$

% Footer disclaimers
\vfill
\begin{center}
\footnotesize
\textcolor{gray}{
Generated by StockIQ Research Platform\\
For questions or additional analysis, contact research@stockiq.com
}
\end{center}

\end{document}
        """
        return template_content
```
