# AI Interview Chatbot

This Python project is an AI-powered chatbot that conducts interviews using job data extracted from the Python Job Scraper. It leverages FastAPI for backend services and Streamlit for the frontend interface. The chatbot asks relevant technical questions, evaluates responses, and provides feedback to simulate a real job interview experience.

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Accessing the Frontend](#accessing-the-frontend)
  - [Starting an Interview](#starting-an-interview)
- [Backend API Endpoints](#backend-api-endpoints)
- [Future Improvements](#future-improvements)


## About the Project

The AI Interview Chatbot project aims to provide an interactive interview simulation for job candidates. It combines web scraping, AI capabilities, and a web-based user interface to create an engaging and educational interview experience. The job data is sourced from my previous project - Python Job Scraper, making it easy to adapt the project for various roles and industries.

## Features

- **AI-Driven Interview Questions**: Generates technical questions using OpenAI's API to assess candidates.
- **Interview Simulation**: Evaluates candidate responses, provides hints, and guides the interview process.
- **Job Integration**: Uses job data scraped from the Python Job Scraper project.
- **Frontend and Backend Separation**: FastAPI for backend services and Streamlit for user interface.

## Technologies Used

- **Python**: Core programming language.
- **FastAPI**: Backend API development.
- **OpenAI API**: Generates interview questions and responses.
- **SQLAlchemy**: ORM for database access, using data generated from the Python Job Scraper.
- **Streamlit**: Frontend interface for managing the interview.
- **Docker & Docker Compose**: Containerization for backend and frontend environments.

## Project Structure

```
AI_INTERVIEW_CHATBOT/
├── backend/
│   ├── ai.py — AI interaction logic using OpenAI
│   ├── database.py - Database connection setup
│   ├── dockerfile — Dockerfile for backend container
│   ├── main.py — FastAPI entry point for handling interview interactions
│   ├── models.py — SQLAlchemy models to define the database schema
│   └── requirements.txt — Python package dependencies for backend
├── frontend/
│   ├── api_utils.py - Helper functions for communicating with the backend API
│   ├── dockerfile - Dockerfile for frontend container
│   ├── requirements.txt - Python package dependencies for frontend
│   └── streamlit_app.py - Streamlit frontend application
├── .env — Stores environment variables
├── docker-compose.yml - Docker Compose file for orchestrating containers
└── README.md — Project documentation
```

## Setup and Installation

### Prerequisites

- Python 3.11
- pip
- Docker & Docker Compose
- PostgreSQL database instance
- API Key from OpenAI

### Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/reneczka/ai-interview-chatbot.git
   cd ai-interview-chatbot
   ```

2. **Set up the environment variables:**

   Create a `.env` file in the project root directory. You can find `.env.example` in the repository

3. **Build and run Docker containers:**

   Use Docker Compose to build and run the containers:

   ```sh
   docker-compose up --build
   ```

   This command will start both the backend API (FastAPI) and the frontend (Streamlit).

## Usage

### Accessing the Frontend

1. **Access the frontend application:**

   Once the Docker containers are running, open a browser and visit:

   [http://localhost:8501](http://localhost:8501)

   The application will prompt you to select a job listing and start an interview.

### Starting an Interview

- **Choose a job** from the displayed list and click **"Start Interview."**
- **Answer the questions** in the chat interface; the AI will respond based on your answers.

## Backend API Endpoints

- **`GET /jobs/`**: Retrieve a list of all available job positions from the database.
- **`POST /message/`**: Send user input during the interview and get the AI's response.

## Future Improvements

- **Additional Job Boards**: Expand data integration to include other job boards.
- **Advanced Interview Scenarios**: Add different types of interview scenarios (e.g., behavioral, problem-solving).
- **User Management**: Implement user authentication and management features.

## All Done!

You're good to go! This project offers an interactive experience for job candidates and can be expanded in the future to incorporate more features, such as integration with other job boards.

