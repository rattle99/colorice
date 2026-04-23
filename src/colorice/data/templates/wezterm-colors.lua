-- colorice theme — generated from {wallpaper}
-- Usage: in your wezterm.lua:
--   local colorice = require("colorice-colors")
--   config.colors = colorice.colors

local M = {{}}

M.colors = {{
  foreground    = "{foreground}",
  background    = "{background}",
  cursor_bg     = "{cursor}",
  cursor_fg     = "{background}",
  cursor_border = "{cursor}",
  selection_fg  = "{foreground}",
  selection_bg  = "{color8}",

  ansi = {{
    "{color0}",   -- black
    "{color1}",   -- red
    "{color2}",   -- green
    "{color3}",   -- yellow
    "{color4}",   -- blue
    "{color5}",   -- magenta
    "{color6}",   -- cyan
    "{color7}",   -- white
  }},

  brights = {{
    "{color8}",   -- bright black
    "{color9}",   -- bright red
    "{color10}",  -- bright green
    "{color11}",  -- bright yellow
    "{color12}",  -- bright blue
    "{color13}",  -- bright magenta
    "{color14}",  -- bright cyan
    "{color15}",  -- bright white
  }},

  tab_bar = {{
    background = "{background}",
    active_tab = {{
      bg_color  = "{color8}",
      fg_color  = "{foreground}",
    }},
    inactive_tab = {{
      bg_color  = "{background}",
      fg_color  = "{color8}",
    }},
    inactive_tab_hover = {{
      bg_color  = "{color8}",
      fg_color  = "{foreground}",
    }},
    new_tab = {{
      bg_color  = "{background}",
      fg_color  = "{color8}",
    }},
  }},
}}

return M
