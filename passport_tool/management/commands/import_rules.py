import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from passport_tool.models import CountryRule

class Command(BaseCommand):
    help = 'Import global photo rules from JSON'

    def handle(self, *args, **options):
        json_path = os.path.join(os.getcwd(), 'global_photo_rules.json')
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'JSON file not found at {json_path}'))
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        count = 0
        for entry in data:
            country_name = entry['country_name']
            country_code = entry['country_code']
            
            for doc in entry['documents']:
                name = doc['name']
                category = doc.get('category', 'Passport')
                
                # Determine is_exam
                is_exam = category == 'Education'
                
                # For India exams, set hierarchy
                exam_country = None
                exam_state = None
                exam_organization = None
                
                display_name = name
                if is_exam:
                    display_name = name # Keep as is, or "SSC CGL" etc.
                    exam_country = country_name
                    
                    # Detect State from name if available in typical format
                    if "TNPSC" in name or "Tamil Nadu" in name:
                        exam_state = "Tamil Nadu"
                        exam_organization = "TNPSC"
                    elif "KPSC" in name or "Kerala" in name:
                        exam_state = "Kerala"
                        exam_organization = "KPSC"
                    elif "APPSC" in name or "Andhra Pradesh" in name:
                        exam_state = "Andhra Pradesh"
                        exam_organization = "APPSC"
                    elif "TSPSC" in name or "Telangana" in name:
                        exam_state = "Telangana"
                        exam_organization = "TSPSC"
                    elif "UPPSC" in name or "Uttar Pradesh" in name:
                        exam_state = "Uttar Pradesh"
                        exam_organization = "UPPSC"
                    elif "MPSC" in name or "Maharashtra" in name:
                        exam_state = "Maharashtra"
                        exam_organization = "MPSC"
                    elif "WBPSC" in name or "West Bengal" in name:
                        exam_state = "West Bengal"
                        exam_organization = "WBPSC"
                    elif "RPSC" in name or "Rajasthan" in name:
                        exam_state = "Rajasthan"
                        exam_organization = "RPSC"
                    elif "GPSC" in name or "Gujarat" in name:
                        exam_state = "Gujarat"
                        exam_organization = "GPSC"
                    elif "BPSC" in name or "Bihar" in name:
                        exam_state = "Bihar"
                        exam_organization = "BPSC"
                    else:
                        exam_state = "Central"
                        if "SSC" in name: exam_organization = "SSC"
                        elif "UPSC" in name: exam_organization = "UPSC"
                        elif "NEET" in name: exam_organization = "NTA (NEET)"
                        elif "JEE" in name: exam_organization = "NTA (JEE)"
                        elif "GATE" in name: exam_organization = "IIT (GATE)"
                        elif "IBPS" in name: exam_organization = "IBPS"
                        elif "Railway" in name or "RRB" in name: exam_organization = "RRB"
                        else: exam_organization = "Other"

                # Prepare dimensions
                width_mm = doc.get('width_mm', 0)
                height_mm = doc.get('height_mm', 0)
                width_px = doc.get('width_px')
                height_px = doc.get('height_px')
                
                # Conversion if inch/px provided
                if 'width_inch' in doc:
                    width_mm = int(doc['width_inch'] * 25.4)
                    height_mm = int(doc['height_inch'] * 25.4)
                
                # If mm is missing but px is present, estimate mm for mandatory field
                if width_px and width_mm == 0:
                    width_mm = int(width_px * 25.4 / 300) # Assume 300 DPI
                if height_px and height_mm == 0:
                    height_mm = int(height_px * 25.4 / 300)

                # Fallback defaults to avoid validation errors
                if width_mm == 0: width_mm = 35
                if height_mm == 0: height_mm = 45

                slug = slugify(f"{display_name}-{country_name}")
                
                rule, created = CountryRule.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'country': display_name,
                        'width_mm': width_mm,
                        'height_mm': height_mm,
                        'width_px': width_px,
                        'height_px': height_px,
                        'bg_color': doc.get('bg_color', 'white'),
                        'meta_title': f"{display_name} Photo Maker & Compliance Tool",
                        'meta_description': f"Generate {display_name} photos with official size {width_mm}x{height_mm}mm. Free online tool with background removal.",
                        'content_body': f"Official requirements for {display_name}. Background: {doc.get('bg_color')}. Size: {width_mm}x{height_mm}mm.",
                        'h1': f"{display_name} Photo Creator",
                        'default_target_kb': doc.get('max_kb', 350),
                        'is_exam': is_exam,
                        'exam_country': exam_country,
                        'exam_state': exam_state,
                        'exam_organization': exam_organization,
                    }
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} new rules.'))
