# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Secret_Hitler
import pickle

import sys
import os


# Run python -i game_peek.py [GAME SAVE] to interact with, get info from, and resave a game

game = Secret_Hitler.Game.load(sys.argv[1])
