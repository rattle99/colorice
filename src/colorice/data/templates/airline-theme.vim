" colorice airline theme — generated from {wallpaper}
" Usage: place in ~/.config/vim/autoload/airline/themes/colorice.vim
" then set g:airline_theme = 'colorice' in vimrc

let g:airline#themes#colorice#palette = {}

" UI accent tones — derived from palette
let s:bg       = "{background}"
let s:fg       = "{foreground}"
let s:accent   = "{color4}"
let s:insert   = "{color2}"
let s:visual   = "{color5}"
let s:replace  = "{color1}"
let s:command  = "{color3}"
let s:terminal = "{color6}"
let s:white    = "{color7}"
let s:mid_bg   = "{color8.darken_25}"
let s:mid_fg   = "{color8.darken_15}"
let s:dark_bg  = "{background.darken_5}"
let s:line_bg  = "{background.lighten_8}"

" Normal mode — accent (blue/purple)
let s:N1 = [s:bg,    s:accent,  0, 0]
let s:N2 = [s:fg,    s:mid_bg,  0, 0]
let s:N3 = [s:accent,s:line_bg, 0, 0]
let g:airline#themes#colorice#palette.normal = airline#themes#generate_color_map(s:N1, s:N2, s:N3)

" Insert mode — green accent
let s:I1 = [s:bg,    s:insert,  0, 0]
let s:I2 = [s:white, s:mid_bg,  0, 0]
let s:I3 = [s:insert,s:line_bg, 0, 0]
let g:airline#themes#colorice#palette.insert = airline#themes#generate_color_map(s:I1, s:I2, s:I3)

" Visual mode — magenta accent
let s:V1 = [s:bg,    s:visual,  0, 0]
let s:V2 = [s:white, s:mid_bg,  0, 0]
let s:V3 = [s:visual,s:line_bg, 0, 0]
let g:airline#themes#colorice#palette.visual = airline#themes#generate_color_map(s:V1, s:V2, s:V3)

" Replace mode — red accent
let s:R1 = [s:bg,     s:replace, 0, 0]
let s:R2 = [s:white,  s:mid_bg,  0, 0]
let s:R3 = [s:replace,s:line_bg, 0, 0]
let g:airline#themes#colorice#palette.replace = airline#themes#generate_color_map(s:R1, s:R2, s:R3)

" Command mode — yellow accent
let s:C1 = [s:bg,     s:command, 0, 0]
let s:C2 = [s:fg,     s:mid_bg,  0, 0]
let s:C3 = [s:command,s:line_bg, 0, 0]
let g:airline#themes#colorice#palette.commandline = airline#themes#generate_color_map(s:C1, s:C2, s:C3)

" Terminal mode — cyan accent
let s:T1 = [s:bg,      s:terminal, 0, 0]
let s:T2 = [s:white,   s:mid_bg,   0, 0]
let s:T3 = [s:terminal,s:line_bg,  0, 0]
let g:airline#themes#colorice#palette.terminal = airline#themes#generate_color_map(s:T1, s:T2, s:T3)

" Inactive window
let s:IA = [s:mid_fg, s:dark_bg, 0, 0]
let g:airline#themes#colorice#palette.inactive = airline#themes#generate_color_map(s:IA, s:IA, s:IA)

" Warning and error sections
let g:airline#themes#colorice#palette.normal.airline_warning  = [s:bg, s:visual,  0, 0]
let g:airline#themes#colorice#palette.normal.airline_error    = [s:bg, s:insert,  0, 0]
let g:airline#themes#colorice#palette.insert.airline_warning  = [s:bg, s:visual,  0, 0]
let g:airline#themes#colorice#palette.insert.airline_error    = [s:bg, s:insert,  0, 0]
let g:airline#themes#colorice#palette.visual.airline_warning  = [s:bg, s:visual,  0, 0]
let g:airline#themes#colorice#palette.visual.airline_error    = [s:bg, s:insert,  0, 0]
