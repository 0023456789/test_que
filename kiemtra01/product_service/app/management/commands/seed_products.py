from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models.computer import ComputerProduct
from app.models.mobile import MobileProduct
from app.models.tablet import TabletProduct
from app.models.smartwatch import SmartwatchProduct
from app.models.headphone import HeadphoneProduct
from app.models.camera import CameraProduct
from app.models.gaming_console import GamingConsoleProduct
from app.models.tv import TVProduct
from app.models.smart_home import SmartHomeProduct
from app.models.fitness_tracker import FitnessTrackerProduct
from app.models.drone import DroneProduct


class Command(BaseCommand):
    help = 'Seed database with sample products for all categories'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Seeding Computer Products...')
            self.seed_computers()
            
            self.stdout.write('Seeding Mobile Products...')
            self.seed_mobiles()
            
            self.stdout.write('Seeding Tablet Products...')
            self.seed_tablets()
            
            self.stdout.write('Seeding Smartwatch Products...')
            self.seed_smartwatches()
            
            self.stdout.write('Seeding Headphone Products...')
            self.seed_headphones()
            
            self.stdout.write('Seeding Camera Products...')
            self.seed_cameras()
            
            self.stdout.write('Seeding Gaming Console Products...')
            self.seed_gaming_consoles()
            
            self.stdout.write('Seeding TV Products...')
            self.seed_tvs()
            
            self.stdout.write('Seeding Smart Home Products...')
            self.seed_smart_homes()
            
            self.stdout.write('Seeding Fitness Tracker Products...')
            self.seed_fitness_trackers()
            
            self.stdout.write('Seeding Drone Products...')
            self.seed_drones()
            
            self.stdout.write(self.style.SUCCESS('Successfully seeded all product categories!'))

    def seed_computers(self):
        computers = [
            {
                'name': 'MacBook Pro 14"',
                'brand': 'Apple',
                'cpu': 'apple_m3',
                'ram_gb': 16,
                'storage_type': 'ssd',
                'storage_gb': 512,
                'gpu': 'Integrated',
                'display_size_inches': Decimal('14.2'),
                'display_resolution': '3024x1964',
                'refresh_rate_hz': 120,
                'operating_system': 'macos',
                'has_touchscreen': False,
                'has_backlit_keyboard': True,
                'has_fingerprint_reader': True,
                'has_webcam': True,
                'battery_hours': Decimal('18.0'),
                'ports': '["Thunderbolt 4 x3", "HDMI", "SD Card Slot"]',
                'warranty_months': 12,
                'price': Decimal('1999.99'),
                'stock': 25,
                'description': 'Powerful MacBook Pro with M3 chip for professionals.'
            },
            {
                'name': 'Dell XPS 15',
                'brand': 'Dell',
                'cpu': 'intel_i7',
                'ram_gb': 32,
                'storage_type': 'ssd',
                'storage_gb': 1024,
                'gpu': 'NVIDIA RTX 4050',
                'display_size_inches': Decimal('15.6'),
                'display_resolution': '1920x1080',
                'refresh_rate_hz': 60,
                'operating_system': 'windows',
                'has_touchscreen': False,
                'has_backlit_keyboard': True,
                'has_fingerprint_reader': True,
                'has_webcam': True,
                'battery_hours': Decimal('8.5'),
                'ports': '["USB-C x2", "USB-A x2", "HDMI 2.1", "SD Card Reader"]',
                'warranty_months': 12,
                'price': Decimal('1799.99'),
                'stock': 15,
                'description': 'High-performance laptop with powerful graphics for creative work.'
            },
            {
                'name': 'ThinkPad X1 Carbon',
                'brand': 'Lenovo',
                'cpu': 'intel_i5',
                'ram_gb': 16,
                'storage_type': 'ssd',
                'storage_gb': 512,
                'gpu': 'Integrated',
                'display_size_inches': Decimal('14.0'),
                'display_resolution': '1920x1200',
                'refresh_rate_hz': 60,
                'operating_system': 'windows',
                'has_touchscreen': False,
                'has_backlit_keyboard': True,
                'has_fingerprint_reader': True,
                'has_webcam': True,
                'battery_hours': Decimal('15.0'),
                'ports': '["USB-C x3", "USB-A x1", "HDMI"]',
                'warranty_months': 36,
                'price': Decimal('1499.99'),
                'stock': 20,
                'description': 'Business laptop with exceptional durability and security features.'
            }
        ]
        
        for comp_data in computers:
            ComputerProduct.objects.get_or_create(
                name=comp_data['name'],
                brand=comp_data['brand'],
                defaults=comp_data
            )

    def seed_mobiles(self):
        mobiles = [
            {
                'name': 'iPhone 15 Pro',
                'brand': 'Apple',
                'chipset': 'apple_a17',
                'ram_gb': 8,
                'storage_gb': 256,
                'display_size_inches': Decimal('6.1'),
                'display_resolution': '2556x1179',
                'refresh_rate_hz': 120,
                'main_camera_mp': 48,
                'front_camera_mp': 12,
                'battery_mah': 3274,
                'fast_charging_w': 20,
                'has_5g': True,
                'has_nfc': True,
                'has_wireless_charging': True,
                'has_water_resistance': True,
                'operating_system': 'ios',
                'sim_type': 'dual_sim',
                'color_options': '["Titanium Blue", "Titanium White", "Titanium Black", "Titanium Natural"]',
                'price': Decimal('999.99'),
                'stock': 50,
                'description': 'Premium iPhone with titanium design and powerful A17 chip.'
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'brand': 'Samsung',
                'chipset': 'snapdragon_8',
                'ram_gb': 12,
                'storage_gb': 512,
                'display_size_inches': Decimal('6.8'),
                'display_resolution': '3120x1440',
                'refresh_rate_hz': 120,
                'main_camera_mp': 200,
                'front_camera_mp': 12,
                'battery_mah': 5000,
                'fast_charging_w': 45,
                'has_5g': True,
                'has_nfc': True,
                'has_wireless_charging': True,
                'has_water_resistance': True,
                'operating_system': 'android',
                'sim_type': 'dual_sim',
                'color_options': '["Titanium Black", "Titanium Gray", "Titanium Violet", "Titanium Yellow"]',
                'price': Decimal('1199.99'),
                'stock': 30,
                'description': 'Flagship Android phone with incredible camera system and S Pen support.'
            }
        ]
        
        for mobile_data in mobiles:
            MobileProduct.objects.get_or_create(
                name=mobile_data['name'],
                brand=mobile_data['brand'],
                defaults=mobile_data
            )

    def seed_tablets(self):
        tablets = [
            {
                'name': 'iPad Pro 12.9"',
                'brand': 'Apple',
                'cpu': 'apple_m2',
                'ram_gb': 8,
                'storage_gb': 256,
                'display_size_inches': Decimal('12.9'),
                'display_resolution': '2732x2048',
                'refresh_rate_hz': 120,
                'main_camera_mp': 12,
                'front_camera_mp': 12,
                'battery_mah': 10758,
                'has_cellular': False,
                'has_stylus_support': True,
                'has_keyboard_support': True,
                'operating_system': 'ios',
                'weight_grams': 682,
                'price': Decimal('1099.99'),
                'stock': 25,
                'description': 'Professional tablet with M2 chip and stunning display.'
            },
            {
                'name': 'Samsung Galaxy Tab S9',
                'brand': 'Samsung',
                'cpu': 'snapdragon_8',
                'ram_gb': 8,
                'storage_gb': 128,
                'display_size_inches': Decimal('11.0'),
                'display_resolution': '2560x1600',
                'refresh_rate_hz': 120,
                'main_camera_mp': 13,
                'front_camera_mp': 12,
                'battery_mah': 8400,
                'has_cellular': False,
                'has_stylus_support': True,
                'has_keyboard_support': True,
                'operating_system': 'android',
                'weight_grams': 498,
                'price': Decimal('699.99'),
                'stock': 20,
                'description': 'Premium Android tablet with S Pen included.'
            }
        ]
        
        for tablet_data in tablets:
            TabletProduct.objects.get_or_create(
                name=tablet_data['name'],
                brand=tablet_data['brand'],
                defaults=tablet_data
            )

    def seed_smartwatches(self):
        smartwatches = [
            {
                'name': 'Apple Watch Series 9',
                'brand': 'Apple',
                'compatibility': 'ios_only',
                'display_type': 'oled',
                'display_size_inches': Decimal('1.9'),
                'battery_days': Decimal('1.5'),
                'has_gps': True,
                'has_heart_rate_monitor': True,
                'has_blood_oxygen_monitor': True,
                'has_ecg': True,
                'has_sleep_tracking': True,
                'has_water_resistance': True,
                'strap_material': 'Sport Band',
                'case_material': 'Aluminum',
                'price': Decimal('399.99'),
                'stock': 40,
                'description': 'Advanced health monitoring and fitness tracking.'
            },
            {
                'name': 'Samsung Galaxy Watch 6',
                'brand': 'Samsung',
                'compatibility': 'android_only',
                'display_type': 'amoled',
                'display_size_inches': Decimal('1.3'),
                'battery_days': Decimal('2.0'),
                'has_gps': True,
                'has_heart_rate_monitor': True,
                'has_blood_oxygen_monitor': True,
                'has_ecg': True,
                'has_sleep_tracking': True,
                'has_water_resistance': True,
                'strap_material': 'Silicone',
                'case_material': 'Stainless Steel',
                'price': Decimal('299.99'),
                'stock': 35,
                'description': 'Comprehensive health and fitness features for Android users.'
            }
        ]
        
        for watch_data in smartwatches:
            SmartwatchProduct.objects.get_or_create(
                name=watch_data['name'],
                brand=watch_data['brand'],
                defaults=watch_data
            )

    def seed_headphones(self):
        headphones = [
            {
                'name': 'AirPods Pro 2',
                'brand': 'Apple',
                'headphone_type': 'true_wireless',
                'is_wireless': True,
                'has_noise_cancelling': True,
                'has_microphone': True,
                'battery_hours': Decimal('6.0'),
                'charging_time_hours': Decimal('1.0'),
                'bluetooth_version': '5.3',
                'frequency_response': '20Hz - 20kHz',
                'impedance_ohms': None,
                'driver_size_mm': 11,
                'has_fast_charging': True,
                'price': Decimal('249.99'),
                'stock': 60,
                'description': 'Premium true wireless earbuds with active noise cancellation.'
            },
            {
                'name': 'Sony WH-1000XM5',
                'brand': 'Sony',
                'headphone_type': 'over_ear',
                'is_wireless': True,
                'has_noise_cancelling': True,
                'has_microphone': True,
                'battery_hours': Decimal('30.0'),
                'charging_time_hours': Decimal('3.0'),
                'bluetooth_version': '5.2',
                'frequency_response': '4Hz - 40kHz',
                'impedance_ohms': 48,
                'driver_size_mm': 30,
                'has_fast_charging': True,
                'price': Decimal('399.99'),
                'stock': 25,
                'description': 'Industry-leading noise cancellation and exceptional sound quality.'
            }
        ]
        
        for headphone_data in headphones:
            HeadphoneProduct.objects.get_or_create(
                name=headphone_data['name'],
                brand=headphone_data['brand'],
                defaults=headphone_data
            )

    def seed_cameras(self):
        cameras = [
            {
                'name': 'Canon EOS R5',
                'brand': 'Canon',
                'camera_type': 'mirrorless',
                'sensor_type': 'full_frame',
                'megapixels': 45,
                'iso_range': '100-51200',
                'video_resolution': '8K',
                'video_fps': 30,
                'has_image_stabilization': True,
                'has_wifi': True,
                'has_bluetooth': True,
                'has_gps': False,
                'battery_shots': 490,
                'lens_mount': 'Canon RF',
                'viewfinder_type': 'Electronic',
                'price': Decimal('3899.99'),
                'stock': 10,
                'description': 'Professional mirrorless camera with 8K video recording.'
            },
            {
                'name': 'DJI Mini 3 Pro',
                'brand': 'DJI',
                'camera_type': 'action',
                'sensor_type': '1_inch',
                'megapixels': 48,
                'iso_range': '100-3200',
                'video_resolution': '4K',
                'video_fps': 60,
                'has_image_stabilization': True,
                'has_wifi': True,
                'has_bluetooth': True,
                'has_gps': True,
                'battery_shots': None,
                'lens_mount': '',
                'viewfinder_type': '',
                'price': Decimal('759.99'),
                'stock': 20,
                'description': 'Compact drone with professional camera capabilities.'
            }
        ]
        
        for camera_data in cameras:
            CameraProduct.objects.get_or_create(
                name=camera_data['name'],
                brand=camera_data['brand'],
                defaults=camera_data
            )

    def seed_gaming_consoles(self):
        consoles = [
            {
                'name': 'PlayStation 5',
                'brand': 'Sony',
                'console_type': 'home',
                'generation': '9th Generation',
                'storage_gb': 825,
                'max_resolution': '4K',
                'max_fps': 120,
                'has_disc_drive': True,
                'has_4k_support': True,
                'has_ray_tracing': True,
                'has_online_gaming': True,
                'controller_included': True,
                'backward_compatibility': '["PS4", "PS3", "PS2", "PS1"]',
                'subscription_required': True,
                'price': Decimal('499.99'),
                'stock': 30,
                'description': 'Next-generation gaming console with ultra-fast SSD and ray tracing.'
            },
            {
                'name': 'Nintendo Switch OLED',
                'brand': 'Nintendo',
                'console_type': 'hybrid',
                'generation': '8th Generation',
                'storage_gb': 64,
                'max_resolution': '1080p',
                'max_fps': 60,
                'has_disc_drive': False,
                'has_4k_support': False,
                'has_ray_tracing': False,
                'has_online_gaming': True,
                'controller_included': True,
                'backward_compatibility': '["Nintendo Switch"]',
                'subscription_required': True,
                'price': Decimal('349.99'),
                'stock': 40,
                'description': 'Hybrid console with vibrant OLED display for handheld and TV gaming.'
            }
        ]
        
        for console_data in consoles:
            GamingConsoleProduct.objects.get_or_create(
                name=console_data['name'],
                brand=console_data['brand'],
                defaults=console_data
            )

    def seed_tvs(self):
        tvs = [
            {
                'name': 'LG OLED55C3',
                'brand': 'LG',
                'display_type': 'oled',
                'display_size_inches': 55,
                'resolution': '4k',
                'refresh_rate_hz': 120,
                'has_smart_tv': True,
                'operating_system': 'webOS',
                'has_hdr': True,
                'hdr_format': 'Dolby Vision, HDR10',
                'has_dolby_vision': True,
                'has_dolby_atmos': True,
                'hdmi_ports': 4,
                'usb_ports': 3,
                'has_wifi': True,
                'has_bluetooth': True,
                'wall_mountable': True,
                'price': Decimal('1499.99'),
                'stock': 15,
                'description': 'Premium OLED TV with perfect blacks and infinite contrast.'
            },
            {
                'name': 'Samsung QN90B',
                'brand': 'Samsung',
                'display_type': 'qled',
                'display_size_inches': 65,
                'resolution': '4k',
                'refresh_rate_hz': 120,
                'has_smart_tv': True,
                'operating_system': 'Tizen',
                'has_hdr': True,
                'hdr_format': 'HDR10+, HDR10',
                'has_dolby_vision': False,
                'has_dolby_atmos': True,
                'hdmi_ports': 4,
                'usb_ports': 2,
                'has_wifi': True,
                'has_bluetooth': True,
                'wall_mountable': True,
                'price': Decimal('1799.99'),
                'stock': 12,
                'description': 'Neo QLED TV with exceptional brightness and color accuracy.'
            }
        ]
        
        for tv_data in tvs:
            TVProduct.objects.get_or_create(
                name=tv_data['name'],
                brand=tv_data['brand'],
                defaults=tv_data
            )

    def seed_smart_homes(self):
        smart_homes = [
            {
                'name': 'Amazon Echo Dot 5th Gen',
                'brand': 'Amazon',
                'smart_category': 'speaker',
                'voice_assistant': 'alexa',
                'connectivity': '["Wi-Fi", "Bluetooth"]',
                'power_source': 'wired',
                'mobile_app_support': True,
                'has_scheduling': True,
                'has_automation': True,
                'installation_required': False,
                'price': Decimal('49.99'),
                'stock': 80,
                'description': 'Compact smart speaker with Alexa voice assistant.'
            },
            {
                'name': 'Philips Hue Starter Kit',
                'brand': 'Philips',
                'smart_category': 'lighting',
                'voice_assistant': 'multiple',
                'connectivity': '["Zigbee", "Wi-Fi"]',
                'power_source': 'wired',
                'mobile_app_support': True,
                'has_scheduling': True,
                'has_automation': True,
                'installation_required': True,
                'price': Decimal('89.99'),
                'stock': 45,
                'description': 'Smart lighting system with millions of color options.'
            }
        ]
        
        for home_data in smart_homes:
            SmartHomeProduct.objects.get_or_create(
                name=home_data['name'],
                brand=home_data['brand'],
                defaults=home_data
            )

    def seed_fitness_trackers(self):
        fitness_trackers = [
            {
                'name': 'Fitbit Charge 6',
                'brand': 'Fitbit',
                'tracker_type': 'band',
                'display_type': 'AMOLED',
                'battery_days': Decimal('7.0'),
                'has_gps': True,
                'has_heart_rate_monitor': True,
                'has_blood_oxygen_monitor': True,
                'has_sleep_tracking': True,
                'has_step_counter': True,
                'has_calorie_tracking': True,
                'has_water_resistance': True,
                'strap_material': 'Silicone',
                'mobile_app_support': True,
                'price': Decimal('159.99'),
                'stock': 70,
                'description': 'Advanced fitness tracker with built-in GPS and health monitoring.'
            },
            {
                'name': 'Oura Ring Gen 3',
                'brand': 'Oura',
                'tracker_type': 'ring',
                'display_type': '',
                'battery_days': Decimal('7.0'),
                'has_gps': False,
                'has_heart_rate_monitor': True,
                'has_blood_oxygen_monitor': True,
                'has_sleep_tracking': True,
                'has_step_counter': True,
                'has_calorie_tracking': True,
                'has_water_resistance': True,
                'strap_material': '',
                'mobile_app_support': True,
                'price': Decimal('349.99'),
                'stock': 25,
                'description': 'Smart ring with advanced sleep and recovery tracking.'
            }
        ]
        
        for fitness_data in fitness_trackers:
            FitnessTrackerProduct.objects.get_or_create(
                name=fitness_data['name'],
                brand=fitness_data['brand'],
                defaults=fitness_data
            )

    def seed_drones(self):
        drones = [
            {
                'name': 'DJI Mini 3',
                'brand': 'DJI',
                'drone_type': 'consumer',
                'camera_resolution_mp': 12,
                'video_resolution': '4K',
                'flight_time_minutes': 38,
                'max_range_km': Decimal('10.0'),
                'max_speed_kmh': 57,
                'has_gps': True,
                'has_obstacle_avoidance': False,
                'has_follow_me': True,
                'has_return_to_home': True,
                'controller_included': True,
                'battery_charging_time': 60,
                'weight_grams': 248,
                'price': Decimal('469.99'),
                'stock': 20,
                'description': 'Lightweight drone under 250g with 4K camera capabilities.'
            },
            {
                'name': 'Autel Robotics EVO Lite+',
                'brand': 'Autel Robotics',
                'drone_type': 'consumer',
                'camera_resolution_mp': 20,
                'video_resolution': '6K',
                'flight_time_minutes': 40,
                'max_range_km': Decimal('12.0'),
                'max_speed_kmh': 68,
                'has_gps': True,
                'has_obstacle_avoidance': True,
                'has_follow_me': True,
                'has_return_to_home': True,
                'controller_included': True,
                'battery_charging_time': 70,
                'weight_grams': 835,
                'price': Decimal('1249.99'),
                'stock': 10,
                'description': 'Advanced consumer drone with 6K video and obstacle avoidance.'
            }
        ]
        
        for drone_data in drones:
            DroneProduct.objects.get_or_create(
                name=drone_data['name'],
                brand=drone_data['brand'],
                defaults=drone_data
            )
