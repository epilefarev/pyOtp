import keplergl

kepler_map = keplergl.KeplerGl(height=400)
kepler_map.save_to_html(file_name='earthquake.html')