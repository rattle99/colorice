-- colorice theme — generated from {wallpaper}
-- Usage: place in ~/.config/nvim/colors/colorice.lua
-- then run :colorscheme colorice  or add  vim.cmd("colorscheme colorice")  to init.lua

vim.cmd("highlight clear")
vim.g.colors_name = "colorice"

local c = {{
  bg       = "{background}",
  fg       = "{foreground}",
  cursor   = "{cursor}",
  black    = "{color0}",
  red      = "{color1}",
  green    = "{color2}",
  yellow   = "{color3}",
  blue     = "{color4}",
  magenta  = "{color5}",
  cyan     = "{color6}",
  white    = "{color7}",
  br_black = "{color8}",
  br_red   = "{color9}",
  br_green = "{color10}",
  br_yellow= "{color11}",
  br_blue  = "{color12}",
  br_mag   = "{color13}",
  br_cyan  = "{color14}",
  br_white = "{color15}",
}}

local function hi(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

-- Base
hi("Normal",       {{ fg = c.fg,       bg = c.bg }})
hi("NormalFloat",  {{ fg = c.fg,       bg = c.br_black }})
hi("Visual",       {{ bg = c.br_black }})
hi("CursorLine",   {{ bg = c.br_black }})
hi("CursorLineNr", {{ fg = c.yellow,   bold = true }})
hi("LineNr",       {{ fg = c.br_black }})
hi("SignColumn",   {{ bg = c.bg }})
hi("StatusLine",   {{ fg = c.fg,       bg = c.br_black }})
hi("StatusLineNC", {{ fg = c.br_black, bg = c.bg }})
hi("VertSplit",    {{ fg = c.br_black }})
hi("Pmenu",        {{ fg = c.fg,       bg = c.br_black }})
hi("PmenuSel",     {{ fg = c.bg,       bg = c.blue }})
hi("Search",       {{ fg = c.bg,       bg = c.yellow }})
hi("IncSearch",    {{ fg = c.bg,       bg = c.cursor }})
hi("MatchParen",   {{ fg = c.yellow,   bold = true }})

-- Syntax
hi("Comment",      {{ fg = c.br_black, italic = true }})
hi("Constant",     {{ fg = c.cyan }})
hi("String",       {{ fg = c.green }})
hi("Number",       {{ fg = c.magenta }})
hi("Boolean",      {{ fg = c.magenta }})
hi("Identifier",   {{ fg = c.fg }})
hi("Function",     {{ fg = c.blue }})
hi("Keyword",      {{ fg = c.red }})
hi("Operator",     {{ fg = c.cyan }})
hi("Type",         {{ fg = c.yellow }})
hi("Special",      {{ fg = c.magenta }})
hi("PreProc",      {{ fg = c.magenta }})
hi("Todo",         {{ fg = c.yellow,   bold = true }})
hi("Error",        {{ fg = c.red,      bold = true }})
hi("Warning",      {{ fg = c.yellow }})

-- Diagnostic
hi("DiagnosticError", {{ fg = c.red }})
hi("DiagnosticWarn",  {{ fg = c.yellow }})
hi("DiagnosticInfo",  {{ fg = c.blue }})
hi("DiagnosticHint",  {{ fg = c.cyan }})
