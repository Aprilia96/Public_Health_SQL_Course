#!/usr/bin/env python3
"""Generate visual diagrams for the PDF course."""
import os, math
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUTDIR = "/home/claude/uk-public-health-course/images"
os.makedirs(OUTDIR, exist_ok=True)

def save_fig(name, fig, dpi=100):
    path = os.path.join(OUTDIR, f"{name}.png")
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  {name}.png")

# ============ 1. File system structure (Lesson 2) ============
def gen_filesystem():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'File system: Windows vs. Unix', ha='center', fontsize=13, weight='bold')
    
    # Windows box
    box1 = FancyBboxPatch((0.3, 4.5), 4, 4, boxstyle="round,pad=0.1", 
                          edgecolor='#005eb8', facecolor='#eef4fb', linewidth=2)
    ax.add_patch(box1)
    ax.text(2.3, 8.2, 'Windows', fontsize=11, weight='bold', color='#005eb8')
    win_lines = [
        "C:\\ (drive root)",
        "Users\\alice\\Documents\\",
        "backslash \\ separator",
        "%USERPROFILE% shorthand"
    ]
    for i, line in enumerate(win_lines):
        ax.text(0.6, 7.8-i*0.65, f"• {line}", fontsize=9, family='monospace')
    
    # Unix box
    box2 = FancyBboxPatch((5.7, 4.5), 4, 4, boxstyle="round,pad=0.1",
                          edgecolor='#0e7c86', facecolor='#f2f8f8', linewidth=2)
    ax.add_patch(box2)
    ax.text(7.7, 8.2, 'macOS / Linux', fontsize=11, weight='bold', color='#0e7c86')
    unix_lines = [
        "/ (root)",
        "~/Documents/  or",
        "/home/alice/docs/",
        "forward / separator"
    ]
    for i, line in enumerate(unix_lines):
        ax.text(6, 7.8-i*0.65, f"• {line}", fontsize=9, family='monospace')
    
    # Tip at bottom
    ax.text(5, 1.2, 'Lesson: Always use forward slashes in R/Python; they work on all systems.',
            ha='center', fontsize=9, style='italic', bbox=dict(boxstyle='round', 
            facecolor='#f1eefa', alpha=0.8))
    
    save_fig("01_filesystem", fig)

# ============ 2. Database concepts (Lesson 9) ============
def gen_database_schema():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    
    ax.text(5, 9.5, 'Relational database: tables & keys', ha='center', 
            fontsize=13, weight='bold')
    
    # Patients table
    tbl1 = FancyBboxPatch((0.3, 5.5), 2.8, 3, boxstyle="round,pad=0.05",
                          edgecolor='#0e7c86', facecolor='#f2f8f8', linewidth=1.5)
    ax.add_patch(tbl1)
    ax.text(1.7, 8.2, 'patients', fontsize=10, weight='bold', ha='center')
    patients_cols = [
        "patient_id (PK)",
        "name",
        "birth_date",
        "practice_code (FK)"
    ]
    for i, col in enumerate(patients_cols):
        ax.text(0.5, 7.8-i*0.55, col, fontsize=8, family='monospace')
    
    # Practices table
    tbl2 = FancyBboxPatch((3.6, 5.5), 2.8, 3, boxstyle="round,pad=0.05",
                          edgecolor='#0e7c86', facecolor='#f2f8f8', linewidth=1.5)
    ax.add_patch(tbl2)
    ax.text(5, 8.2, 'gp_practices', fontsize=10, weight='bold', ha='center')
    practices_cols = [
        "practice_code (PK)",
        "practice_name",
        "icb_name",
        "list_size"
    ]
    for i, col in enumerate(practices_cols):
        ax.text(3.8, 7.8-i*0.55, col, fontsize=8, family='monospace')
    
    # Admissions table
    tbl3 = FancyBboxPatch((6.9, 5.5), 2.8, 3, boxstyle="round,pad=0.05",
                          edgecolor='#0e7c86', facecolor='#f2f8f8', linewidth=1.5)
    ax.add_patch(tbl3)
    ax.text(8.3, 8.2, 'admissions', fontsize=10, weight='bold', ha='center')
    admissions_cols = [
        "admission_id (PK)",
        "patient_id (FK)",
        "admission_date",
        "specialty"
    ]
    for i, col in enumerate(admissions_cols):
        ax.text(7.1, 7.8-i*0.55, col, fontsize=8, family='monospace')
    
    # Arrows for FK relationships
    ax.arrow(2.8, 6.8, 0.5, 0, head_width=0.25, head_length=0.15, 
             fc='#005eb8', ec='#005eb8', linewidth=1.5)
    ax.arrow(6.3, 6.5, 0.4, 0, head_width=0.25, head_length=0.15,
             fc='#005eb8', ec='#005eb8', linewidth=1.5)
    
    ax.text(3.2, 6.5, 'FK', fontsize=7, weight='bold', color='#005eb8')
    ax.text(6.5, 6.2, 'FK', fontsize=7, weight='bold', color='#005eb8')
    
    # Legend
    legend_y = 4.5
    ax.text(0.5, legend_y, '● PK = Primary Key (unique row identifier)', fontsize=8)
    ax.text(0.5, legend_y-0.4, '● FK = Foreign Key (reference to another table)', fontsize=8)
    ax.text(0.5, legend_y-0.8, '● Joins connect tables via FK→PK relationships', fontsize=8)
    
    save_fig("09_database_schema", fig)

