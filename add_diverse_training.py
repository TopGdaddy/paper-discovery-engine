"""
add_diverse_training.py - Add clearly different papers to improve training

THE PROBLEM:
============
Your classifier sees all papers as similar because they're ALL from AI/ML!
Even your "not relevant" papers are still about AI topics.

THE SOLUTION:
=============
Add papers from COMPLETELY DIFFERENT fields:
- Biology (fruit fly genetics, marine ecosystems)
- Economics (monetary policy, trade analysis)
- Physics (quantum mechanics, astrophysics)
- Medicine (clinical trials, drug studies)
- History (medieval periods, ancient civilizations)

These papers have VERY DIFFERENT vocabulary and concepts.
The embedding vectors will be FAR APART from your AI papers.
Now the classifier can easily draw a line between them!

BEFORE:
    All papers clustered together → No clear boundary → 50% accuracy

AFTER:
    AI papers in one area, Other papers far away → Clear boundary → 80%+ accuracy
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager


def main():
    print("=" * 70)
    print("📚 ADDING DIVERSE TRAINING DATA")
    print("=" * 70)
    print("\nThis will add papers from DIFFERENT FIELDS to help the model")
    print("learn what 'not relevant' really means!")
    
    db = DatabaseManager("data/papers.db")
    
    # =========================================================================
    # DIVERSE PAPERS FROM COMPLETELY DIFFERENT FIELDS
    # =========================================================================
    # These are designed to be as DIFFERENT as possible from AI/ML papers
    # The vocabulary, concepts, and topics are completely different
    
    diverse_papers = [
        # ----- BIOLOGY -----
        {
            'arxiv_id': 'diverse-bio-001',
            'title': 'Genetic Mechanisms of Drosophila Wing Development',
            'summary': 'We investigate the role of homeobox genes in fruit fly wing morphogenesis. Our analysis of gene expression patterns during larval stages reveals critical developmental pathways involving hedgehog and decapentaplegic signaling cascades. Mutant phenotypes demonstrate the essential nature of these pathways for proper wing formation.',
            'authors': 'Sarah Chen, Michael Rodriguez',
            'primary_category': 'q-bio.GN',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/bio1.pdf',
            'abs_url': 'https://example.com/bio1',
        },
        {
            'arxiv_id': 'diverse-bio-002', 
            'title': 'Coral Reef Ecosystem Dynamics Under Ocean Acidification',
            'summary': 'This study examines the impact of decreasing ocean pH on coral reef biodiversity in the Indo-Pacific region. We measured calcification rates, species diversity indices, and symbiotic zooxanthellae density across 47 reef sites. Results indicate significant bleaching events correlated with pH levels below 7.9.',
            'authors': 'James Williams, Lisa Park',
            'primary_category': 'q-bio.PE',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/bio2.pdf',
            'abs_url': 'https://example.com/bio2',
        },
        
        # ----- ECONOMICS -----
        {
            'arxiv_id': 'diverse-econ-001',
            'title': 'Monetary Policy Transmission in Emerging Markets',
            'summary': 'We analyze the effectiveness of central bank interest rate decisions on inflation control in developing economies. Using panel data from 23 countries over 2000-2022, we estimate vector autoregression models to quantify policy transmission lags. Our findings suggest weaker transmission in economies with underdeveloped financial sectors.',
            'authors': 'Robert Kim, Anna Petrov',
            'primary_category': 'econ.GN',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/econ1.pdf',
            'abs_url': 'https://example.com/econ1',
        },
        {
            'arxiv_id': 'diverse-econ-002',
            'title': 'Housing Price Bubbles and Mortgage Default Risk',
            'summary': 'This paper develops a theoretical framework for identifying real estate price bubbles using fundamental valuation metrics. We apply our methodology to the 2006-2008 housing crisis, demonstrating that loan-to-value ratios above 80% significantly increased default probabilities during the market correction.',
            'authors': 'David Miller, Jennifer Chang',
            'primary_category': 'econ.GN',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/econ2.pdf',
            'abs_url': 'https://example.com/econ2',
        },
        
        # ----- PHYSICS -----
        {
            'arxiv_id': 'diverse-phys-001',
            'title': 'Quantum Entanglement in Superconducting Qubit Arrays',
            'summary': 'We demonstrate Bell inequality violations in a 2D array of transmon qubits coupled via tunable couplers. Operating at 15 millikelvin, we achieve two-qubit gate fidelities of 99.4% and measure CHSH inequality S-values exceeding 2.7, confirming genuine multipartite entanglement.',
            'authors': 'Thomas Anderson, Marie Curie',
            'primary_category': 'quant-ph',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/phys1.pdf',
            'abs_url': 'https://example.com/phys1',
        },
        {
            'arxiv_id': 'diverse-phys-002',
            'title': 'Gravitational Wave Detection from Neutron Star Mergers',
            'summary': 'We report the detection of gravitational waves from a binary neutron star inspiral event at redshift z=0.03. The chirp mass of 1.186 solar masses and tidal deformability constraints are consistent with soft equations of state. Electromagnetic counterpart observations confirm kilonova emission.',
            'authors': 'John Smith, Elena Rossi',
            'primary_category': 'astro-ph.HE',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/phys2.pdf',
            'abs_url': 'https://example.com/phys2',
        },
        
        # ----- MEDICINE -----
        {
            'arxiv_id': 'diverse-med-001',
            'title': 'Phase III Trial of GLP-1 Agonists in Type 2 Diabetes',
            'summary': 'This randomized controlled trial evaluated semaglutide versus placebo in 1,200 patients with type 2 diabetes over 52 weeks. Primary endpoints included HbA1c reduction and cardiovascular outcomes. Treatment group showed mean HbA1c reduction of 1.4% and 21% lower major adverse cardiac events.',
            'authors': 'Patricia Wong, Ahmed Hassan',
            'primary_category': 'med.endo',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/med1.pdf',
            'abs_url': 'https://example.com/med1',
        },
        {
            'arxiv_id': 'diverse-med-002',
            'title': 'Vaccine Efficacy Against Respiratory Syncytial Virus',
            'summary': 'We conducted a multi-center trial of an RSV prefusion F protein vaccine in adults over 60 years. Among 24,000 participants, vaccine efficacy against RSV-associated lower respiratory tract disease was 82.6%. Adverse events were primarily mild injection site reactions.',
            'authors': 'Rachel Green, Carlos Mendez',
            'primary_category': 'med.inf',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/med2.pdf',
            'abs_url': 'https://example.com/med2',
        },
        
        # ----- CHEMISTRY -----
        {
            'arxiv_id': 'diverse-chem-001',
            'title': 'Synthesis of Organic Semiconductor Polymers',
            'summary': 'We present a novel Stille coupling route to synthesize thiophene-fused conjugated polymers with enhanced hole mobility. Characterization via cyclic voltammetry shows HOMO levels at -5.2 eV suitable for organic photovoltaic applications. Thin film transistors achieve mobilities of 2.3 cm²/Vs.',
            'authors': 'Kevin Zhang, Sophie Martin',
            'primary_category': 'chem.org',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/chem1.pdf',
            'abs_url': 'https://example.com/chem1',
        },
        
        # ----- GEOLOGY -----
        {
            'arxiv_id': 'diverse-geo-001',
            'title': 'Volcanic Magma Chamber Dynamics in the Cascades',
            'summary': 'Seismic tomography reveals low-velocity zones beneath Mount Rainier indicating partial melt accumulation at 8-12 km depth. Geodetic data shows radial deformation consistent with magma recharge rates of 0.001 km³/year. Implications for eruption hazard assessment are discussed.',
            'authors': 'Brian Taylor, Michelle Lee',
            'primary_category': 'geo.volc',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/geo1.pdf',
            'abs_url': 'https://example.com/geo1',
        },
        
        # ----- HISTORY (as if it were a paper) -----
        {
            'arxiv_id': 'diverse-hist-001',
            'title': 'Medieval Silk Road Trade Networks and Economic Development',
            'summary': 'This analysis examines commercial relationships between Venetian merchants and Central Asian khanates during the 13th-14th centuries. Documentary evidence from Genoese trading posts reveals complex credit instruments and insurance mechanisms that facilitated long-distance commerce.',
            'authors': 'Elizabeth Brown, Marco Polo',
            'primary_category': 'history',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/hist1.pdf',
            'abs_url': 'https://example.com/hist1',
        },
        
        # ----- ENVIRONMENTAL SCIENCE -----
        {
            'arxiv_id': 'diverse-env-001',
            'title': 'Arctic Permafrost Thaw and Methane Emissions',
            'summary': 'We quantify methane flux from thermokarst lakes in Siberian permafrost regions using eddy covariance measurements. Annual emissions of 42 g CH4/m² are observed, with ebullition contributing 60% of total flux. Climate projections suggest 30% increase by 2050 under RCP 8.5.',
            'authors': 'Olga Petrova, Hans Schmidt',
            'primary_category': 'env.sci',
            'published': datetime.now(),
            'pdf_url': 'https://example.com/env1.pdf',
            'abs_url': 'https://example.com/env1',
        },
    ]
    
    # =========================================================================
    # ADD PAPERS TO DATABASE AND LABEL THEM
    # =========================================================================
    
    print(f"\n📝 Adding {len(diverse_papers)} diverse papers...")
    print("-" * 50)
    
    added_count = 0
    skipped_count = 0
    
    for paper in diverse_papers:
        # Check if already exists
        existing = db.get_paper(paper['arxiv_id'])
        
        if existing:
            print(f"   ⏭️  Already exists: {paper['title'][:40]}...")
            skipped_count += 1
            continue
        
        # Add to database
        result = db.add_paper(paper)
        
        if result:
            # IMPORTANT: Label as NOT RELEVANT (0)
            db.label_paper(paper['arxiv_id'], label=0)
            print(f"   ✅ Added: {paper['title'][:45]}...")
            added_count += 1
        else:
            print(f"   ❌ Failed: {paper['title'][:40]}...")
    
    # =========================================================================
    # SHOW RESULTS
    # =========================================================================
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    
    print(f"\n   ✅ Added: {added_count} diverse papers")
    print(f"   ⏭️  Skipped: {skipped_count} (already existed)")
    
    # Get updated stats
    stats = db.get_stats()
    
    print(f"\n📊 NEW TOTALS:")
    print(f"   📝 Total labeled: {stats['labeled_papers']}")
    print(f"   👍 Relevant: {stats['positive_labels']}")
    print(f"   👎 Not Relevant: {stats['negative_labels']}")
    
    # Calculate balance
    if stats['positive_labels'] > 0 and stats['negative_labels'] > 0:
        ratio = stats['positive_labels'] / stats['negative_labels']
        print(f"\n   ⚖️  Balance ratio: {ratio:.1f}:1 (relevant:not relevant)")
        
        if 0.5 <= ratio <= 2.0:
            print("      ✅ Good balance!")
        else:
            print("      ⚠️  Slightly imbalanced, but should still work")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("\n   1. Retrain the classifier:")
    print("      python train_classifier.py")
    print("\n   2. Check if accuracy improved:")
    print("      python test_model.py")
    print("\n   3. Score all papers:")
    print("      python score_papers.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()