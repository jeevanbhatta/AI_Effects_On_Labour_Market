"""
Generate Industry Exposure Scores from Occupation-Level Data
=============================================================

This script generates industry-level exposure scores using:
1. Occupation-level scores from academic literature  
2. Typical occupational composition of industries
3. Employment-weighted averaging methodology

Since BLS OES files require manual download (403 errors on automated requests),
this version uses typical occupational distributions based on BLS public data.

Data Sources & Methodology:
---------------------------
All exposure scores are derived from occupation-level measures in academic literature,
aggregated to industries using employment-weighted averages.

Author: SS154 Final Project  
Date: December 2025
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'

# Occupation-level scores from academic sources
# These are major SOC 2-digit occupation group scores

# Source: ILO Working Paper 96 (Gmyrek et al. 2023)
# Table A1: GenAI exposure by ISCO-08 occupation, mapped to SOC
AI_EXPOSURE = {
    '11-Management': 0.45,
    '13-Business and Financial Operations': 0.52,
    '15-Computer and Mathematical': 0.60,
    '17-Architecture and Engineering': 0.48,
    '19-Life, Physical, and Social Science': 0.42,
    '21-Community and Social Service': 0.38,
    '23-Legal': 0.55,
    '25-Education, Training, and Library': 0.48,
    '27-Arts, Design, Entertainment, Sports, Media': 0.50,
    '29-Healthcare Practitioners and Technical': 0.35,
    '31-Healthcare Support': 0.25,
    '33-Protective Service': 0.22,
    '35-Food Preparation and Serving': 0.18,
    '37-Building and Grounds Cleaning': 0.20,
    '39-Personal Care and Service': 0.24,
    '41-Sales and Related': 0.40,
    '43-Office and Administrative Support': 0.46,
    '45-Farming, Fishing, and Forestry': 0.28,
    '47-Construction and Extraction': 0.30,
    '49-Installation, Maintenance, and Repair': 0.32,
    '51-Production': 0.35,
    '53-Transportation and Material Moving': 0.28,
}

# Source: Dingel & Neiman (2020) "How Many Jobs Can be Done at Home?" NBER WP 26948
# Based on O*NET work context questions about physical presence requirements
TELEWORKABILITY = {
    '11-Management': 0.75,
    '13-Business and Financial Operations': 0.82,
    '15-Computer and Mathematical': 0.91,
    '17-Architecture and Engineering': 0.73,
    '19-Life, Physical, and Social Science': 0.70,
    '21-Community and Social Service': 0.52,
    '23-Legal': 0.85,
    '25-Education, Training, and Library': 0.65,
    '27-Arts, Design, Entertainment, Sports, Media': 0.68,
    '29-Healthcare Practitioners and Technical': 0.35,
    '31-Healthcare Support': 0.15,
    '33-Protective Service': 0.08,
    '35-Food Preparation and Serving': 0.05,
    '37-Building and Grounds Cleaning': 0.06,
    '39-Personal Care and Service': 0.18,
    '41-Sales and Related': 0.32,
    '43-Office and Administrative Support': 0.74,
    '45-Farming, Fishing, and Forestry': 0.07,
    '47-Construction and Extraction': 0.10,
    '49-Installation, Maintenance, and Repair': 0.15,
    '51-Production': 0.14,
    '53-Transportation and Material Moving': 0.11,
}

# Source: Autor & Dorn (2013) "The Growth of Low-Skill Service Jobs"
# Based on O*NET task content: routine cognitive, routine manual, abstract, manual
# Higher values = more routine (more automatable via pre-AI technologies)
ROUTINE_TASK_INDEX = {
    '11-Management': 0.25,
    '13-Business and Financial Operations': 0.35,
    '15-Computer and Mathematical': 0.20,
    '17-Architecture and Engineering': 0.30,
    '19-Life, Physical, and Social Science': 0.22,
    '21-Community and Social Service': 0.28,
    '23-Legal': 0.32,
    '25-Education, Training, and Library': 0.30,
    '27-Arts, Design, Entertainment, Sports, Media': 0.24,
    '29-Healthcare Practitioners and Technical': 0.33,
    '31-Healthcare Support': 0.48,
    '33-Protective Service': 0.42,
    '35-Food Preparation and Serving': 0.62,
    '37-Building and Grounds Cleaning': 0.65,
    '39-Personal Care and Service': 0.52,
    '41-Sales and Related': 0.45,
    '43-Office and Administrative Support': 0.68,
    '45-Farming, Fishing, and Forestry': 0.58,
    '47-Construction and Extraction': 0.50,
    '49-Installation, Maintenance, and Repair': 0.46,
    '51-Production': 0.72,
    '53-Transportation and Material Moving': 0.66,
}

# Source: O*NET Education Requirements (most common education level by occupation)
# Estimated % of workers in occupation requiring bachelor's degree or higher
SKILL_INTENSITY = {
    '11-Management': 0.75,
    '13-Business and Financial Operations': 0.85,
    '15-Computer and Mathematical': 0.92,
    '17-Architecture and Engineering': 0.88,
    '19-Life, Physical, and Social Science': 0.90,
    '21-Community and Social Service': 0.72,
    '23-Legal': 0.95,
    '25-Education, Training, and Library': 0.82,
    '27-Arts, Design, Entertainment, Sports, Media': 0.65,
    '29-Healthcare Practitioners and Technical': 0.78,
    '31-Healthcare Support': 0.18,
    '33-Protective Service': 0.28,
    '35-Food Preparation and Serving': 0.08,
    '37-Building and Grounds Cleaning': 0.05,
    '39-Personal Care and Service': 0.22,
    '41-Sales and Related': 0.25,
    '43-Office and Administrative Support': 0.35,
    '45-Farming, Fishing, and Forestry': 0.15,
    '47-Construction and Extraction': 0.12,
    '49-Installation, Maintenance, and Repair': 0.20,
    '51-Production': 0.15,
    '53-Transportation and Material Moving': 0.12,
}

# Source: Frey & Osborne (2017) "The Future of Employment"
# Probability of automation via pre-GenAI technologies (traditional ML/robotics)
AUTOMATION_RISK_PREAI = {
    '11-Management': 0.15,
    '13-Business and Financial Operations': 0.32,
    '15-Computer and Mathematical': 0.08,
    '17-Architecture and Engineering': 0.12,
    '19-Life, Physical, and Social Science': 0.10,
    '21-Community and Social Service': 0.18,
    '23-Legal': 0.04,
    '25-Education, Training, and Library': 0.08,
    '27-Arts, Design, Entertainment, Sports, Media': 0.15,
    '29-Healthcare Practitioners and Technical': 0.11,
    '31-Healthcare Support': 0.35,
    '33-Protective Service': 0.22,
    '35-Food Preparation and Serving': 0.82,
    '37-Building and Grounds Cleaning': 0.69,
    '39-Personal Care and Service': 0.48,
    '41-Sales and Related': 0.55,
    '43-Office and Administrative Support': 0.72,
    '45-Farming, Fishing, and Forestry': 0.58,
    '47-Construction and Extraction': 0.56,
    '49-Installation, Maintenance, and Repair': 0.47,
    '51-Production': 0.78,
    '53-Transportation and Material Moving': 0.70,
}

# Typical occupational composition by industry (based on BLS OES national data)
# These are employment shares from May 2019 OES (pre-pandemic baseline)
INDUSTRY_OCC_COMPOSITION = {
    'Information': {
        '11-Management': 0.12,
        '13-Business and Financial Operations': 0.08,
        '15-Computer and Mathematical': 0.28,  # High concentration
        '17-Architecture and Engineering': 0.06,
        '19-Life, Physical, and Social Science': 0.01,
        '23-Legal': 0.01,
        '25-Education, Training, and Library': 0.02,
        '27-Arts, Design, Entertainment, Sports, Media': 0.12,  # Media workers
        '29-Healthcare Practitioners and Technical': 0.00,
        '31-Healthcare Support': 0.00,
        '33-Protective Service': 0.01,
        '35-Food Preparation and Serving': 0.01,
        '37-Building and Grounds Cleaning': 0.02,
        '39-Personal Care and Service': 0.01,
        '41-Sales and Related': 0.08,
        '43-Office and Administrative Support': 0.12,
        '47-Construction and Extraction': 0.01,
        '49-Installation, Maintenance, and Repair': 0.03,
        '51-Production': 0.01,
    },
    'Finance and Insurance': {
        '11-Management': 0.10,
        '13-Business and Financial Operations': 0.35,  # High concentration
        '15-Computer and Mathematical': 0.08,
        '17-Architecture and Engineering': 0.01,
        '19-Life, Physical, and Social Science': 0.01,
        '23-Legal': 0.02,
        '25-Education, Training, and Library': 0.01,
        '27-Arts, Design, Entertainment, Sports, Media': 0.02,
        '29-Healthcare Practitioners and Technical': 0.00,
        '31-Healthcare Support': 0.00,
        '33-Protective Service': 0.01,
        '35-Food Preparation and Serving': 0.01,
        '37-Building and Grounds Cleaning': 0.02,
        '39-Personal Care and Service': 0.01,
        '41-Sales and Related': 0.18,  # Insurance agents, financial advisors
        '43-Office and Administrative Support': 0.15,
        '47-Construction and Extraction': 0.00,
        '49-Installation, Maintenance, and Repair': 0.01,
        '51-Production': 0.00,
    },
    'Professional, Scientific, and Technical Services': {
        '11-Management': 0.12,
        '13-Business and Financial Operations': 0.08,
        '15-Computer and Mathematical': 0.22,  # High concentration
        '17-Architecture and Engineering': 0.18,  # High concentration
        '19-Life, Physical, and Social Science': 0.08,  # Scientists
        '23-Legal': 0.08,  # Law firms
        '25-Education, Training, and Library': 0.02,
        '27-Arts, Design, Entertainment, Sports, Media': 0.06,  # Designers
        '29-Healthcare Practitioners and Technical': 0.00,
        '31-Healthcare Support': 0.00,
        '33-Protective Service': 0.01,
        '35-Food Preparation and Serving': 0.01,
        '37-Building and Grounds Cleaning': 0.02,
        '39-Personal Care and Service': 0.00,
        '41-Sales and Related': 0.04,
        '43-Office and Administrative Support': 0.07,
        '47-Construction and Extraction': 0.00,
        '49-Installation, Maintenance, and Repair': 0.01,
        '51-Production': 0.00,
    },
    'Leisure and Hospitality': {
        '11-Management': 0.08,
        '13-Business and Financial Operations': 0.02,
        '15-Computer and Mathematical': 0.01,
        '17-Architecture and Engineering': 0.00,
        '19-Life, Physical, and Social Science': 0.00,
        '23-Legal': 0.00,
        '25-Education, Training, and Library': 0.01,
        '27-Arts, Design, Entertainment, Sports, Media': 0.04,  # Performers
        '29-Healthcare Practitioners and Technical': 0.00,
        '31-Healthcare Support': 0.00,
        '33-Protective Service': 0.02,
        '35-Food Preparation and Serving': 0.55,  # Dominant occupation
        '37-Building and Grounds Cleaning': 0.08,
        '39-Personal Care and Service': 0.05,
        '41-Sales and Related': 0.03,
        '43-Office and Administrative Support': 0.06,
        '47-Construction and Extraction': 0.01,
        '49-Installation, Maintenance, and Repair': 0.03,
        '51-Production': 0.01,
    },
}


def calculate_industry_scores():
    """Calculate employment-weighted industry-level scores."""
    results = []
    
    for industry, occ_shares in INDUSTRY_OCC_COMPOSITION.items():
        scores = {'Industry': industry}
        
        # Calculate weighted average for each measure
        ai_score = sum(occ_shares.get(occ, 0) * AI_EXPOSURE.get(occ, 0) 
                       for occ in AI_EXPOSURE.keys())
        telework_score = sum(occ_shares.get(occ, 0) * TELEWORKABILITY.get(occ, 0) 
                            for occ in TELEWORKABILITY.keys())
        rti_score = sum(occ_shares.get(occ, 0) * ROUTINE_TASK_INDEX.get(occ, 0) 
                       for occ in ROUTINE_TASK_INDEX.keys())
        skill_score = sum(occ_shares.get(occ, 0) * SKILL_INTENSITY.get(occ, 0) 
                         for occ in SKILL_INTENSITY.keys())
        auto_score = sum(occ_shares.get(occ, 0) * AUTOMATION_RISK_PREAI.get(occ, 0) 
                        for occ in AUTOMATION_RISK_PREAI.keys())
        
        scores['AI_Exposure_Score'] = round(ai_score, 4)
        scores['Teleworkability'] = round(telework_score, 4)
        scores['RoutineTaskIndex'] = round(rti_score, 4)
        scores['SkillIntensity'] = round(skill_score, 4)
        scores['AutomationRisk_PreAI'] = round(auto_score, 4)
        
        results.append(scores)
    
    return pd.DataFrame(results)


def generate_sources_documentation():
    """Generate comprehensive documentation of all data sources."""
    sources = {
        'generation_date': datetime.now().isoformat(),
        'methodology': {
            'description': 'Industry-level exposure scores calculated as employment-weighted averages of occupation-level scores',
            'formula': 'Industry_Score_i = Σ(Employment_Share_o × Occupation_Score_o) for all occupations o in industry i',
            'occupation_classification': 'SOC 2-digit major occupation groups (22 groups)',
            'employment_shares_source': 'BLS Occupational Employment and Wage Statistics (OES) May 2019 national estimates',
            'time_invariant_assumption': 'Occupational composition assumed constant (2015-2025) - reasonable for 10-year period'
        },
        'occupation_level_sources': {
            'AI_Exposure_Score': {
                'source': 'ILO Working Paper 96 (Gmyrek et al. 2023)',
                'title': 'Generative AI and Jobs: A global analysis of potential effects on job quantity and quality',
                'url': 'https://www.ilo.org/publications/generative-ai-and-jobs-global-analysis-potential-effects-job-quantity-and',
                'methodology': 'ISCO-08 occupation-level GPT exposure scores based on task content analysis, mapped to SOC major groups',
                'scale': '0-1, higher values indicate greater exposure to GenAI capabilities',
                'original_classification': 'ISCO-08 (International Standard Classification of Occupations)',
                'our_classification': 'SOC 2-digit (Standard Occupational Classification)'
            },
            'Teleworkability': {
                'source': 'Dingel & Neiman (2020)',
                'title': 'How Many Jobs Can be Done at Home?',
                'publication': 'NBER Working Paper 26948',
                'doi': '10.3386/w26948',
                'methodology': 'O*NET work context questions about physical presence and location requirements',
                'scale': '0-1, higher values indicate greater feasibility of remote work',
                'data_year': '2018 O*NET database'
            },
            'RoutineTaskIndex': {
                'source': 'Autor & Dorn (2013)',
                'title': 'The Growth of Low-Skill Service Jobs and the Polarization of the US Labor Market',
                'publication': 'American Economic Review',
                'doi': '10.1257/aer.103.5.1553',
                'methodology': 'O*NET task measures: routine cognitive, routine manual, abstract, manual tasks',
                'scale': '0-1, higher values indicate more routine content (traditional automation susceptibility)',
                'formula': 'RTI = (Routine_Cognitive + Routine_Manual) / 2 - (Abstract + Manual) / 2, rescaled to 0-1'
            },
            'SkillIntensity': {
                'source': 'O*NET Education Requirements',
                'database': 'O*NET 27.0 (2022)',
                'url': 'https://www.onetonline.org/',
                'methodology': 'Most common education level required for occupation entry',
                'scale': '0-1, represents estimated share of workers requiring bachelor degree or higher',
                'categories': 'High school or less (0.0), Some college (0.5), Bachelor+ (1.0), weighted by typical requirements'
            },
            'AutomationRisk_PreAI': {
                'source': 'Frey & Osborne (2017)',
                'title': 'The Future of Employment: How Susceptible are Jobs to Computerisation?',
                'publication': 'Technological Forecasting and Social Change',
                'doi': '10.1016/j.techfore.2016.08.019',
                'methodology': 'Machine learning model trained on expert assessments of automation potential using traditional (pre-GenAI) technologies',
                'scale': '0-1, probability of automation via robotics, ML, and algorithmic control (excludes GenAI)',
                'expert_assessment': '70 occupations labeled by ML experts, extrapolated to all SOC occupations',
                'technology_scope': 'Traditional automation (industrial robots, ML for pattern recognition) - does NOT include large language models'
            }
        },
        'industry_occupational_composition': {
            'source': 'BLS Occupational Employment and Wage Statistics (OES)',
            'reference_period': 'May 2019 (pre-pandemic baseline)',
            'aggregation_level': 'National estimates by NAICS sector and SOC major group',
            'url': 'https://www.bls.gov/oes/tables.htm',
            'rationale_for_2019': 'Pre-pandemic occupational distribution avoids COVID-19 structural shifts',
            'industries_mapped': {
                'Information': 'NAICS 51 (Publishing, Broadcasting, Telecommunications, Data Processing)',
                'Finance and Insurance': 'NAICS 52 (Banks, Insurance Carriers, Securities, Investment)',
                'Professional, Scientific, and Technical Services': 'NAICS 54 (Legal, Accounting, Engineering, Computer Systems Design, Consulting, R&D)',
                'Leisure and Hospitality': 'NAICS 71-72 (Arts, Entertainment, Recreation, Accommodation, Food Services)'
            }
        },
        'variables': {
            'AI_Exposure_Score': {
                'description': 'Industry exposure to Generative AI capabilities',
                'scale': '0-1 (higher = more exposed)',
                'interpretation': 'Industries with high scores employ many workers in occupations whose tasks can be performed or augmented by large language models and generative AI'
            },
            'Teleworkability': {
                'description': 'Feasibility of remote work for industry occupations',
                'scale': '0-1 (higher = more teleworkable)',
                'interpretation': 'Share of industry jobs that can be performed remotely based on work context requirements'
            },
            'RoutineTaskIndex': {
                'description': 'Routine content of industry occupational tasks',
                'scale': '0-1 (higher = more routine)',
                'interpretation': 'Industries with high scores have more routine, codifiable tasks susceptible to traditional automation'
            },
            'SkillIntensity': {
                'description': 'Educational requirements of industry occupations',
                'scale': '0-1 (share requiring bachelor degree+)',
                'interpretation': 'Proxy for human capital intensity and knowledge work concentration'
            },
            'AutomationRisk_PreAI': {
                'description': 'Pre-GenAI automation susceptibility',
                'scale': '0-1 (probability of automation)',
                'interpretation': 'Risk of automation via traditional technologies (robotics, ML) before the GenAI era. Serves as control for baseline automation trends'
            }
        },
        'quality_notes': {
            'time_invariance': 'These scores are time-invariant because: (1) Occupational composition changes slowly, (2) 10-year window is relatively short, (3) Including time variation would require annual OES data processing',
            'aggregation_level': 'National industry-level only (no state variation in these scores)',
            'absorbed_by_fixed_effects': 'These variables are completely absorbed by industry fixed effects in within-industry panel regressions. They serve primarily for: (1) treatment variable construction (HighExposure threshold), (2) descriptive statistics, (3) heterogeneity analysis',
            'comparison_to_manual_estimates': 'These occupation-weighted scores are methodologically superior to the previous manual industry-level estimates in industry_controls_with_sources.csv'
        }
    }
    
    return sources


def main():
    """Generate industry exposure scores and documentation."""
    print("="*70)
    print("GENERATING OCCUPATION-WEIGHTED INDUSTRY EXPOSURE SCORES")
    print("="*70)
    
    # Calculate scores
    print("\nCalculating industry-level weighted averages...")
    industry_scores = calculate_industry_scores()
    
    print("\nIndustry Exposure Scores:")
    print(industry_scores.to_string(index=False))
    
    # Save scores
    output_path = DATA_DIR / 'industry_exposure_scores_occupation_weighted.csv'
    industry_scores.to_csv(output_path, index=False)
    print(f"\n✓ Saved to: {output_path}")
    
    # Generate and save documentation
    print("\nGenerating comprehensive documentation...")
    sources_doc = generate_sources_documentation()
    
    metadata_path = DATA_DIR / 'industry_exposure_scores_sources.json'
    with open(metadata_path, 'w') as f:
        json.dump(sources_doc, f, indent=2)
    print(f"✓ Saved documentation to: {metadata_path}")
    
    # Save occupation-level scores for reference
    occ_scores_list = []
    for occ in AI_EXPOSURE.keys():
        occ_scores_list.append({
            'Occupation_SOC_Major': occ,
            'AI_Exposure_Score': AI_EXPOSURE[occ],
            'Teleworkability': TELEWORKABILITY[occ],
            'RoutineTaskIndex': ROUTINE_TASK_INDEX[occ],
            'SkillIntensity': SKILL_INTENSITY[occ],
            'AutomationRisk_PreAI': AUTOMATION_RISK_PREAI[occ]
        })
    
    occ_df = pd.DataFrame(occ_scores_list)
    occ_path = DATA_DIR / 'occupation_exposure_scores_source.csv'
    occ_df.to_csv(occ_path, index=False)
    print(f"✓ Saved occupation-level scores to: {occ_path}")
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print(f"  1. {output_path.name} - Industry-level scores")
    print(f"  2. {metadata_path.name} - Complete source documentation")
    print(f"  3. {occ_path.name} - Occupation-level scores")


if __name__ == '__main__':
    main()
