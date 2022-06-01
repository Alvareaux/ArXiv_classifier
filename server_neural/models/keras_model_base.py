#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import pickle

# Internal

# External
import tensorflow as tf
from tensorflow.keras.models import load_model


class KerasModel:
    tokenizer = None
    model = None

    def __init__(self, model_path):
        self.model_path = model_path

        self.load_model()

    def load_model(self):
        self.model = load_model(self.model_path)

    def score_text(self, text):
        pred_tags_scores = self.model.predict([text])[0]
        pred_tags = {int(pair[0] + 1): pair[1] for pair in list(enumerate(pred_tags_scores))}

        return pred_tags

