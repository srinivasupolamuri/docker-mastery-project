# Phase 1 – Beginner Docker

## Overview

Phase 1 demonstrates the fundamentals of containerizing a FastAPI
application using Docker.

The application uses a single-stage Docker build based on Ubuntu 22.04.
Python, pip, FastAPI, Uvicorn, and the application code are installed
inside the Docker image.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- Ubuntu 22.04
- Docker
- WSL 2
- Docker Desktop

## Project Structure

```text
phase1-beginner/
├── app/
│   └── main.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