# ============ 3. SQL SELECT clause anatomy (Lesson 12) ============
def gen_sql_select():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    
    ax.text(5, 7.5, 'SQL SELECT statement anatomy', ha='center', 
            fontsize=13, weight='bold')
    
    # Color-coded SQL
    sql = """SELECT   patient_id, admission_date, specialty
FROM     admissions
WHERE    admission_method = 'Emergency'
ORDER BY admission_date DESC;"""
    
    y = 6.8
    clauses = [
        ("SELECT", "Which columns?", "#005eb8"),
        ("FROM", "Which table?", "#0e7c86"),
        ("WHERE", "Which rows?", "#b35a00"),
        ("ORDER BY", "Sort how?", "#5b4b9e")
    ]
    
    for clause, desc, col in clauses:
        ax.text(0.8, y, clause, fontsize=10, weight='bold', family='monospace', color=col)
        ax.text(2.5, y, desc, fontsize=9, style='italic', color=col)
        y -= 1
    
    # Example
    ax.text(0.5, 1.8, 'Example result:', fontsize=9, weight='bold')
    result_box = FancyBboxPatch((0.3, 0.3), 9.4, 1.3, boxstyle="round,pad=0.05",
                                edgecolor='#dbe5e3', facecolor='#f5f8f7', linewidth=1)
    ax.add_patch(result_box)
    ax.text(0.7, 1.3, "patient_id | admission_date | specialty", 
            fontsize=8, family='monospace', weight='bold')
    ax.text(0.7, 0.95, "1042      | 2025-12-15     | Emergency", 
            fontsize=8, family='monospace')
    ax.text(0.7, 0.6, "1056      | 2025-12-10     | Respiratory", 
            fontsize=8, family='monospace')
    
    save_fig("12_sql_select", fig)

