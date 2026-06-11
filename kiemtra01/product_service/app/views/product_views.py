import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import (
    ComputerProduct, MobileProduct, TabletProduct, SmartwatchProduct,
    HeadphoneProduct, CameraProduct, GamingConsoleProduct, TVProduct,
    SmartHomeProduct, FitnessTrackerProduct, DroneProduct
)

PRODUCT_MODELS = {
    'computers': ComputerProduct,
    'mobiles': MobileProduct,
    'tablets': TabletProduct,
    'smartwatches': SmartwatchProduct,
    'headphones': HeadphoneProduct,
    'cameras': CameraProduct,
    'gaming_consoles': GamingConsoleProduct,
    'tvs': TVProduct,
    'smart_homes': SmartHomeProduct,
    'fitness_trackers': FitnessTrackerProduct,
    'drones': DroneProduct,
}


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _model_to_dict(model, item):
    """Convert any product model to dictionary"""
    data = {
        "id": item.id,
        "name": item.name,
        "brand": item.brand,
        "price": float(item.price),
        "stock": item.stock,
        "description": item.description,
        "is_active": item.is_active,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }
    
    # Add model-specific fields
    if hasattr(item, 'cpu'):
        data["cpu"] = item.get_cpu_display() if hasattr(item, 'get_cpu_display') else item.cpu
    if hasattr(item, 'chipset'):
        data["chipset"] = item.get_chipset_display() if hasattr(item, 'get_chipset_display') else item.chipset
    if hasattr(item, 'gpu'):
        data["gpu"] = item.gpu
    if hasattr(item, 'ram_gb'):
        data["ram_gb"] = item.ram_gb
    if hasattr(item, 'storage_gb'):
        data["storage_gb"] = item.storage_gb
    if hasattr(item, 'storage_type'):
        data["storage_type"] = item.get_storage_type_display() if hasattr(item, 'get_storage_type_display') else item.storage_type
    if hasattr(item, 'display_size_inches'):
        data["display_size_inches"] = float(item.display_size_inches)
    if hasattr(item, 'display_resolution'):
        data["display_resolution"] = item.display_resolution
    if hasattr(item, 'refresh_rate_hz'):
        data["refresh_rate_hz"] = item.refresh_rate_hz
    if hasattr(item, 'operating_system'):
        data["operating_system"] = item.get_operating_system_display() if hasattr(item, 'get_operating_system_display') and item.operating_system else item.operating_system
    if hasattr(item, 'has_touchscreen'):
        data["has_touchscreen"] = item.has_touchscreen
    if hasattr(item, 'has_backlit_keyboard'):
        data["has_backlit_keyboard"] = item.has_backlit_keyboard
    if hasattr(item, 'has_fingerprint_reader'):
        data["has_fingerprint_reader"] = item.has_fingerprint_reader
    if hasattr(item, 'has_webcam'):
        data["has_webcam"] = item.has_webcam
    if hasattr(item, 'ports'):
        data["ports"] = item.ports
    if hasattr(item, 'warranty_months'):
        data["warranty_months"] = item.warranty_months
    if hasattr(item, 'main_camera_mp'):
        data["main_camera_mp"] = item.main_camera_mp
    if hasattr(item, 'front_camera_mp'):
        data["front_camera_mp"] = item.front_camera_mp
    if hasattr(item, 'battery_mah'):
        data["battery_mah"] = item.battery_mah
    if hasattr(item, 'battery_hours'):
        data["battery_hours"] = float(item.battery_hours) if item.battery_hours else None
    if hasattr(item, 'battery_days'):
        data["battery_days"] = float(item.battery_days)
    if hasattr(item, 'has_wifi'):
        data["has_wifi"] = item.has_wifi
    if hasattr(item, 'has_bluetooth'):
        data["has_bluetooth"] = item.has_bluetooth
    if hasattr(item, 'has_5g'):
        data["has_5g"] = item.has_5g
    if hasattr(item, 'has_nfc'):
        data["has_nfc"] = item.has_nfc
    if hasattr(item, 'has_wireless_charging'):
        data["has_wireless_charging"] = item.has_wireless_charging
    if hasattr(item, 'has_water_resistance'):
        data["has_water_resistance"] = item.has_water_resistance
    if hasattr(item, 'fast_charging_w'):
        data["fast_charging_w"] = item.fast_charging_w
    if hasattr(item, 'sim_type'):
        data["sim_type"] = item.get_sim_type_display() if hasattr(item, 'get_sim_type_display') else item.sim_type
    if hasattr(item, 'color_options'):
        data["color_options"] = item.color_options
    if hasattr(item, 'has_gps'):
        data["has_gps"] = item.has_gps
    if hasattr(item, 'megapixels'):
        data["megapixels"] = item.megapixels
    if hasattr(item, 'camera_type'):
        data["camera_type"] = item.get_camera_type_display() if hasattr(item, 'get_camera_type_display') else item.camera_type
    if hasattr(item, 'sensor_type'):
        data["sensor_type"] = item.get_sensor_type_display() if hasattr(item, 'get_sensor_type_display') else item.sensor_type
    if hasattr(item, 'iso_range'):
        data["iso_range"] = item.iso_range
    if hasattr(item, 'video_resolution'):
        data["video_resolution"] = item.video_resolution
    if hasattr(item, 'video_fps'):
        data["video_fps"] = item.video_fps
    if hasattr(item, 'has_image_stabilization'):
        data["has_image_stabilization"] = item.has_image_stabilization
    if hasattr(item, 'battery_shots'):
        data["battery_shots"] = item.battery_shots
    if hasattr(item, 'lens_mount'):
        data["lens_mount"] = item.lens_mount
    if hasattr(item, 'viewfinder_type'):
        data["viewfinder_type"] = item.viewfinder_type
    if hasattr(item, 'headphone_type'):
        data["headphone_type"] = item.get_headphone_type_display() if hasattr(item, 'get_headphone_type_display') else item.headphone_type
    if hasattr(item, 'is_wireless'):
        data["is_wireless"] = item.is_wireless
    if hasattr(item, 'has_noise_cancelling'):
        data["has_noise_cancelling"] = item.has_noise_cancelling
    if hasattr(item, 'has_microphone'):
        data["has_microphone"] = item.has_microphone
    if hasattr(item, 'charging_time_hours'):
        data["charging_time_hours"] = float(item.charging_time_hours) if item.charging_time_hours else None
    if hasattr(item, 'bluetooth_version'):
        data["bluetooth_version"] = item.bluetooth_version
    if hasattr(item, 'frequency_response'):
        data["frequency_response"] = item.frequency_response
    if hasattr(item, 'impedance_ohms'):
        data["impedance_ohms"] = item.impedance_ohms
    if hasattr(item, 'driver_size_mm'):
        data["driver_size_mm"] = item.driver_size_mm
    if hasattr(item, 'has_fast_charging'):
        data["has_fast_charging"] = item.has_fast_charging
    if hasattr(item, 'console_type'):
        data["console_type"] = item.get_console_type_display() if hasattr(item, 'get_console_type_display') else item.console_type
    if hasattr(item, 'display_type'):
        data["display_type"] = item.get_display_type_display() if hasattr(item, 'get_display_type_display') else item.display_type
    if hasattr(item, 'resolution'):
        data["resolution"] = item.get_resolution_display() if hasattr(item, 'get_resolution_display') else item.resolution
    if hasattr(item, 'has_smart_tv'):
        data["has_smart_tv"] = item.has_smart_tv
    if hasattr(item, 'has_hdr'):
        data["has_hdr"] = item.has_hdr
    if hasattr(item, 'hdr_format'):
        data["hdr_format"] = item.hdr_format
    if hasattr(item, 'has_dolby_vision'):
        data["has_dolby_vision"] = item.has_dolby_vision
    if hasattr(item, 'has_dolby_atmos'):
        data["has_dolby_atmos"] = item.has_dolby_atmos
    if hasattr(item, 'hdmi_ports'):
        data["hdmi_ports"] = item.hdmi_ports
    if hasattr(item, 'usb_ports'):
        data["usb_ports"] = item.usb_ports
    if hasattr(item, 'wall_mountable'):
        data["wall_mountable"] = item.wall_mountable
    if hasattr(item, 'smart_category'):
        data["smart_category"] = item.get_smart_category_display() if hasattr(item, 'get_smart_category_display') else item.smart_category
    if hasattr(item, 'voice_assistant'):
        data["voice_assistant"] = item.get_voice_assistant_display() if hasattr(item, 'get_voice_assistant_display') else item.voice_assistant
    if hasattr(item, 'connectivity'):
        data["connectivity"] = item.connectivity
    if hasattr(item, 'power_source'):
        data["power_source"] = item.get_power_source_display() if hasattr(item, 'get_power_source_display') else item.power_source
    if hasattr(item, 'mobile_app_support'):
        data["mobile_app_support"] = item.mobile_app_support
    if hasattr(item, 'has_scheduling'):
        data["has_scheduling"] = item.has_scheduling
    if hasattr(item, 'has_automation'):
        data["has_automation"] = item.has_automation
    if hasattr(item, 'installation_required'):
        data["installation_required"] = item.installation_required
    # Smartwatch-specific
    if hasattr(item, 'compatibility'):
        data["compatibility"] = item.get_compatibility_display() if hasattr(item, 'get_compatibility_display') else item.compatibility
    if hasattr(item, 'has_blood_oxygen_monitor'):
        data["has_blood_oxygen_monitor"] = item.has_blood_oxygen_monitor
    if hasattr(item, 'has_ecg'):
        data["has_ecg"] = item.has_ecg
    if hasattr(item, 'strap_material'):
        data["strap_material"] = item.strap_material
    if hasattr(item, 'case_material'):
        data["case_material"] = item.case_material
    # Gaming Console-specific
    if hasattr(item, 'generation'):
        data["generation"] = item.generation
    if hasattr(item, 'max_resolution'):
        data["max_resolution"] = item.max_resolution
    if hasattr(item, 'max_fps'):
        data["max_fps"] = item.max_fps
    if hasattr(item, 'has_disc_drive'):
        data["has_disc_drive"] = item.has_disc_drive
    if hasattr(item, 'has_ray_tracing'):
        data["has_ray_tracing"] = item.has_ray_tracing
    if hasattr(item, 'has_online_gaming'):
        data["has_online_gaming"] = item.has_online_gaming
    if hasattr(item, 'controller_included'):
        data["controller_included"] = item.controller_included
    if hasattr(item, 'backward_compatibility'):
        data["backward_compatibility"] = item.backward_compatibility
    if hasattr(item, 'subscription_required'):
        data["subscription_required"] = item.subscription_required
    # Fitness Tracker-specific
    if hasattr(item, 'has_blood_oxygen_monitor'):
        data["has_blood_oxygen_monitor"] = item.has_blood_oxygen_monitor
    if hasattr(item, 'has_step_counter'):
        data["has_step_counter"] = item.has_step_counter
    if hasattr(item, 'has_calorie_tracking'):
        data["has_calorie_tracking"] = item.has_calorie_tracking
    # Drone-specific
    if hasattr(item, 'video_resolution') and 'video_resolution' not in data:
        data["video_resolution"] = item.video_resolution
    if hasattr(item, 'max_range_km'):
        data["max_range_km"] = float(item.max_range_km) if item.max_range_km else None
    if hasattr(item, 'max_speed_kmh'):
        data["max_speed_kmh"] = item.max_speed_kmh
    if hasattr(item, 'has_obstacle_avoidance'):
        data["has_obstacle_avoidance"] = item.has_obstacle_avoidance
    if hasattr(item, 'has_follow_me'):
        data["has_follow_me"] = item.has_follow_me
    if hasattr(item, 'has_return_to_home'):
        data["has_return_to_home"] = item.has_return_to_home
    if hasattr(item, 'battery_charging_time'):
        data["battery_charging_time"] = item.battery_charging_time
    # Tablet-specific
    if hasattr(item, 'has_cellular'):
        data["has_cellular"] = item.has_cellular
    if hasattr(item, 'has_keyboard_support'):
        data["has_keyboard_support"] = item.has_keyboard_support
    # Drone/Tablet weight (already in drone, also in tablet)
    if hasattr(item, 'drone_type'):
        data["drone_type"] = item.get_drone_type_display() if hasattr(item, 'get_drone_type_display') else item.drone_type
    if hasattr(item, 'flight_time_minutes'):
        data["flight_time_minutes"] = item.flight_time_minutes
    if hasattr(item, 'weight_grams') and 'weight_grams' not in data:
        data["weight_grams"] = item.weight_grams
    if hasattr(item, 'camera_resolution_mp'):
        data["camera_resolution_mp"] = item.camera_resolution_mp
    if hasattr(item, 'tracker_type'):
        data["tracker_type"] = item.get_tracker_type_display() if hasattr(item, 'get_tracker_type_display') else item.tracker_type
    if hasattr(item, 'has_heart_rate_monitor'):
        data["has_heart_rate_monitor"] = item.has_heart_rate_monitor
    if hasattr(item, 'has_sleep_tracking'):
        data["has_sleep_tracking"] = item.has_sleep_tracking
    if hasattr(item, 'has_stylus_support'):
        data["has_stylus_support"] = item.has_stylus_support
    if hasattr(item, 'has_4k_support'):
        data["has_4k_support"] = item.has_4k_support
    if hasattr(item, 'weight_grams'):
        data["weight_grams"] = item.weight_grams

    return data



