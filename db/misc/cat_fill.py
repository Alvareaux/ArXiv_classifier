#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from db.db_connection.db_local import LocalConnectDB

# External
import sqlalchemy.exc


class CatFiller:
    cats = {
        'Physics': {
            'astro-ph.GA': 'Astrophysics of Galaxies',
            'astro-ph.CO': 'Cosmology and Nongalactic Astrophysics',
            'astro-ph.EP': 'Earth and Planetary Astrophysics',
            'astro-ph.HE': 'High Energy Astrophysical Phenomena',
            'astro-ph.IM': 'Instrumentation and Methods for Astrophysics',
            'astro-ph.SR': 'Solar and Stellar Astrophysics',
            'cond-mat.dis-nn': 'Disordered Systems and Neural Networks',
            'cond-mat.mtrl-sci': 'Materials Science',
            'cond-mat.mes-hall': 'Mesoscale and Nanoscale Physics',
            'cond-mat.other': 'Other Condensed Matter',
            'cond-mat.quant-gas': 'Quantum Gases',
            'cond-mat.soft': 'Soft Condensed Matter',
            'cond-mat.stat-mech': 'Statistical Mechanics',
            'cond-mat.str-el': 'Strongly Correlated Electrons',
            'cond-mat.supr-con': 'Superconductivity',
            'gr-qc': 'General Relativity and Quantum Cosmology',
            'hep-ex': 'High Energy Physics - Experiment',
            'hep-lat': 'High Energy Physics - Lattice',
            'hep-ph': 'High Energy Physics - Phenomenology',
            'hep-th': 'High Energy Physics - Theory',
            'math-ph': 'Mathematical Physics',
            'nlin.AO': 'Adaptation and Self-Organizing Systems',
            'nlin.CG': 'Cellular Automata and Lattice Gases',
            'nlin.CD': 'Chaotic Dynamics',
            'nlin.SI': 'Exactly Solvable and Integrable Systems',
            'nlin.PS': 'Pattern Formation and Solitons',
            'nucl-ex': 'Nuclear Experiment',
            'nucl-th': 'Nuclear Theory',
            'physics.acc-ph': 'Accelerator Physics',
            'physics.app-ph': 'Applied Physics',
            'physics.ao-ph': 'Atmospheric and Oceanic Physics',
            'physics.atom-ph': 'Atomic Physics',
            'physics.atm-clus': 'Atomic and Molecular Clusters',
            'physics.bio-ph': 'Biological Physics',
            'physics.chem-ph': 'Chemical Physics',
            'physics.class-ph': 'Classical Physics',
            'physics.comp-ph': 'Computational Physics',
            'physics.data-an': 'Data Analysis, Statistics and Probability',
            'physics.flu-dyn': 'Fluid Dynamics',
            'physics.gen-ph': 'General Physics',
            'physics.geo-ph': 'Geophysics',
            'physics.hist-ph': 'History and Philosophy of Physics',
            'physics.ins-det': 'Instrumentation and Detectors',
            'physics.med-ph': 'Medical Physics',
            'physics.optics': 'Optics',
            'physics.ed-ph': 'Physics Education',
            'physics.soc-ph': 'Physics and Society',
            'physics.plasm-ph': 'Plasma Physics',
            'physics.pop-ph': 'Popular Physics',
            'physics.space-ph': 'Space Physics',
            'quant-ph': 'Quantum Physics',
        },

        'Mathematics': {
            'math.AG': 'Algebraic Geometry',
            'math.AT': 'Algebraic Topology',
            'math.AP': 'Analysis of PDEs',
            'math.CT': 'Category Theory',
            'math.CA': 'Classical Analysis and ODEs',
            'math.CO': 'Combinatorics',
            'math.AC': 'Commutative Algebra',
            'math.CV': 'Complex Variables',
            'math.DG': 'Differential Geometry',
            'math.DS': 'Dynamical Systems',
            'math.FA': 'Functional Analysis',
            'math.GM': 'General Mathematics',
            'math.GN': 'General Topology',
            'math.GT': 'Geometric Topology',
            'math.GR': 'Group Theory',
            'math.HO': 'History and Overview',
            'math.IT': 'Information Theory',
            'math.KT': 'K-Theory and Homology',
            'math.LO': 'Logic',
            'math.MP': 'Mathematical Physics',
            'math.MG': 'Metric Geometry',
            'math.NT': 'Number Theory',
            'math.NA': 'Numerical Analysis',
            'math.OA': 'Operator Algebras',
            'math.OC': 'Optimization and Control',
            'math.PR': 'Probability',
            'math.QA': 'Quantum Algebra',
            'math.RT': 'Representation Theory',
            'math.RA': 'Rings and Algebras',
            'math.SP': 'Spectral Theory',
        },

        'Computer science': {
            'cs.AI': 'Artificial Intelligence',
            'cs.CL': 'Computation and Language',
            'cs.CC': 'Computational Complexity',
            'cs.CE': 'Computational Engineering, Finance, and Science',
            'cs.CG': 'Computational Geometry',
            'cs.GT': 'Computer Science and Game Theory',
            'cs.CV': 'Computer Vision and Pattern Recognition',
            'cs.CY': 'Computers and Society',
            'cs.CR': 'Cryptography and Security',
            'cs.DS': 'Data Structures and Algorithms',
            'cs.DB': 'Databases',
            'cs.DL': 'Digital Libraries',
            'cs.DM': 'Discrete Mathematics',
            'cs.DC': 'Distributed, Parallel, and Cluster Computing',
            'cs.ET': 'Emerging Technologies',
            'cs.FL': 'Formal Languages and Automata Theory',
            'cs.GL': 'General Literature',
            'cs.GR': 'Graphics',
            'cs.AR': 'Hardware Architecture',
            'cs.HC': 'Human-Computer Interaction',
            'cs.IR': 'Information Retrieval',
            'cs.IT': 'Information Theory',
            'cs.LG': 'Learning',
            'cs.LO': 'Logic in Computer Science',
            'cs.MS': 'Mathematical Software',
            'cs.MA': 'Multiagent Systems',
            'cs.MM': 'Multimedia',
            'cs.NI': 'Networking and Internet Architecture',
            'cs.NE': 'Neural and Evolutionary Computing',
            'cs.NA': 'Numerical Analysis',
        },

        'Quantitative biology': {
            'q-bio.BM': 'Biomolecules',
            'q-bio.GN': 'Genomics',
            'q-bio.MN': 'Molecular Networks',
            'q-bio.SC': 'Subcellular Processes',
            'q-bio.CB': 'Cell Behavior',
            'q-bio.NC': 'Neurons and Cognition',
            'q-bio.TO': 'Tissues and Organs',
            'q-bio.PE': 'Populations and Evolution',
            'q-bio.QM': 'Quantitative Methods',
            'q-bio.OT': 'Other',
        },

        'Quantitative finance': {
            'q-fin.PR': 'Pricing of Securities',
            'q-fin.RM': 'Risk Management',
            'q-fin.PM': 'Portfolio Management',
            'q-fin.TR': 'Trading and Microstructure',
            'q-fin.MF': 'Mathematical Finance',
            'q-fin.CP': 'Computational Finance',
            'q-fin.ST': 'Statistical Finance',
            'q-fin.GN': 'General Finance',
            'q-fin.EC': 'Economics',
        },

        'Statistics': {
            'stat.AP': 'Applications',
            'stat.CO': 'Computation',
            'stat.ML': 'Machine Learning',
            'stat.ME': 'Methodology',
            'stat.OT': 'Other Statistics',
            'stat.TH': 'Theory',
        },
    }

    def __init__(self, db):
        self.db = db

    def run(self, table_base, table_cat):
        unpack_dict = self.unpack_base(table_base)
        self.unpack(table_cat, unpack_dict)

    def unpack(self, table, unpack_dict):
        db_list = []

        i = 0
        for cat_key in self.cats.keys():
            for cat in self.cats[cat_key].keys():
                cat_id = unpack_dict[cat_key]

                db_dict = {
                    'id': i,
                    'base_id': cat_id,
                    'category': cat,
                    'description': self.cats[cat_key][cat]
                }

                db_list.append(db_dict)

                i += 1

        try:
            self.db.insert(table, db_list)
        except sqlalchemy.exc.IntegrityError as e:
            print(e)

    def unpack_base(self, table):
        id_dict = {}
        db_list = []

        for cat_key_pair in enumerate(self.cats.keys()):
            id_dict[cat_key_pair[1]] = cat_key_pair[0]

            db_dict = {
                'id': cat_key_pair[0],
                'base_category': cat_key_pair[1]
            }

            db_list.append(db_dict)

        try:
            self.db.insert(table, db_list)
        except sqlalchemy.exc.IntegrityError as e:
            print(e)

        return id_dict


if __name__ == '__main__':
    from db.db_init.db_init_base import BaseBase, base_name
    from db.db_init.db_init_base import BaseList, CatList

    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'

    db_loc = LocalConnectDB(BaseBase, base_name, config_path)
    filler = CatFiller(db_loc)

    filler.run(BaseList, CatList)
