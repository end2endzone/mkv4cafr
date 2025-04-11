#!/usr/bin/python

import sys

import os
from os import path

import io
import itertools as IT
import xml.etree.ElementTree as ET

import platform

LEVEL_SUCCESS = 0
LEVEL_WARNING = 1
LEVEL_ERROR = 2

# Queries examples:
# https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fend2endzone%2Ffa6f6ec2f8315e357405164b4d618ef4%2Fraw%2Fafe1c3be748e7a78bc905c322afbd9a24f1e328e%2Fmybadge.json
# https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fend2endzone%2Ffa6f6ec2f8315e357405164b4d618ef4%2Fraw%2F5df297ffc360897097974338d4d43ef69271831b%2Fmybadge.json
# https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fend2endzone%2Ffa6f6ec2f8315e357405164b4d618ef4%2Fraw%2Fmybadge.json

def getNamedLogo():
  # Search the running CI/CD service from environment variables
  namedLogo = ""
  if os.getenv('APPVEYOR', "") != "":
    namedLogo = "AppVeyor"
  elif os.getenv('TRAVIS', "") != "":
    namedLogo = "Travis CI"
  elif os.getenv('JENKINS_URL', "") != "":
    namedLogo = "Jenkins"
  elif os.getenv('GITHUB_ACTIONS', "") != "":
    if os.getenv('RUNNER_OS', "") == "macOS":
      namedLogo = "Apple"
    elif os.getenv('RUNNER_OS', "") == "Linux":
      namedLogo = "Linux"
    elif os.getenv('RUNNER_OS', "") == "Windows":
      namedLogo = "Windows"
    else:
      namedLogo = "GitHub"
  elif platform.system() == "Darwin":
      namedLogo = "Apple"
  elif platform.system() == "Linux":
      namedLogo = "Linux"
  elif platform.system() == "Windows":
      namedLogo = "Windows"
  return namedLogo

def getColorFromLevel(level):
  color = ""
  if level == LEVEL_SUCCESS:
    color = "Green"
  elif level == LEVEL_WARNING:
    color = "Orange"
  else:
    color = "Red"
  return color

def main():
  print("maketestbadge v1.2")
  
  # Validate input file
  if len(sys.argv)  == 2:
    file_path = sys.argv[1]
  else:
    print("Create endpoint badge json files from junit report. See https://shields.io/endpoint for details.")
    print("Missing input file. Please specify a path to an xml report.")
    sys.exit(1);
  if not path.isfile(file_path) or not path.exists(file_path):
    print("File not found: " + file_path)
    sys.exit(1);
  
  print("Creating badge from xml report '" + file_path + "' for https://shields.io/endpoint")
  
  # Parse the content of the file
  try:
    tree = ET.parse(file_path)
  except ET.ParseError as err:
    lineno, column = err.position
    err.msg = "Failed parsing file at line=" + str(lineno) + ", column=" + str(column) + "."
    #raise
    print(err.msg)
    sys.exit(1);
  root = tree.getroot()
  
  # Find the important attributes
  #testsuites = root.find('./testsuite')
  try:
    lines_valid = root.attrib['lines-valid']
    lines_covered = root.attrib['lines-covered']
    line_rate = root.attrib['line-rate']
  except KeyError as err:
    err.msg = "Failed to find attributes 'lines-valid' or 'lines-covered' values."
    #raise
    print(err.msg)
    sys.exit(1);
  lines_valid      = int(lines_valid  )
  lines_covered    = int(lines_covered)
  line_rate        = int((float(line_rate)+0.005)*100)
  print("Found coverage of " + str(line_rate) + "%, lines_valid: " + str(lines_valid) + " lines_covered: " + str(lines_covered) + ".")
  
  # Evaluate badge properties
  
  # badge_color, a.k.a message color
  if (line_rate <= 40):
    badge_color = "#da644d"  # red
  elif (line_rate <= 60):
    badge_color = "#d7af23"  # yellow
  elif (line_rate <= 80):
    badge_color = "#a2a328"  # sick green
  elif (line_rate <= 90):
    badge_color = "#97c510"  # greener
  else:
    badge_color = "#4dc71f"  # green
  
  # badge_message
  badge_message = str(line_rate) + "%"
  
  # other
  badge_schemaVersion = 1
  badge_label = "coverage"
  #badge_labelColor = "#5c5c5c"
  badge_namedLogo = getNamedLogo()
  badge_logoColor = "white"
  
  print("Creating " + badge_label + " badge: " + badge_namedLogo + ", " + badge_message)
  
  relative_path = "coverage.json"
  full_path = os.path.realpath(relative_path)
  
  # Save as badge.json
  try:
    text_file = open(full_path, "w")
    text_file.write("{\n")
    text_file.write("  \"schemaVersion\": {0},\n".format(badge_schemaVersion))
    text_file.write("  \"namedLogo\": \"{0}\",\n".format(badge_namedLogo))
    text_file.write("  \"logoColor\": \"{0}\",\n".format(badge_logoColor))
    text_file.write("  \"label\": \"{0}\",\n".format(badge_label))
    #text_file.write("  \"labelColor\": \"{0}\",\n".format(badge_labelColor))
    text_file.write("  \"color\": \"{0}\",\n".format(badge_color))
    text_file.write("  \"message\": \"{0}\"\n".format(badge_message))
    text_file.write("}\n")
    text_file.close()
  except OSError as err:
    err.msg = "Failed to save coverage.json."
    #raise
    print(err.msg)
    sys.exit(1);
  
  print("Saved badge as " + full_path)
  
if __name__ == "__main__":
  main()
  