# ============ 4. JOIN types visual (Lesson 25) ============
def gen_joins():
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))
    fig.suptitle('SQL JOIN types', fontsize=13, weight='bold', y=0.98)
    
    for ax in axes: 
        ax.set_xlim(-1, 3); ax.set_ylim(-1, 3); ax.axis('off')
    
    # INNER JOIN
    ax = axes[0]
    ax.text(1, 2.7, 'INNER JOIN', fontsize=10, weight='bold', ha='center')
    circle1 = plt.Circle((0.6, 1.5), 0.6, color='#0e7c86', alpha=0.3, linewidth=2, 
                        edgecolor='#0e7c86')
    circle2 = plt.Circle((1.4, 1.5), 0.6, color='#005eb8', alpha=0.3, linewidth=2,
                        edgecolor='#005eb8')
    overlap = plt.Circle((1, 1.5), 0.3, color='#1e7a44', alpha=0.6)
    ax.add_patch(circle1); ax.add_patch(circle2); ax.add_patch(overlap)
    ax.text(1, 0.5, 'Only matching rows', fontsize=8, ha='center', style='italic')
    ax.text(0.6, 2.2, 'A', fontsize=9, weight='bold', ha='center')
    ax.text(1.4, 2.2, 'B', fontsize=9, weight='bold', ha='center')
    
    # LEFT JOIN
    ax = axes[1]
    ax.text(1, 2.7, 'LEFT JOIN', fontsize=10, weight='bold', ha='center')
    rect = FancyBboxPatch((-0.4, 0.9), 0.8, 1.2, boxstyle="round,pad=0.05",
                         color='#0e7c86', alpha=0.3, linewidth=2, edgecolor='#0e7c86')
    ax.add_patch(rect)
    circle3 = plt.Circle((1.2, 1.5), 0.6, color='#005eb8', alpha=0.3, linewidth=2,
                        edgecolor='#005eb8')
    ax.add_patch(circle3)
    ax.text(0, 2.2, 'A', fontsize=9, weight='bold', ha='center')
    ax.text(1.2, 2.2, 'B', fontsize=9, weight='bold', ha='center')
    ax.text(1, 0.2, 'All A rows,\nmatching B', fontsize=8, ha='center', style='italic')
    
    # RIGHT JOIN
    ax = axes[2]
    ax.text(1, 2.7, 'RIGHT JOIN', fontsize=10, weight='bold', ha='center')
    circle4 = plt.Circle((0.6, 1.5), 0.6, color='#0e7c86', alpha=0.3, linewidth=2,
                        edgecolor='#0e7c86')
    rect2 = FancyBboxPatch((0.8, 0.9), 0.8, 1.2, boxstyle="round,pad=0.05",
                          color='#005eb8', alpha=0.3, linewidth=2, edgecolor='#005eb8')
    ax.add_patch(circle4); ax.add_patch(rect2)
    ax.text(0.6, 2.2, 'A', fontsize=9, weight='bold', ha='center')
    ax.text(1.2, 2.2, 'B', fontsize=9, weight='bold', ha='center')
    ax.text(1, 0.2, 'Matching A,\nall B rows', fontsize=8, ha='center', style='italic')
    
    plt.tight_layout()
    save_fig("25_joins", fig)

# ============ 5. R data structures (Lesson 46) ============
def gen_r_structures():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    
    ax.text(5, 9.5, 'R data structures', ha='center', fontsize=13, weight='bold')
    
    structures = [
        ("Vector", "c(1, 2, 3)\nOne type only", 1, 7),
        ("List", "list(1, 'a', TRUE)\nMixed types", 5, 7),
        ("Data frame", "data.frame(\n  x=1:3,\n  y=c('a','b','c'))\nLike a table", 1, 4),
        ("Matrix", "matrix(1:6, nrow=2)\nNumeric grid", 5, 4),
    ]
    
    colors = ['#eef4fb', '#f2f8f8', '#f1eefa', '#fdf3e7']
    borders = ['#005eb8', '#0e7c86', '#5b4b9e', '#b35a00']
    
    for i, (name, desc, x, y) in enumerate(structures):
        box = FancyBboxPatch((x-0.9, y-1.4), 1.8, 2.2, boxstyle="round,pad=0.08",
                            edgecolor=borders[i], facecolor=colors[i], linewidth=2)
        ax.add_patch(box)
        ax.text(x, y+0.5, name, fontsize=10, weight='bold', ha='center', color=borders[i])
        ax.text(x, y-0.4, desc, fontsize=7.5, ha='center', family='monospace')
    
    save_fig("46_r_structures", fig)

