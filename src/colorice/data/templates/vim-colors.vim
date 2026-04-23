" colorice theme — generated from {wallpaper}
" Usage: place in ~/.vim/colors/colorice.vim
" then add `colorscheme colorice` to ~/.vimrc

highlight clear
if exists("syntax_on")
  syntax reset
endif
let g:colors_name = "colorice"

" Color definitions
let s:bg       = "{background}"
let s:fg       = "{foreground}"
let s:cursor   = "{cursor}"
let s:black    = "{color0}"
let s:red      = "{color1}"
let s:green    = "{color2}"
let s:yellow   = "{color3}"
let s:blue     = "{color4}"
let s:magenta  = "{color5}"
let s:cyan     = "{color6}"
let s:white    = "{color7}"
let s:br_black = "{color8}"

" Base
execute "highlight Normal       guifg=" . s:fg       . " guibg=" . s:bg
execute "highlight Visual                              guibg=" . s:br_black
execute "highlight CursorLine                          guibg=" . s:br_black
execute "highlight CursorLineNr guifg=" . s:yellow   . " gui=bold"
execute "highlight LineNr       guifg=" . s:br_black
execute "highlight StatusLine   guifg=" . s:fg       . " guibg=" . s:br_black
execute "highlight VertSplit    guifg=" . s:br_black
execute "highlight Pmenu        guifg=" . s:fg       . " guibg=" . s:br_black
execute "highlight PmenuSel     guifg=" . s:bg       . " guibg=" . s:blue
execute "highlight Search       guifg=" . s:bg       . " guibg=" . s:yellow
execute "highlight MatchParen   guifg=" . s:yellow   . " gui=bold"

" Syntax
execute "highlight Comment      guifg=" . s:br_black . " gui=italic"
execute "highlight Constant     guifg=" . s:cyan
execute "highlight String       guifg=" . s:green
execute "highlight Number       guifg=" . s:magenta
execute "highlight Identifier   guifg=" . s:fg
execute "highlight Function     guifg=" . s:blue
execute "highlight Keyword      guifg=" . s:red
execute "highlight Operator     guifg=" . s:cyan
execute "highlight Type         guifg=" . s:yellow
execute "highlight Special      guifg=" . s:magenta
execute "highlight PreProc      guifg=" . s:magenta
execute "highlight Todo         guifg=" . s:yellow   . " gui=bold"
execute "highlight Error        guifg=" . s:red      . " gui=bold"
