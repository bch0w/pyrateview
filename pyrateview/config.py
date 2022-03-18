"""
The PyrateView Configuration file.
"""
title = "Vs [km/s]"

# Movie
mov_bounds = [-1e-4, 1e-4]
mov_scale = 4.

# Data and coordinate scaling
scale_data = 1E-3
scale_coords = 1E-3
zero_origin = False # True

# Colormap
cmap = "Rainbow Desaturated"
invert_cmap = True
center_cmap = True

# Colorbar
cbar = True
cbar_position = [.3, .1]
cbar_orientation = "Horizontal"
title_justification = "Left"
text_position = "top"
label_format = "%.2f"
round_label = False
num_labels = 3
num_values = 33
use_above_range = False
use_below_range = False
cbar_thickness = 35
cbar_length = 0.15

# Global parameters
fontcolor = "k"
linecolor = "k"
fontsize = 50
resolution = [2100, 2100]