# ============ 6. ggplot2 layers (Lesson 56) ============
def gen_ggplot_layers():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    
    ax.text(5, 9.5, 'ggplot2: layered grammar of graphics', ha='center',
            fontsize=13, weight='bold')
    
    layers = [
        ("Data", "data frame", "#eef4fb", "#005eb8", 8.5),
        ("Aesthetics", "aes(x, y, color)", "#f2f8f8", "#0e7c86", 7.2),
        ("Geometry", "geom_point(), geom_line()", "#f1eefa", "#5b4b9e", 5.9),
        ("Facets", "facet_wrap(~variable)", "#fdf3e7", "#b35a00", 4.6),
        ("Statistics", "stat_summary(), trend lines", "#e8f2f3", "#1e7a44", 3.3),
        ("Theme", "theme_minimal(), colors", "#fef5f1", "#c05541", 2.0),
    ]
    
    for name, desc, bg, border, y in layers:
        box = FancyBboxPatch((1.5, y-0.45), 7, 0.8, boxstyle="round,pad=0.06",
                            edgecolor=border, facecolor=bg, linewidth=1.5)
        ax.add_patch(box)
        ax.text(2, y-0.05, name, fontsize=9, weight='bold', color=border)
        ax.text(5, y-0.05, desc, fontsize=8, family='monospace', style='italic')
        
        if y > 2:
            ax.arrow(5, y-0.55, 0, -0.25, head_width=0.2, head_length=0.1,
                    fc='#9db9bd', ec='#9db9bd', linewidth=1)
    
    save_fig("56_ggplot_layers", fig)

# ============ 7. Reproducible pipeline (Lesson 83) ============
def gen_pipeline():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')
    
    ax.text(5, 5.5, 'Reproducible Analytical Pipeline (RAP)', ha='center',
            fontsize=13, weight='bold')
    
    steps = [
        ("Extract", "DBI/SQL pull\nfrom warehouse", 1, "#005eb8"),
        ("Clean", "dplyr, janitor\nstandardise", 2.5, "#0e7c86"),
        ("Analyse", "stats, models,\naggregates", 4, "#5b4b9e"),
        ("Report", "Quarto render\nHTML/PDF", 5.5, "#b35a00"),
        ("Publish", "GH pages,\nemail", 7, "#1e7a44"),
    ]
    
    for name, desc, x, col in steps:
        box = FancyBboxPatch((x-0.55, 2), 1.1, 2, boxstyle="round,pad=0.08",
                            edgecolor=col, facecolor='white', linewidth=2)
        ax.add_patch(box)
        ax.text(x, 3.5, name, fontsize=9, weight='bold', ha='center', color=col)
        ax.text(x, 2.8, desc, fontsize=7, ha='center', family='monospace')
        
        if x < 6.5:
            ax.arrow(x+0.65, 3, 0.6, 0, head_width=0.25, head_length=0.15,
                    fc='#9db9bd', ec='#9db9bd', linewidth=1.5)
    
    # Loop back
    ax.annotate('', xy=(0.6, 3), xytext=(7.5, 3),
                arrowprops=dict(arrowstyle='<-', lw=1.5, color='#9db9bd',
                              connectionstyle="arc3,rad=-.6"))
    ax.text(4, 0.7, 'Every month: re-run steps 1-4 = fresh outputs from unchanged code',
            ha='center', fontsize=8, style='italic')
    
    save_fig("83_pipeline", fig)

# ============ 8. Git workflow (Lesson 85) ============
def gen_git_workflow():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    
    ax.text(5, 7.5, 'Git & GitHub workflow', ha='center', fontsize=13, weight='bold')
    
    # Timeline
    timeline_y = 5.5
    stages = [
        ("1. Create\nbranch", 1.5, "#0e7c86"),
        ("2. Commit\nchanges", 3.5, "#005eb8"),
        ("3. Push to\nGitHub", 5.5, "#5b4b9e"),
        ("4. Open\nPull Request", 7.5, "#b35a00"),
        ("5. Merge\nto main", 9, "#1e7a44"),
    ]
    
    for label, x, col in stages:
        circle = plt.Circle((x, timeline_y), 0.35, color=col, alpha=0.8, linewidth=2,
                           edgecolor=col)
        ax.add_patch(circle)
        ax.text(x, timeline_y-1, label, fontsize=8, ha='center', weight='bold')
        
        if x < 8.5:
            ax.arrow(x+0.45, timeline_y, 1.5, 0, head_width=0.2, head_length=0.15,
                    fc='#9db9bd', ec='#9db9bd', linewidth=1.2)
    
    # Audit trail box
    box = FancyBboxPatch((0.3, 1.8), 9.4, 1.5, boxstyle="round,pad=0.08",
                        edgecolor='#005eb8', facecolor='#eef4fb', linewidth=1.5)
    ax.add_patch(box)
    ax.text(5, 3, 'Audit trail: Every change has a commit message + review', 
            ha='center', fontsize=9, weight='bold')
    ax.text(5, 2.4, 'Code is traced; nothing merges without peer eyes; rollback is instant.',
            ha='center', fontsize=8, style='italic')
    
    save_fig("85_git_workflow", fig)

