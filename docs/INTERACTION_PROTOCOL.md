# Interactive adjustment protocol

## Structural operations
- merge_sections
- split_section
- merge_nodes
- reorder_nodes
- hide_node
- promote_node
- demote_node
- set_two_layer_parent

## Visual operations
- set_mode
- set_palette
- set_density
- set_typography_scale
- set_spacing_scale
- set_language
- set_aspect_ratio

## Content operations
- shorten_copy(percent)
- rewrite_title
- rewrite_subtitle
- add_verified_fact
- remove_unverified_fact

Every structural or content operation should trigger:
`spec update → layout → QA → auto-fix → render → export`.
