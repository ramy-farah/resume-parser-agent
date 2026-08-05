# Resume Parser Agent

An AI-powered agent that reads a resume (PDF or DOCX), extracts structured candidate data using the Claude API, and writes it to a CSV that mimics a contractor-onboarding "board" — inspired by a similar workflow I built in production at IBM to speed up contractor onboarding on a federal program.

## Problem

Onboarding new contractors typically involves manually reading each resume and re-typing key details (contact info, most recent role, skills, education) into a tracking system. This is slow, repetitive, and error-prone at any real volume.

## Approach

- **Input:** a resume file (PDF or DOCX)
- **Text extraction:** `pypdf` / `python-docx` pull raw text from the file
- **Structured extraction:** the raw text is sent to Claude (via the Anthropic API) with a prompt requesting a fixed JSON schema — name, email, phone, location, most recent title/company, estimated years of experience, top skills, and education
- **Output:** the parsed JSON is appended as a new row in `onboarding_board.csv`, simulating a live onboarding board that accumulates one row per candidate

The core design choice was keeping the extraction schema fixed and explicit in the prompt, so every resume — regardless of format or structure — maps to the same consistent set of fields, which is what makes the output usable in a downstream tracking system.

## Tech stack

- Python
- Anthropic API (Claude)
- `pypdf`, `python-docx` for file parsing
- CSV as a lightweight stand-in for a board/database

## Result

Running the script on a sample resume correctly extracts all fields into clean, structured JSON and appends it to the CSV — turning an unstructured PDF into usable, tabular data with a single function call.

## What I'd improve next

- **Error handling for edge cases:** the Claude API can occasionally decline to process a given input; the script should catch this gracefully rather than crashing (partially addressed, but worth hardening further)
- **Validation:** add checks to confirm extracted emails/phone numbers are well-formed before writing to the board
- **Batch processing:** extend the script to process a folder of resumes in one run instead of one file at a time
- **Real board integration:** swap the CSV output for an actual Monday.com (or Airtable) API call, closer to the original production tool

## Background

This project is a sanitized, from-scratch rebuild of a similar tool I built as a Data Analysis & Operations Consultant at IBM, where an AI-powered resume-parsing agent auto-populated a Monday.com board with contractor onboarding details, cutting manual data entry and improving processing efficiency by roughly 50%. This repo demonstrates the same core approach outside of any proprietary or federal program context.