# ============ 9. Statistics concepts (Lesson 69) ============
def gen_stats_concepts():
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    fig.suptitle('Key statistical concepts', fontsize=13, weight='bold')
    
    # Mean, SD, CI
    ax = axes[0, 0]
    x = np.linspace(0, 100, 1000)
    y = 1/np.sqrt(2*np.pi*15**2) * np.exp(-0.5*((x-50)/15)**2)
    ax.fill_between(x, y, alpha=0.3, color='#005eb8')
    ax.axvline(50, color='#005eb8', linestyle='--', linewidth=2, label='Mean')
    ax.axvline(50-1.96*15, color='#b35a00', linestyle=':', linewidth=1.5, label='95% CI')
    ax.axvline(50+1.96*15, color='#b35a00', linestyle=':', linewidth=1.5)
    ax.set_title('Normal distribution & CI', fontsize=9, weight='bold')
    ax.set_xlabel('Value', fontsize=8); ax.set_ylabel('Density', fontsize=8)
    ax.legend(fontsize=7, loc='upper right'); ax.grid(True, alpha=0.2)
    
    # Confidence intervals
    ax = axes[0, 1]
    ests = [45, 52, 48, 55, 50, 49, 51, 47]
    cis_lower = [40, 47, 43, 50, 45, 44, 46, 42]
    cis_upper = [50, 57, 53, 60, 55, 54, 56, 52]
    for i, (est, lo, hi) in enumerate(zip(ests, cis_lower, cis_upper)):
        ax.plot([lo, hi], [i, i], 'o-', color='#0e7c86', linewidth=1.5, markersize=4)
        ax.plot(est, i, 'o', color='#005eb8', markersize=6)
    ax.axvline(50, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_title('8 studies: CI bands around point est.', fontsize=9, weight='bold')
    ax.set_xlabel('Estimate ± 95% CI', fontsize=8); ax.set_ylabel('Study', fontsize=8)
    ax.grid(True, alpha=0.2, axis='x')
    
    # P-value intuition
    ax = axes[1, 0]
    x = np.linspace(-4, 4, 1000)
    y_h0 = 1/np.sqrt(2*np.pi) * np.exp(-0.5*x**2)
    ax.fill_between(x[x > 2], y_h0[x > 2], alpha=0.3, color='#b35a00', label='p<0.05')
    ax.plot(x, y_h0, color='#0e7c86', linewidth=2, label='H₀: no difference')
    ax.axvline(2, color='#b35a00', linestyle=':', linewidth=1.5)
    ax.text(2.5, 0.15, 'p<0.05', fontsize=8, color='#b35a00', weight='bold')
    ax.set_title('P-value: evidence against H₀', fontsize=9, weight='bold')
    ax.set_xlabel('Test statistic (SD)', fontsize=8); ax.set_ylabel('Density', fontsize=8)
    ax.legend(fontsize=7); ax.grid(True, alpha=0.2)
    
    # Effect sizes
    ax = axes[1, 1]
    categories = ['Small\n(d=0.2)', 'Medium\n(d=0.5)', 'Large\n(d=0.8)']
    effect_sizes = [0.2, 0.5, 0.8]
    colors_es = ['#dbe5e3', '#9db9bd', '#0e7c86']
    bars = ax.bar(categories, effect_sizes, color=colors_es, edgecolor='#0e7c86', linewidth=1.5)
    ax.set_ylabel("Cohen's d", fontsize=8)
    ax.set_title('Effect size interpretation', fontsize=9, weight='bold')
    ax.set_ylim(0, 1); ax.grid(True, alpha=0.2, axis='y')
    
    plt.tight_layout()
    save_fig("69_stats", fig)

# ============ 10. Readmissions analysis (Capstone A) ============
def gen_capstone_a():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis('off')
    
    ax.text(6, 9.5, 'Capstone A: 30-day emergency readmissions', ha='center',
            fontsize=12, weight='bold')
    
    # Timeline
    ax.text(1, 8.5, 'Index admission', fontsize=9, weight='bold', color='#005eb8')
    ax.add_patch(plt.Rectangle((0.7, 7.8), 0.6, 0.4, facecolor='#005eb8', edgecolor='#005eb8'))
    
    ax.text(6, 8.5, '30-day window', fontsize=9, weight='bold', color='#b35a00')
    ax.arrow(1.5, 8, 4, 0, head_width=0.2, head_length=0.3, fc='#b35a00', ec='#b35a00')
    ax.text(3.5, 7.5, 'Readmitted = 1', fontsize=8, ha='center', color='#1e7a44')
    ax.text(3.5, 7, 'Not readmitted = 0', fontsize=8, ha='center', color='#9db9bd')
    
    ax.text(10, 8.5, 'End of window', fontsize=9, weight='bold', color='#0e7c86')
    ax.add_patch(plt.Rectangle((9.7, 7.8), 0.6, 0.4, facecolor='#0e7c86', edgecolor='#0e7c86'))
    
    # Metrics
    metrics = [
        ("Eligible discharges", "275", "#005eb8"),
        ("Readmitted", "70 (25.5%)", "#b35a00"),
        ("Not readmitted", "205 (74.5%)", "#9db9bd"),
        ("Rate by specialty", "varies 15–35%", "#0e7c86"),
    ]
    
    y_pos = 6.5
    for metric, value, col in metrics:
        ax.text(1.5, y_pos, metric, fontsize=9, weight='bold')
        ax.text(5, y_pos, value, fontsize=9, family='monospace', color=col, weight='bold')
        y_pos -= 1
    
    # Bottom note
    ax.text(6, 1.5, 'Key: exclude deaths without readmission (no opportunity to return)',
            ha='center', fontsize=8, style='italic',
            bbox=dict(boxstyle='round', facecolor='#fdf3e7', alpha=0.7))
    
    save_fig("capstone_a", fig)

# ============ 11. MMR uptake by deprivation (Capstone B) ============
def gen_capstone_b():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    deciles = np.arange(1, 11)
    uptake = [0.25 + 0.025*d for d in deciles]  # gradient by deprivation
    
    colors_grad = plt.cm.RdYlGn(np.linspace(0.3, 0.9, 10))
    bars = ax.bar(deciles, uptake, color=colors_grad, edgecolor='#0e7c86', linewidth=1.5)
    
    ax.set_xlabel('IMD decile (1=most deprived, 10=least deprived)', fontsize=9, weight='bold')
    ax.set_ylabel('MMR dose 2 uptake by age 2', fontsize=9, weight='bold')
    ax.set_title('Capstone B: Vaccination equity (gradient analysis)', fontsize=12, weight='bold')
    ax.set_ylim(0, 1); ax.set_xticks(deciles)
    ax.grid(True, alpha=0.2, axis='y')
    
    # Annotate
    ax.text(1, 0.15, 'Low uptake\nin deprived areas', fontsize=8, style='italic', color='#b35a00')
    ax.text(9, 0.75, 'Higher uptake\nin affluent areas', fontsize=8, style='italic', color='#1e7a44')
    
    plt.tight_layout()
    save_fig("capstone_b", fig)

# ============ Run all ============
print("Generating diagrams...")
gen_filesystem()
gen_database_schema()
gen_sql_select()
gen_joins()
gen_r_structures()
gen_ggplot_layers()
gen_pipeline()
gen_git_workflow()
gen_stats_concepts()
gen_capstone_a()
gen_capstone_b()
print(f"\nAll diagrams saved to {OUTDIR}")
