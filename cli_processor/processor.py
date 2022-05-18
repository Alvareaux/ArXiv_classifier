#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from pipeline.clear_text import TextCleaner
from pipeline.preprocess_text import TextPreprocessor

# External


class Processor:
    def __init__(self):
        self.prc = TextPreprocessor()
        self.clr = TextCleaner()

    def process_text(self, text: str) -> str:
        text = self.clr.text_clearing_pipeline(text)
        text = self.prc.lemmatize(text)

        return text


if __name__ == '__main__':
    from addons.timer import Timer

    timer = Timer()
    prc = TextPreprocessor()
    clr = TextCleaner()

    text = '''A fully differential calculation in perturbative quantum chromodynamics is
presented for the production of massive photon pairs at hadron colliders. All
next-to-leading order perturbative contributions from quark-antiquark,
gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as
all-orders resummation of initial-state gluon radiation valid at
next-to-next-to-leading logarithmic accuracy. The region of phase space is
specified in which the calculation is most reliable. Good agreement is
demonstrated with data from the Fermilab Tevatron, and predictions are made for
more detailed tests with CDF and DO data. Predictions are shown for
distributions of diphoton pairs produced at the energy of the Large Hadron
Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs
boson are contrasted with those produced from QCD processes at the LHC, showing
that enhanced sensitivity to the signal can be obtained with judicious
selection of events.
    '''

    text = clr.text_clearing_pipeline(text)

    timer.start()
    print(prc.lemmatize(text))
    print(timer.finish())
