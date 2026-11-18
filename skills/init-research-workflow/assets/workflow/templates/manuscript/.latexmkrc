# Run latexmk from manuscript/. Explicit filenames override this default.
@default_files = ('{{ PROJECT_SLUG }}.tex');
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$aux_dir = 'aux';
$out_dir = 'out';
# TeX Live needs emulation for separate aux/output directories; works on MiKTeX too.
$emulate_aux = 1;
$do_cd = 0;
