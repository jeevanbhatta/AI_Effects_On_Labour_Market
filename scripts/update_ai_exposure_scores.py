"""
Script to update AI_Exposure_Score in occupation_panel.csv using:
1. ILO 2025 AI Exposure Scores from ISCO-08 classifications
2. ISCO to SOC crosswalk mapping

Data sources:
- ILO Working Paper 140: https://webapps.ilo.org/static/english/intserv/working-papers/wp140/index.html
- ISCO-SOC Crosswalk: data/isco_soc_crosswalk (JOLTS) - ISCO-08 to 2010 SOC.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Define paths
DATA_DIR = Path(__file__).parent.parent / "data"
CROSSWALK_FILE = DATA_DIR / "isco_soc_crosswalk (JOLTS) - ISCO-08 to 2010 SOC.csv"
OCCUPATION_PANEL_FILE = DATA_DIR / "occupation_panel.csv"

# ILO 2025 AI Exposure Scores (from Table A1 in the Annex)
# Gradient 4 = Highest exposure, Gradient 3 = Significant, Gradient 2 = Moderate, Gradient 1 = Low
# Format: ISCO_Code: Mean_Score
# Source: ILO Working Paper 140 (2025) - Generative AI and Jobs
ILO_SCORES = {
    # Gradient 4 - Highest exposure, low task variability
    "4132": 0.70,  # Data Entry Clerks
    "4131": 0.65,  # Typists and Word Processing Operators
    "4311": 0.64,  # Accounting and Bookkeeping Clerks
    "4312": 0.64,  # Statistical, Finance and Insurance Clerks
    "3311": 0.63,  # Securities and Finance Dealers and Brokers
    "4419": 0.63,  # Clerical Support Workers Not Elsewhere Classified
    "2413": 0.62,  # Financial Analysts
    "4313": 0.61,  # Payroll Clerks
    "5244": 0.61,  # Contact Centre Salespersons
    "2513": 0.60,  # Web and Multimedia Developers
    "3312": 0.60,  # Credit and Loans Officers
    "4110": 0.60,  # General Office Clerks
    "4416": 0.60,  # Personnel Clerks
    
    # Gradient 3 - Significant exposure
    "2643": 0.59,  # Translators, Interpreters and Other Linguists
    "4120": 0.58,  # Secretaries (general)
    "4211": 0.58,  # Bank Tellers and Related Clerks
    "4222": 0.58,  # Contact Centre Information Clerks
    "4414": 0.58,  # Scribes and Related Workers
    "2412": 0.57,  # Financial and Investment Advisers
    "2514": 0.57,  # Applications Programmers
    "2521": 0.57,  # Database Designers and Administrators
    "2522": 0.57,  # Systems Administrators
    "3314": 0.57,  # Statistical, Mathematical and Related Associate Professionals
    "3331": 0.57,  # Clearing and Forwarding Agents
    "4225": 0.57,  # Inquiry Clerks
    "4226": 0.57,  # Receptionists (general)
    "2120": 0.56,  # Mathematicians, Actuaries and Statisticians
    "4221": 0.56,  # Travel Consultants and Clerks
    "2431": 0.55,  # Advertising and Marketing Professionals
    "2519": 0.55,  # Software and Applications Developers and Analysts NEC
    "2622": 0.55,  # Librarians and Related Information Professionals
    "2631": 0.55,  # Economists
    "2641": 0.55,  # Authors and Related Writers
    "3342": 0.55,  # Legal Secretaries
    "4227": 0.55,  # Survey and Market Research Interviewers
    "2112": 0.54,  # Meteorologists
    "2642": 0.54,  # Journalists
    "3343": 0.54,  # Administrative and Executive Secretaries
    "4223": 0.54,  # Telephone Switchboard Operators
    "2512": 0.53,  # Software Developers
    "3321": 0.53,  # Insurance Representatives
    "3344": 0.53,  # Medical Secretaries
    "3514": 0.53,  # Web Technicians
    "2523": 0.52,  # Computer Network Professionals
    "3252": 0.52,  # Medical Records and Health Information Technicians
    "2411": 0.51,  # Accountants
    "2434": 0.51,  # ICT Sales Professionals
    "4224": 0.51,  # Hotel Receptionists
    "4413": 0.51,  # Coding, Proofreading and Related Clerks
    "2433": 0.50,  # Technical and Medical Sales Professionals (excl ICT)
    "4323": 0.50,  # Transport Clerks
    
    # Gradient 2 - Moderate exposure
    "2166": 0.49,  # Graphic and Multimedia Designers
    "2511": 0.49,  # Systems Analysts
    "2529": 0.49,  # Database and Network Professionals NEC
    "3313": 0.49,  # Accounting Associate Professionals
    "3322": 0.49,  # Commercial Sales Representatives
    "3352": 0.49,  # Government Tax and Excise Officials
    "2153": 0.48,  # Telecommunications Engineers
    "2632": 0.48,  # Sociologists, Anthropologists and Related Professionals
    "3332": 0.48,  # Conference and Event Planners
    "4213": 0.48,  # Pawnbrokers and Money-lenders
    "1346": 0.47,  # Financial and Insurance Services Branch managers
    "2356": 0.47,  # Information Technology Trainers
    "2621": 0.47,  # Archivists and Curators
    "2633": 0.47,  # Philosophers, Historians and Political Scientists
    "2656": 0.47,  # Announcers on Radio, Television and Other Media
    "3512": 0.47,  # ICT User Support Technicians
    "2421": 0.46,  # Management and Organization Analysts
    "4411": 0.46,  # Library Clerks
    "5243": 0.46,  # Door-to-door Salespersons
    "2423": 0.45,  # Personnel and Careers Professionals
    "3315": 0.45,  # Valuers and Loss Assessors
    "3353": 0.45,  # Government Social Benefits Officials
    "4212": 0.45,  # Bookmakers, Croupiers and Related Gaming Workers
    "1330": 0.44,  # ICT Service Managers
    "1420": 0.44,  # Retail and Wholesale Trade Managers
    "2165": 0.44,  # Cartographers and Surveyors
    "3324": 0.44,  # Trade Brokers
    "3339": 0.44,  # Business Services Agents NEC
    "4322": 0.44,  # Production Clerks
    "2432": 0.43,  # Public Relations Professionals
    "3341": 0.43,  # Office Supervisors
    "3354": 0.43,  # Government Licensing Officials
    "3511": 0.43,  # ICT Operations Technicians
    "3513": 0.43,  # Computer Network and Systems Technicians
    "4214": 0.43,  # Debt Collectors and Related Workers
    "5221": 0.43,  # Shopkeepers
    "1219": 0.42,  # Business Services and Administration Managers NEC
    "2152": 0.42,  # Electronics Engineers
    "4229": 0.42,  # Client Information Workers NEC
    "5242": 0.42,  # Sales Demonstrators
    "1221": 0.41,  # Sales and Marketing Managers
    "2424": 0.41,  # Training and Staff Development Professionals
    "4412": 0.41,  # Mail Carriers and Sorting Clerks
    "2131": 0.40,  # Biologists, Botanists, Zoologists and Related Professionals
    
    # Gradient 1 - Low exposure (but high task variability)
    "2351": 0.39,  # Education Methods Specialists
    "2634": 0.39,  # Psychologists
    "3411": 0.39,  # Legal and Related Associate Professionals
    "3431": 0.39,  # Photographers
    "5230": 0.39,  # Cashiers and Ticket Clerks
    "2111": 0.38,  # Physicists and Astronomers
    "3141": 0.38,  # Life Science Technicians (excluding Medical)
    "5223": 0.38,  # Shop Sales Assistants
    "7321": 0.38,  # Pre-press Technicians
    "9623": 0.38,  # Meter Readers and Vending-machine Collectors
    "1411": 0.37,  # Hotel Managers
    "3433": 0.37,  # Gallery, Museum and Library Technicians
    "4415": 0.37,  # Filing and Copying Clerks
    "9621": 0.37,  # Messengers, Package Deliverers and Luggage Porters
    "3256": 0.35,  # Medical Assistants
    "5211": 0.35,  # Stall and Market Salespersons
    "8322": 0.28,  # Car, Taxi and Van Drivers
    
    # Minimal Exposure - Low overall exposure
    "3522": 0.45,  # Telecommunications Engineering Technicians
    "2422": 0.42,  # Policy Administration Professionals
    "2164": 0.41,  # Town and Traffic Planners
    "2265": 0.41,  # Dieticians and Nutritionists
    "1223": 0.40,  # Research and Development Managers
    "1222": 0.39,  # Advertising and Public Relations Managers
    "2113": 0.39,  # Chemists
    "3323": 0.39,  # Buyers
    "3333": 0.39,  # Employment agents and contractors
    "1112": 0.38,  # Senior Government Officials
    "1120": 0.38,  # Managing Directors and Chief Executives
    "1321": 0.38,  # Manufacturing Managers
    "1324": 0.38,  # Supply, Distribution and Related Managers
    "1349": 0.38,  # Professional Services Managers Not Elsewhere Classified
    "2133": 0.38,  # Environmental Protection Professionals
    "2143": 0.38,  # Environmental Engineers
    "3114": 0.38,  # Electronics Engineering Technicians
    "1114": 0.37,  # Senior Officials of Special-interest Organizations
    "1211": 0.37,  # Finance Managers
    "1344": 0.37,  # Social Welfare Managers
    "2141": 0.37,  # Industrial and Production Engineers
    "2161": 0.37,  # Building Architects
    "2162": 0.37,  # Landscape Architects
    "2310": 0.37,  # University and Higher Education Teachers
    "2619": 0.37,  # Legal Professionals Not Elsewhere Classified
    "2654": 0.37,  # Film, Stage and Related Directors and Producers
    "3422": 0.37,  # Sports Coaches, Instructors and Officials
    "3432": 0.37,  # Interior Designers and Decorators
    "4321": 0.37,  # Stock Clerks
    "1212": 0.36,  # Human Resource Managers
    "1342": 0.36,  # Health Service Managers
    "1345": 0.36,  # Education Managers
    "1412": 0.36,  # Restaurant Managers
    "2114": 0.36,  # Geologists and geophysicists
    "2611": 0.36,  # Lawyers
    "3359": 0.36,  # Government Regulatory Associate Professionals NEC
    "5222": 0.36,  # Shop Supervisors
    "1322": 0.35,  # Mining Managers
    "2145": 0.35,  # Chemical Engineers
    "2163": 0.35,  # Product and Garment Designers
    "2320": 0.35,  # Vocational Education Teachers
    "2354": 0.35,  # Other Music Teachers
    "2355": 0.35,  # Other Arts Teachers
    "3118": 0.35,  # Draughtspersons
    "3122": 0.35,  # Manufacturing Supervisors
    "3334": 0.35,  # Real Estate Agents and Property Managers
    "3521": 0.35,  # Broadcasting and Audio-visual Technicians
    "1323": 0.34,  # Construction Managers
    "1343": 0.34,  # Aged Care Service Managers
    "2353": 0.34,  # Other Language Teachers
    "3155": 0.34,  # Air Traffic Safety Electronics Technicians
    "2262": 0.33,  # Pharmacists
    "2359": 0.33,  # Teaching Professionals Not Elsewhere Classified
    "3412": 0.33,  # Social Work Associate Professionals
    "1431": 0.32,  # Sports, Recreation and Cultural Centre Managers
    "2230": 0.32,  # Traditional and Complementary Medicine Professionals
    "3351": 0.32,  # Customs and Border Inspectors
    "5113": 0.32,  # Travel Guides
    "8219": 0.32,  # Assemblers Not Elsewhere Classified
    "2655": 0.31,  # Actors
    "3135": 0.31,  # Metal Production Process Controllers
    "3154": 0.31,  # Air Traffic Controllers
    "3212": 0.31,  # Medical and Pathology Laboratory Technicians
    "7515": 0.31,  # Food and Beverage Tasters and Graders
    "7543": 0.31,  # Product Graders and Testers (except Foods and Beverages)
    "1341": 0.30,  # Child Care Service Managers
    "2222": 0.30,  # Midwifery Professionals
    "3213": 0.30,  # Pharmaceutical Technicians and Assistants
    "3259": 0.30,  # Health Associate Professionals Not Elsewhere Classified
    "5161": 0.30,  # Astrologers, Fortune-tellers and Related Workers
    "9629": 0.29,  # Elementary Workers Not Elsewhere Classified
    "2264": 0.28,  # Physiotherapists
    "5131": 0.28,  # Waiters
    "8171": 0.28,  # Pulp and Papermaking Plant Operators
    "8212": 0.28,  # Electrical and Electronic Equipment Assemblers
    "1311": 0.27,  # Agricultural and Forestry Production Managers
    "5153": 0.27,  # Building Caretakers
    "8211": 0.27,  # Mechanical Machinery Assemblers
    "5112": 0.25,  # Transport Conductors
    "5322": 0.25,  # Home-based Personal Care Workers
    "8321": 0.25,  # Motorcycle Drivers
    "5245": 0.24,  # Service Station Attendants
    "8332": 0.24,  # Heavy Truck and Lorry Drivers
    "3221": 0.22,  # Nursing Associate Professionals
    
    # Not Exposed - Very low or no exposure
    "1213": 0.36,  # Policy and Planning Managers
    "2144": 0.32,  # Mechanical Engineers
    "3116": 0.32,  # Chemical Engineering Technicians
    "1111": 0.31,  # Legislators
    "2151": 0.31,  # Electrical Engineers
    "2612": 0.31,  # Judges
    "2142": 0.30,  # Civil Engineers
    "2149": 0.30,  # Engineering Professionals Not Elsewhere Classified
    "2330": 0.30,  # Secondary Education Teachers
    "2132": 0.29,  # Farming, Forestry and Fisheries Advisers
    "2146": 0.29,  # Mining Engineers, Metallurgists and Related Professionals
    "2211": 0.29,  # Generalist Medical Practitioners
    "3121": 0.29,  # Mining Supervisors
    "3133": 0.29,  # Chemical Processing Plant Controllers
    "3134": 0.29,  # Petroleum and Natural Gas Refining Plant Operators
    "3152": 0.29,  # Ships' Deck Officers and Pilots
    "2263": 0.28,  # Environmental and Occupational Health Professionals
    "2352": 0.28,  # Special Needs Teachers
    "2635": 0.28,  # Social Work and Counselling Professionals
    "2652": 0.28,  # Musicians, Singers and Composers
    "3112": 0.28,  # Civil Engineering Technicians
    "3117": 0.28,  # Mining and metallurgical technicians
    "3123": 0.28,  # Construction Supervisors
    "3131": 0.28,  # Power Production Plant Operators
    "2212": 0.27,  # Specialist Medical Practitioners
    "3113": 0.27,  # Electrical Engineering Technicians
    "3132": 0.27,  # Incinerator and Water Treatment Plant Operators
    "3153": 0.27,  # Aircraft Pilots and Related Associate Professionals
    "8132": 0.27,  # Photographic Products Machine Operators
    "2341": 0.26,  # Primary School Teachers
    "3111": 0.26,  # Chemical and Physical Science Technicians
    "3115": 0.26,  # Mechanical Engineering Technicians
    "3119": 0.26,  # Physical and Engineering Science Technicians NEC
    "3142": 0.26,  # Agricultural Technicians
    "5132": 0.26,  # Bartenders
    "8121": 0.26,  # Metal Processing Plant Operators
    "2221": 0.25,  # Nursing Professionals
    "3423": 0.25,  # Fitness and Recreation Instructors and Programme Leaders
    "3434": 0.25,  # Chefs
    "5241": 0.25,  # Fashion and Other Models
    "7322": 0.25,  # Printers
    "7421": 0.25,  # Electronics Mechanics and Servicers
    "2266": 0.24,  # Audiologists and Speech Therapists
    "2267": 0.24,  # Optometrists and Ophthalmic Opticians
    "3254": 0.24,  # Dispensing Opticians
    "3257": 0.24,  # Environmental and Occupational Health Inspectors
    "5246": 0.24,  # Food Service Counter Attendants
    "5312": 0.24,  # Teachers' Aides
    "7422": 0.24,  # ICT Installers and Servicers
    "8131": 0.24,  # Chemical Products Plant and Machine Operators
    "1113": 0.23,  # Traditional Chiefs and Heads of Villages
    "2240": 0.23,  # Paramedical Practitioners
    "3151": 0.23,  # Ships' Engineers
    "3355": 0.23,  # Police Inspectors and Detectives
    "3421": 0.23,  # Athletes and Sports Players
    "8114": 0.23,  # Cement, Stone and Other Mineral Products Machine Operators
    "1312": 0.22,  # Aquaculture and Fisheries Production Managers
    "3211": 0.22,  # Medical Imaging and Therapeutic Equipment Technicians
    "3253": 0.22,  # Community Health Workers
    "3258": 0.22,  # Ambulance Workers
    "5111": 0.22,  # Travel Attendants and Travel Stewards
    "5151": 0.22,  # Cleaning and Housekeeping Supervisors
    "5162": 0.22,  # Companions and Valets
    "5212": 0.22,  # Street Food Salespersons
    "6123": 0.22,  # Apiarists and Sericulturists
    "6221": 0.22,  # Aquaculture Workers
    "7323": 0.22,  # Print Finishing and Binding Workers
    "7513": 0.22,  # Dairy Products Makers
    "7521": 0.22,  # Wood Treaters
    "7523": 0.22,  # Woodworking Machine Tool Setters and Operators
    "8183": 0.22,  # Packing, Bottling and Labelling Machine Operators
    "2342": 0.21,  # Early Childhood Educators
    "2651": 0.21,  # Visual Artists
    "3143": 0.21,  # Forestry Technicians
    "5169": 0.21,  # Personal Services Workers Not Elsewhere Classified
    "7127": 0.21,  # Air Conditioning and Refrigeration Mechanics
    "7213": 0.21,  # Sheet Metal Workers
    "7311": 0.21,  # Precision-instrument Makers and Repairers
    "8112": 0.21,  # Mineral and Stone Processing Plant Operators
    "8154": 0.21,  # Bleaching, Dyeing and Fabric Cleaning Machine Operators
    "9331": 0.21,  # Hand and Pedal Vehicle Drivers
    "2269": 0.20,  # Health Professionals Not Elsewhere Classified
    "3222": 0.20,  # Midwifery Associate Professionals
    "5152": 0.20,  # Domestic Housekeepers
    "5165": 0.20,  # Driving Instructors
    "5414": 0.20,  # Security Guards
    "5419": 0.20,  # Protective Services Workers Not Elsewhere Classified
    "6129": 0.20,  # Animal Producers Not Elsewhere Classified
    "7222": 0.20,  # Toolmakers and Related Workers
    "8122": 0.20,  # Metal Finishing, Plating and Coating Machine Operators
    "8182": 0.20,  # Steam Engine and Boiler Operators
    "8311": 0.20,  # Locomotive Engine Drivers
    "8344": 0.20,  # Lifting Truck Operators
    "9321": 0.20,  # Hand Packers
    "9334": 0.20,  # Shelf Fillers
    "9520": 0.20,  # Street Vendors (excluding Food)
    "2653": 0.19,  # Dancers and Choreographers
    "3230": 0.19,  # Traditional and Complementary Medicine Associate Professionals
    "5311": 0.19,  # Child Care Workers
    "6122": 0.19,  # Poultry Producers
    "6130": 0.19,  # Mixed Crop and Animal Producers
    "7232": 0.19,  # Aircraft Engine Mechanics and Repairers
    "7315": 0.19,  # Glass Makers, Cutters, Grinders and Finishers
    "7411": 0.19,  # Building and Related Electricians
    "8113": 0.19,  # Well Drillers and Borers and Related Workers
    "3214": 0.18,  # Medical and Dental Prosthetic Technicians
    "5120": 0.18,  # Cooks
    "5142": 0.18,  # Beauticians and Related Workers
    "5411": 0.18,  # Fire Fighters
    "6111": 0.18,  # Field Crop and Vegetable Growers
    "6113": 0.18,  # Gardeners, Horticultural and Nursery Growers
    "6223": 0.18,  # Deep-sea Fishery Workers
    "7126": 0.18,  # Plumbers and Pipe Fitters
    "7223": 0.18,  # Metal Working Machine Tool Setters and Operators
    "7231": 0.18,  # Motor Vehicle Mechanics and Repairers
    "7313": 0.18,  # Jewellery and Precious Metal Workers
    "7314": 0.18,  # Potters and Related Workers
    "7316": 0.18,  # Sign Writers, Decorative Painters, Engravers and Etchers
    "7534": 0.18,  # Upholsterers and Related Workers
    "8141": 0.18,  # Rubber Products Machine Operators
    "8143": 0.18,  # Paper Products Machine Operators
    "8331": 0.18,  # Bus and Tram Drivers
    "8343": 0.18,  # Crane, hoist and related plant operators
    "9411": 0.18,  # Fast Food Preparers
    "9510": 0.18,  # Street and Related Service Workers
    "9612": 0.18,  # Refuse Sorters
    "2636": 0.17,  # Religious Professionals
    "3255": 0.17,  # Physiotherapy Technicians and Assistants
    "5141": 0.17,  # Hairdressers
    "5163": 0.17,  # Undertakers and Embalmers
    "6112": 0.17,  # Tree and Shrub Crop Growers
    "6114": 0.17,  # Mixed Crop Growers
    "6121": 0.17,  # Livestock and Dairy Producers
    "6222": 0.17,  # Inland and Coastal Waters Fishery Workers
    "7221": 0.17,  # Blacksmiths, Hammersmiths and Forging Press Workers
    "7224": 0.17,  # Metal Polishers, Wheel Grinders and Tool Sharpeners
    "7233": 0.17,  # Agricultural and Industrial Machinery Mechanics
    "7412": 0.17,  # Electrical Mechanics and Fitters
    "7512": 0.17,  # Bakers, Pastry-cooks and Confectionery Makers
    "7532": 0.17,  # Garment and Related Patternmakers and Cutters
    "7536": 0.17,  # Shoemakers and Related Workers
    "8111": 0.17,  # Miners and Quarriers
    "8142": 0.17,  # Plastic Products Machine Operators
    "8181": 0.17,  # Glass and Ceramics Plant Operators
    "8312": 0.17,  # Railway Brake, Signal and Switch Operators
    "3251": 0.16,  # Dental Assistants and Therapists
    "7522": 0.16,  # Cabinet-makers and Related Workers
    "7541": 0.16,  # Underwater Divers
    "8152": 0.16,  # Weaving and Knitting Machine Operators
    "8156": 0.16,  # Shoemaking and Related Machine Operators
    "8157": 0.16,  # Laundry Machine Operators
    "8159": 0.16,  # Textile, Fur and Leather Products Machine Operators NEC
    "2261": 0.15,  # Dentists
    "5329": 0.15,  # Personal Care Workers in Health Services Not Elsewhere Classified
    "7413": 0.15,  # Electrical Line Installers and Repairers
    "7514": 0.15,  # Fruit, Vegetable and Related Preservers
    "7531": 0.15,  # Tailors, Dressmakers, Furriers and Hatters
    "8151": 0.15,  # Fibre Preparing, Spinning and Winding Machine Operators
    "8153": 0.15,  # Sewing Machine Operators
    "8155": 0.15,  # Fur and Leather Preparing Machine Operators
    "8160": 0.15,  # Food and Related Products Machine Operators
    "2250": 0.14,  # Veterinarians
    "3240": 0.14,  # Veterinary Technicians and Assistants
    "5164": 0.14,  # Pet Groomers and Animal Care Workers
    "5321": 0.14,  # Health Care Assistants
    "5412": 0.14,  # Police Officers
    "5413": 0.14,  # Prison Guards
    "7111": 0.14,  # House Builders
    "7125": 0.14,  # Glaziers
    "7312": 0.14,  # Musical Instrument Makers and Tuners
    "7317": 0.14,  # Handicraft Workers in Wood, Basketry and Related Materials
    "7516": 0.14,  # Tobacco Preparers and Tobacco Products Makers
    "7549": 0.14,  # Craft and Related Workers not Elsewhere Classified
    "8172": 0.14,  # Wood Processing Plant Operators
    "8350": 0.14,  # Ships' Deck Crews and Related Workers
    "9111": 0.14,  # Domestic Cleaners and Helpers
    "9121": 0.14,  # Hand Launderers and Pressers
    "9333": 0.14,  # Freight Handlers
    "2659": 0.13,  # Creative and Performing Artists Not Elsewhere Classified
    "6310": 0.13,  # Subsistence Crop Farmers
    "6320": 0.13,  # Subsistence Livestock Farmers
    "7115": 0.13,  # Carpenters and Joiners
    "7121": 0.13,  # Roofers
    "7124": 0.13,  # Insulation Workers
    "7131": 0.13,  # Painters and Related Workers
    "7211": 0.13,  # Metal Moulders and Coremakers
    "7212": 0.13,  # Welders and Flame Cutters
    "7215": 0.13,  # Riggers and Cable Splicers
    "7234": 0.13,  # Bicycle and Related Repairers
    "7318": 0.13,  # Handicraft Workers in Textile, Leather and Related Materials
    "7511": 0.13,  # Butchers, Fishmongers and Related Food Preparers
    "7544": 0.13,  # Fumigators and Other Pest and Weed Controllers
    "8342": 0.13,  # Earthmoving and Related Plant Operators
    "9332": 0.13,  # Drivers of Animal-drawn Vehicles and Machinery
    "9412": 0.13,  # Kitchen Helpers
    "3413": 0.12,  # Religious Associate Professionals
    "6210": 0.12,  # Forestry and Related Workers
    "6330": 0.12,  # Subsistence Mixed Crop and Livestock Farmers
    "6340": 0.12,  # Subsistence Fishers, Hunters, Trappers and Gatherers
    "7132": 0.12,  # Spray Painters and Varnishers
    "7533": 0.12,  # Sewing, Embroidery and Related Workers
    "7542": 0.12,  # Shotfirers and Blasters
    "8341": 0.12,  # Mobile Farm and Forestry Plant Operators
    "9112": 0.12,  # Cleaners and Helpers in Offices, Hotels and Other Establishments
    "9212": 0.12,  # Livestock Farm Labourers
    "9214": 0.12,  # Garden and Horticultural Labourers
    "9329": 0.12,  # Manufacturing Labourers Not Elsewhere Classified
    "7113": 0.11,  # Stonemasons, Stone Cutters, Splitters and Carvers
    "7123": 0.11,  # Plasterers
    "7214": 0.11,  # Structural Metal Preparers and Erectors
    "7535": 0.11,  # Pelt Dressers, Tanners and Fellmongers
    "9123": 0.11,  # Window Cleaners
    "9213": 0.11,  # Mixed Crop and Livestock Farm Labourers
    "9216": 0.11,  # Fishery and Aquaculture Labourers
    "9311": 0.11,  # Mining and Quarrying Labourers
    "9622": 0.11,  # Odd Job Persons
    "7114": 0.10,  # Concrete Placers, Concrete Finishers and Related Workers
    "7122": 0.10,  # Floor Layers and Tile Setters
    "9129": 0.10,  # Other Cleaning Workers
    "6224": 0.09,  # Hunters and Trappers
    "7112": 0.09,  # Bricklayers and Related Workers
    "7119": 0.09,  # Building Frame and Related Trades Workers NEC
    "7133": 0.09,  # Building Structure Cleaners
    "9122": 0.09,  # Vehicle Cleaners
    "9211": 0.09,  # Crop Farm Labourers
    "9215": 0.09,  # Forestry Labourers
    "9312": 0.09,  # Civil Engineering Labourers
    "9313": 0.09,  # Building Construction Labourers
    "9611": 0.09,  # Garbage and Recycling Collectors
    "9613": 0.09,  # Sweepers and Related Labourers
    "9624": 0.09,  # Water and Firewood Collectors
}


def load_crosswalk():
    """Load and process ISCO-SOC crosswalk"""
    print("Loading ISCO-SOC crosswalk...")
    
    # Skip the header rows and load the data
    df = pd.read_csv(CROSSWALK_FILE, skiprows=5)
    
    # Rename columns for clarity
    df.columns = ['ISCO_Code', 'ISCO_Title', 'part', 'SOC_Code', 'SOC_Title', 'Comment']
    
    # Clean SOC codes - remove spaces
    df['SOC_Code'] = df['SOC_Code'].str.strip()
    
    # Convert ISCO codes to 4-digit strings
    df['ISCO_Code'] = df['ISCO_Code'].astype(str).str.zfill(4)
    
    print(f"Loaded {len(df)} ISCO-SOC mappings")
    return df


def create_soc_exposure_mapping(crosswalk_df):
    """Create mapping from SOC codes to AI exposure scores using ISCO crosswalk"""
    print("\nCreating SOC to AI exposure score mapping...")
    
    # Add AI scores to crosswalk
    crosswalk_df['AI_Exposure_Score'] = crosswalk_df['ISCO_Code'].map(ILO_SCORES)
    
    # Group by SOC code and calculate mean exposure score
    # (Some SOC codes map to multiple ISCO codes)
    soc_exposure = crosswalk_df.groupby('SOC_Code').agg({
        'AI_Exposure_Score': 'mean',
        'ISCO_Code': 'count'  # Count number of ISCO mappings
    }).reset_index()
    
    soc_exposure.columns = ['SOC_Code', 'AI_Exposure_Score', 'num_isco_mappings']
    
    # Drop rows with no exposure score
    soc_exposure = soc_exposure.dropna(subset=['AI_Exposure_Score'])
    
    print(f"Created mappings for {len(soc_exposure)} SOC codes")
    print(f"Score range: {soc_exposure['AI_Exposure_Score'].min():.2f} - {soc_exposure['AI_Exposure_Score'].max():.2f}")
    
    return soc_exposure


def update_occupation_panel(soc_exposure_df):
    """Update occupation_panel.csv with new AI exposure scores"""
    print("\nLoading occupation panel...")
    
    # Load the panel data
    df = pd.read_csv(OCCUPATION_PANEL_FILE)
    
    print(f"Loaded panel with {len(df)} rows")
    print(f"Unique occupations: {df['Occupation_Code'].nunique()}")
    print(f"Years: {sorted(df['Year'].unique())}")
    
    # STEP 1: Update 2015-2017 data using SOC codes
    print("\n" + "="*80)
    print("STEP 1: Updating 2015-2017 data using SOC codes")
    print("="*80)
    
    # Extract base SOC code (first 7 characters, e.g., '11-1021' from '11-1021.00')
    df['SOC_Base'] = df['Occupation_Code'].str[:7]
    
    # Create mapping dictionary from SOC codes to scores
    score_dict = soc_exposure_df.set_index('SOC_Code')['AI_Exposure_Score'].to_dict()
    
    # Update AI_Exposure_Score for rows with valid SOC codes
    df['AI_Exposure_Score'] = df['SOC_Base'].map(score_dict)
    
    matched_soc = df['AI_Exposure_Score'].notna().sum()
    print(f"Matched {matched_soc:,} rows using SOC codes")
    
    # STEP 2: Create occupation name to score mapping from 2015-2017 data
    print("\n" + "="*80)
    print("STEP 2: Creating occupation name → score mapping from 2015-2017")
    print("="*80)
    
    # Get unique occupation name to score mappings from years with SOC codes
    occ_name_mapping = df[df['AI_Exposure_Score'].notna()][['Occupation', 'AI_Exposure_Score']].drop_duplicates()
    occ_name_dict = occ_name_mapping.set_index('Occupation')['AI_Exposure_Score'].to_dict()
    
    print(f"Created {len(occ_name_dict)} occupation name mappings")
    
    # STEP 3: Apply occupation name mapping to 2018-2024 data (rows still missing scores)
    print("\n" + "="*80)
    print("STEP 3: Applying occupation name mapping to 2018-2024")
    print("="*80)
    
    # Fill missing scores using occupation name mapping
    missing_mask = df['AI_Exposure_Score'].isna()
    df.loc[missing_mask, 'AI_Exposure_Score'] = df.loc[missing_mask, 'Occupation'].map(occ_name_dict)
    
    matched_by_name = df['AI_Exposure_Score'].notna().sum() - matched_soc
    print(f"Additional {matched_by_name:,} rows matched using occupation names")
    
    # Drop temporary column
    df = df.drop('SOC_Base', axis=1)
    
    # FINAL REPORT
    print("\n" + "="*80)
    print("FINAL COVERAGE REPORT")
    print("="*80)
    
    total_matched = df['AI_Exposure_Score'].notna().sum()
    total_unmatched = df['AI_Exposure_Score'].isna().sum()
    
    print(f"\nTotal matched: {total_matched:,} rows ({total_matched/len(df)*100:.1f}%)")
    print(f"Total unmatched: {total_unmatched:,} rows ({total_unmatched/len(df)*100:.1f}%)")
    
    # Coverage by year
    print("\nCoverage by year:")
    for year in sorted(df['Year'].unique()):
        year_df = df[df['Year'] == year]
        year_matched = year_df['AI_Exposure_Score'].notna().sum()
        year_total = len(year_df)
        print(f"  {year}: {year_matched:,}/{year_total:,} ({year_matched/year_total*100:.1f}%)")
    
    if total_matched > 0:
        print(f"\nAI Exposure Score statistics:")
        print(f"  Mean: {df['AI_Exposure_Score'].mean():.3f}")
        print(f"  Median: {df['AI_Exposure_Score'].median():.3f}")
        print(f"  Std Dev: {df['AI_Exposure_Score'].std():.3f}")
        print(f"  Min: {df['AI_Exposure_Score'].min():.3f}")
        print(f"  Max: {df['AI_Exposure_Score'].max():.3f}")
    
    # Show sample of unmatched occupations if any remain
    if total_unmatched > 0:
        print(f"\nSample of unmatched occupations:")
        unmatched_occs = df[df['AI_Exposure_Score'].isna()]['Occupation'].unique()[:10]
        for occ in unmatched_occs:
            print(f"  - {occ}")
    
    # Save updated file
    output_file = OCCUPATION_PANEL_FILE
    print(f"\nSaving updated file to: {output_file}")
    df.to_csv(output_file, index=False)
    
    return df


def main():
    """Main execution function"""
    print("=" * 80)
    print("Updating AI Exposure Scores in Occupation Panel")
    print("=" * 80)
    
    # Load crosswalk
    crosswalk_df = load_crosswalk()
    
    # Create SOC exposure mapping
    soc_exposure_df = create_soc_exposure_mapping(crosswalk_df)
    
    # Update occupation panel
    updated_df = update_occupation_panel(soc_exposure_df)
    
    print("\n" + "=" * 80)
    print("Update completed successfully!")
    print("=" * 80)
    
    # Show some example mappings
    print("\nSample of updated occupations:")
    sample = updated_df[updated_df['AI_Exposure_Score'].notna()][
        ['Occupation_Code', 'Occupation', 'AI_Exposure_Score', 'Year']
    ].drop_duplicates(subset=['Occupation_Code']).head(10)
    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()
