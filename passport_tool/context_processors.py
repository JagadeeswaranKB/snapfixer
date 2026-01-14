from .models import CountryRule, SiteSettings, PageMeta

def country_rules(request):
    # 1. Distinct countries for the "By Country" column
    # We group by exam_country and take the best 'Passport' rule for each
    all_rules = CountryRule.objects.filter(is_exam=False, is_tool=False).exclude(exam_country="Global").order_by('exam_country', 'country')
    
    unique_countries = {}
    for r in all_rules:
        if r.exam_country not in unique_countries:
            unique_countries[r.exam_country] = r
        elif "Passport" in r.country and "Passport" not in unique_countries[r.exam_country].country:
            unique_countries[r.exam_country] = r

    nav_countries = sorted(unique_countries.values(), key=lambda x: x.exam_country)
    
    exams = CountryRule.objects.filter(is_exam=True).order_by('exam_country', 'exam_state', 'exam_organization', 'country')
    tools = list(CountryRule.objects.filter(is_tool=True))
    
    # Build Hierarchies: Exams and Visas
    exam_hierarchy = {}
    visa_hierarchy = {}

    for item in exams:
        # Determine if it's a Visa or an Exam
        # Logic: If exam_organization is "Visa", "Residence Permit" or country contains "Visa", it's a Visa
        is_visa = (item.exam_organization in ["Visa", "Residence Permit", "BRP", "Biometric Residence Permit"]) or ("Visa" in item.country) or ("BRP" in item.country)
        target_hierarchy = visa_hierarchy if is_visa else exam_hierarchy
        
        c = item.exam_country or "Other"
        
        if c not in target_hierarchy:
            target_hierarchy[c] = {"states": {}, "orgs": {}, "flat_exams": []}
        
        if not item.exam_state and not item.exam_organization:
            target_hierarchy[c]["flat_exams"].append(item)
        elif not item.exam_state and item.exam_organization:
            o = item.exam_organization
            if o not in target_hierarchy[c]["orgs"]:
                target_hierarchy[c]["orgs"][o] = []
            target_hierarchy[c]["orgs"][o].append(item)
        else:
            s = item.exam_state or "General"
            o = item.exam_organization or "Standard"
            
            if s not in target_hierarchy[c]["states"]:
                target_hierarchy[c]["states"][s] = {}
            if o not in target_hierarchy[c]["states"][s]:
                target_hierarchy[c]["states"][s][o] = []
                
            target_hierarchy[c]["states"][s][o].append(item)
    
    return {
        'nav_countries': nav_countries,
        'exam_hierarchy': exam_hierarchy,
        'visa_hierarchy': visa_hierarchy,
        'nav_tools': tools,
        'custom_size_rule': CountryRule.objects.filter(slug='custom-size-passport-photo').first(),
        'site_settings': SiteSettings.load(),
    }

def meta_tags_processor(request):
    """
    Looks up meta tags for the current URL path.
    """
    path = request.path
    page_meta = PageMeta.objects.filter(path=path).first()
    
    # Fallback for home page variations
    if not page_meta and path == '':
        page_meta = PageMeta.objects.filter(path='/').first()
        
    return {
        'page_meta': page_meta
    }
