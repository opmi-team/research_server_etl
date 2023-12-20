from typing import Dict, Any, List
from dataclasses import dataclass, field

import polars


@dataclass
class GTFSSchema:
    """describe GTFS tables"""

    table_name: str
    schema: Dict[str, Any]
    primary_keys: List[str]
    to_date_fields: List[str] = field(default_factory=list)


agency_schema = {
    "agency_id": str,
    "agency_name": str,
    "agency_url": str,
    "agency_timezone": str,
    "agency_lang": str,
    "agency_phone": str,
}

calendar_schema = {
    "service_id": str,
    "monday": polars.Int16,
    "tuesday": polars.Int16,
    "wednesday": polars.Int16,
    "thursday": polars.Int16,
    "friday": polars.Int16,
    "saturday": polars.Int16,
    "sunday": polars.Int16,
    "start_date": str,  # convert to Date
    "end_date": str,  # convert to Date
}

calendar_attributes_schema = {
    "service_id": str,
    "service_description": str,
    "service_schedule_name": str,
    "service_schedule_type": str,
    "service_schedule_typicality": polars.Int64,
    # "rating_start_date": str, # Not Used
    # "rating_end_date": str, # Not Used
    # "rating_description": str, # Not Used
}

calendar_dates_schema = {
    "service_id": str,
    "date": str,  # convert to Date
    "exception_type": polars.Int16,
    "holiday_name": str,
}

checkpoints_schema = {
    "checkpoint_id": str,
    "checkpoint_name": str,
}

directions_schema = {
    "route_id": str,
    "direction_id": polars.Int16,
    "direction": str,
    "direction_destination": str,
}

facilities_schema = {
    "facility_id": str,
    "facility_code": str,
    "facility_class": polars.Int16,
    "facility_type": str,
    "stop_id": str,
    "facility_short_name": str,
    "facility_long_name": str,
    "facility_desc": str,
    "facility_lat": polars.Float64,
    "facility_lon": polars.Float64,
    "wheelchair_facility": polars.Int16,
}


facilities_properties_schema = {
    "facility_id": str,
    "property_id": str,
    "value": str,
}

# Not Used
# facilities_properties_definitions_schema = {
#     "property_id": str,
#     "definition": str,
#     "possible_values": str,
# }

# Not Used
# fare_leg_rules_schema = {
#     "leg_group_id": str,
#     "network_id": str,
#     "from_area_id": str,
#     "to_area_id": str,
#     "fare_product_id": str,
#     "from_timeframe_group_id": str,
#     "to_timeframe_group_id": str,
#     "transfer_only": str,
# }

# Not Used
# fare_media_schema = {
#     "fare_media_id": str,
#     "fare_media_name": str,
#     "fare_media_type": str,
# }

# Not Used
# fare_products_schema = {
#     "fare_product_id": str,
#     "fare_product_name": str,
#     "fare_media_id": str,
#     "amount": str,
#     "currency": str,
# }

# Not Used
# fare_transfer_rules_schema = {
#     "from_leg_group_id": str,
#     "to_leg_group_id": str,
#     "transfer_count": str,
#     "duration_limit": str,
#     "duration_limit_type": str,
#     "fare_transfer_type": str,
#     "fare_product_id": str,
# }

feed_info_schema = {
    "feed_publisher_name": str,
    "feed_publisher_url": str,
    "feed_lang": str,
    "feed_start_date": str,
    "feed_end_date": str,
    "feed_version": str,
    "feed_contact_email": str,
    # "feed_id": str, # Not Used
}

levels_schema = {
    "level_id": str,
    "level_index": polars.Float64,
    "level_name": str,
    "level_elevation": str,
}

lines_schema = {
    "line_id": str,
    "line_short_name": str,
    "line_long_name": str,
    "line_desc": str,
    "line_url": str,
    "line_color": str,
    "line_text_color": str,
    "line_sort_order": polars.Int64,
}

# Not Used
# linked_datasets_schema = {
#     "url": str,
#     "trip_updates": str,
#     "vehicle_positions": str,
#     "service_alerts": str,
#     "authentication_type": str,
# }

multi_route_trips_schema = {
    "added_route_id": str,
    "trip_id": str,
}