@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request, product_type):
    if product_type not in PRODUCT_MODELS:
        return JsonResponse({"error": f"Product type '{product_type}' not found."}, status=404)
    
    model = PRODUCT_MODELS[product_type]
    
    if request.method == "GET":
        queryset = model.objects.filter(is_active=True)

        # Common filters
        brand = request.GET.get("brand")
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        min_price = request.GET.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        in_stock = request.GET.get("in_stock")
        if in_stock in ["1", "true", "True"]:
            queryset = queryset.filter(stock__gt=0)

        # Model-specific filters
        if hasattr(model, 'ram_gb'):
            min_ram = request.GET.get("min_ram_gb")
            if min_ram:
                queryset = queryset.filter(ram_gb__gte=min_ram)

        if hasattr(model, 'storage_gb'):
            min_storage = request.GET.get("min_storage_gb")
            if min_storage:
                queryset = queryset.filter(storage_gb__gte=min_storage)

        if hasattr(model, 'cpu'):
            cpu = request.GET.get("cpu")
            if cpu:
                queryset = queryset.filter(cpu=cpu)

        if hasattr(model, 'chipset'):
            chipset = request.GET.get("chipset")
            if chipset:
                queryset = queryset.filter(chipset=chipset)

        items = [_model_to_dict(model, item) for item in queryset]
        return JsonResponse({"items": items})

    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # Basic required fields
    required = ["name", "brand", "price"]
    for key in required:
        if key not in payload:
            return JsonResponse({"error": f"Missing field: {key}"}, status=400)

    # Create item with common fields
    item_data = {
        "name": payload["name"],
        "brand": payload["brand"],
        "price": Decimal(str(payload["price"])),
        "stock": payload.get("stock", 0),
        "description": payload.get("description", ""),
        "is_active": payload.get("is_active", True),
    }

    # Add model-specific fields
    model_specific_fields = [field.name for field in model._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    for field in model_specific_fields:
        if field in payload:
            value = payload[field]
            if field in ['price', 'display_size_inches', 'battery_hours', 'battery_days']:
                value = Decimal(str(value))
            item_data[field] = value

    item = model.objects.create(**item_data)
    return JsonResponse({"item": _model_to_dict(model, item)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "PUT", "DELETE"])
def product_detail(request, product_type, item_id):
    if product_type not in PRODUCT_MODELS:
        return JsonResponse({"error": f"Product type '{product_type}' not found."}, status=404)
    
    model = PRODUCT_MODELS[product_type]
    item = model.objects.filter(id=item_id).first()
    if not item:
        return JsonResponse({"error": f"{product_type.replace('_', ' ').title()} product not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"item": _model_to_dict(model, item)})

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"message": f"{product_type.replace('_', ' ').title()} product deleted successfully."})

    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # Update fields
    model_specific_fields = [field.name for field in model._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    for field in model_specific_fields:
        if field in payload:
            value = payload[field]
            if field in ['price', 'display_size_inches', 'battery_hours', 'battery_days']:
                value = Decimal(str(value))
            setattr(item, field, value)

    item.save()
    return JsonResponse({"item": _model_to_dict(model, item)})


@csrf_exempt
@require_http_methods(["GET"])
def all_products(request):
    """Get all products from all categories"""
    all_items = []
    
    for product_type, model in PRODUCT_MODELS.items():
        queryset = model.objects.filter(is_active=True)
        for item in queryset:
            data = _model_to_dict(model, item)
            data["product_type"] = product_type
            all_items.append(data)
    
    return JsonResponse({"items": all_items})
