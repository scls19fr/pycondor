<Task type="RT" task_scored="1" aat_min_time="{{ settings_task.aat_min_time }}" start_max_speed="{{ settings_task.start_max_speed }}"
  start_min_height="{{ settings_task.start_min_height }}" start_min_height_ref="{{ settings_task.start_min_height_ref }}"
  start_max_height="{{ settings_task.start_max_height }}" start_max_height_ref="{{ settings_task.start_max_height_ref }}"
  finish_min_height="{{ settings_task.finish_min_height }}"
  fai_finish="0" min_points="{{ nb_wpts-1 }}"
  max_points="10" homogeneous_tps="0" is_closed="{{ is_closed }}">
{% for id, tp in df_task.iterrows() %}
	<Point type="{{ tp.Type }}">
		<Waypoint altitude="{{ tp.Altitude }}" comment="{{ tp.Comment }}" id="{{ id }}" name="{{ tp.Name }}">
			<Location latitude="{{ tp.Lat }}" longitude="{{ tp.Lon }}"/>
		</Waypoint>
		<ObservationZone radius="{{ tp.ObservationZone.Radius }}" type="{{ tp.ObservationZone.Type }}"/>
	</Point>
{% endfor %}
</Task>