pathways_schema = {
    "pathway_id": str,
    "from_stop_id": str,
    "to_stop_id": str,
    "facility_id": str,
    "pathway_mode": polars.Int64,
    # "pathway_type": polars.Int64, # Not in files?
    # "is_bidirectional": str,
    # "length": str,
    # "wheelchair_length": str,
    "traversal_time": polars.Int64,
    "wheelchair_traversal_time": polars.Int64,
    # "ramp_slope": polars.Int64, # Not in files?
    "stair_count": polars.Int64,
    # "max_slope": str,
    "pathway_name": str,
    "pathway_code": str,
    "signposted_as": str,
    "instructions": str,
}

route_patterns_schema = {
    "route_pattern_id": str,
    "route_id": str,
    "direction_id": polars.Int16,
    "route_pattern_name": str,
    "route_pattern_time_desc": str,
    "route_pattern_typicality": polars.Int16,
    "route_pattern_sort_order": polars.Int64,
    "representative_trip_id": str,
    # "canonical_route_pattern": str, # Not Used
}

routes_schema = {
    "route_id": str,
    "agency_id": str,
    "route_short_name": str,
    "route_long_name": str,
    "route_desc": str,
    "route_type": polars.Int64,
    "route_url": str,
    "route_color": str,
    "route_text_color": str,
    "route_sort_order": polars.Int64,
    "route_fare_class": str,
    "line_id": str,
    "listed_route": str,
    # "network_id": str, # Not Used
}

shapes_schema = {
    "shape_id": str,
    "shape_pt_lat": polars.Float64,
    "shape_pt_lon": polars.Float64,
    "shape_pt_sequence": polars.Int64,
    "shape_dist_traveled": polars.Float64,
}

# Not Used
# stop_areas_schema = {
#     "stop_id": str,
#     "area_id": str,
# }

stop_times_schema = {
    "trip_id": str,
    "arrival_time": str,
    "departure_time": str,
    "stop_id": str,
    "stop_sequence": polars.Int64,
    "stop_headsign": str,
    "pickup_type": polars.Int64,
    "drop_off_type": polars.Int64,
    "timepoint": polars.Int64,
    "checkpoint_id": str,
    # "continuous_pickup": str, # Not Used
    # "continuous_drop_off": str, # Not Used
}

stops_schema = {
    "stop_id": str,
    "stop_code": str,
    "stop_name": str,
    "stop_desc": str,
    # "platform_code": str, # Not Used
    # "platform_name": str, # Not Used
    "stop_lat": polars.Float64,
    "stop_lon": polars.Float64,
    "zone_id": str,
    "stop_address": str,
    "stop_url": str,
    "level_id": str,
    "location_type": polars.Int64,
    "parent_station": str,
    # "stop_timezone": str, # Not In File
    "wheelchair_boarding": polars.Int64,
    # "municipality": str, # Not Used
    # "on_street": str, # Not Used
    # "at_street": str, # Not Used
    # "vehicle_type": str, # Not Used
}

transfers_schema = {
    "from_stop_id": str,
    "to_stop_id": str,
    "transfer_type": polars.Int64,
    "min_transfer_time": polars.Int64,
    "min_walk_time": polars.Int64,
    "min_wheelchair_time": polars.Int64,
    "suggested_buffer_time": polars.Int64,
    "wheelchair_transfer": polars.Int64,
    "from_trip_id": str,  # Not Used - Added for primary key
    "to_trip_id": str,  # Not Used - Added for primary key
}

trips_schema = {
    "route_id": str,
    "service_id": str,
    "trip_id": str,
    "trip_headsign": str,
    "trip_short_name": str,
    "direction_id": polars.Int16,
    "block_id": str,
    "shape_id": str,
    "wheelchair_accessible": polars.Int16,
    "trip_route_type": polars.Int64,
    "route_pattern_id": str,
    "bikes_allowed": polars.Int16,
}

# Not Used
# trips_properties_schema = {
#     "trip_id": str,
#     "trip_property_id": str,
#     "value": str,
# }

# Not Used
# trips_properties_definitions_schema = {
#     "trip_property_id": str,
#     "definition": str,
#     "possible_values": str,
# }
