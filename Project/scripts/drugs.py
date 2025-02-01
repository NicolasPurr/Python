import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drugbank.parsers import *

with open("data/drugbank_partial.xml", "r", encoding="utf-8") as file:
    xml_content = file.read()