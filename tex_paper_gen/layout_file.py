import subprocess
import os
# Sample questions with scientific notation
questions = [
    {
        "text": "Calculate the energy equivalent of a mass using $E = mc^2$. Assume m = 2 kg.",
        "type": "written"
    },
    {
        "text": "What is the value of Avogadro's number?",
        "type": "multiple_choice",
        "options": ["$6.022 \\times 10^{23}$", "$6.022 \\times 10^{24}$", "$3.141 \\times 10^{23}$", "$1.414 \\times 10^{23}$"]
    },
]

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True) 

def generate_latex_code(questions):
    latex_content = r"""
\documentclass{exam}
\usepackage{amsmath}
\begin{document}
\title{Automated Exam Paper}
\maketitle
\begin{questions}
"""
    for q in questions:
        latex_content += r"\question " + q['text'] + "\n"
        if q['type'] == 'multiple_choice':
            latex_content += r"\begin{choices}"
            for option in q['options']:
                latex_content += r"\choice " + option + "\n"
            latex_content += r"\end{choices}"
        elif q['type'] == 'written':
            latex_content += r"\vspace{3cm}"  # Space for answer
        latex_content += "\n"  # Newline for each question
    latex_content += r"""
\end{questions}
\end{document}
"""
    return latex_content

def save_latex_file(content, filename="exam.tex"):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as file:
        file.write(content)
    return filepath

def compile_latex(filename="exam.tex"):
    filepath = os.path.join(output_dir, filename)
    subprocess.run(["pdflatex", "-output-directory", output_dir, filepath], check=True)


def generate_exam_pdf(questions):
    latex_content = generate_latex_code(questions)
    tex_filepath = save_latex_file(latex_content)
    compile_latex(os.path.basename(tex_filepath)) 


generate_exam_pdf(questions)
