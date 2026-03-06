#!/bin/bash
# Atlas scheduler launcher - used by launchd
# This wrapper activates the venv properly to avoid permission issues

cd /Users/kalamakuntlarakeshreddy/Desktop/A-Glass-Box-AI-Orchestration-Dashboard
source .venv/bin/activate
exec python scheduler.py
