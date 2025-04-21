# Documentation for the Project

## Overview
This project is a Flask-based web application that integrates with multiple OAuth providers (Spotify, GitHub, Twitch) to authenticate users and provide personalized services. It also includes a chat interface powered by an LLM (Large Language Model) for generating responses and interacting with external data sources.

---

## Features
1. **OAuth Integration**:
   - Supports Spotify, GitHub, and Twitch for user authentication.
   - Fetches user details like email, profile image, and username from the respective providers.

2. **Chat Interface**:
   - Users can interact with an AI-powered chat system.
   - Supports context-aware responses and integrates external data sources when required.

3. **Database Integration**:
   - Uses SQLAlchemy for database operations.
   - Stores user details and session data.

4. **LLM Integration**:
   - Generates responses based on user prompts.
   - Can query external vector databases for additional context.

5. **Background Jobs**:
   - Includes a scheduler for periodic tasks (e.g., Spotify user data processing).

---

## File Structure
### `web.py`
- **Purpose**: Main entry point for the Flask application.
- **Key Routes**:
  - `/`: Renders the main page (requires login).
  - `/login`: Displays the login page with OAuth links.
  - `/callback`: Handles OAuth callback and processes user login.
  - `/prompt`: Processes user prompts and generates AI responses.
  - `/logout`: Logs out the user and clears the session.

### `helpers.py`
- **Purpose**: Contains utility functions for OAuth processing and LLM prompt building.
- **Key Functions**:
  - `get_user_data_from_oauth`: Fetches user details from the OAuth provider.
  - `login_user_process`: Handles user login and database operations.
  - `build_llm_prompt`: Constructs a prompt for the LLM.
  - `requires_vector_data`: Determines if external data is needed for a prompt.

### `templates/index.html`
- **Purpose**: Frontend template for the main page.
- **Key Features**:
  - Displays user details (email, Spotify profile link).
  - Chat interface for interacting with the AI.

---

## Key Components
### OAuth Integration
- **Libraries Used**:
  - `flask_login` for user session management.
  - Custom services (`SpotifyUserService`, `GithubUserService`, etc.) for fetching user details.
- **Environment Variables**:
  - `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`: Required for Spotify OAuth.
  - `DB_URI`: Database connection string.

### Chat System
- **Session Management**:
  - Stores chat history in the session for context-aware responses.
- **LLM Integration**:
  - Uses an LLM to generate responses.
  - Can query external vector databases for additional context.

### Database
- **Model**: `User`
  - Stores user details like `oauth_id`, `username`, `email`, and tokens.
- **Operations**:
  - Checks if a user exists in the database.
  - Adds new users during the login process.

---

## API Endpoints
### `/`
- **Method**: `GET`
- **Description**: Renders the main page.
- **Authentication**: Required.

### `/login`
- **Method**: `GET`
- **Description**: Displays the login page with OAuth links.

### `/callback`
- **Method**: `GET`
- **Description**: Handles OAuth callback and processes user login.

### `/prompt`
- **Method**: `POST`
- **Description**: Processes user prompts and generates AI responses.
- **Request Body**:
  ```json
  {
    "prompt": "Your question or input here"
  }
  ```

### `/logout`
- **Method**: `GET`
- **Description**: Logs out the user and clears the session.

---

## Environment Variables
- `FLASK_SECRET_KEY`: Secret key for Flask sessions.
- `DB_URI`: Database connection string.
- `SPOTIFY_CLIENT_ID`: Spotify OAuth client ID.
- `SPOTIFY_CLIENT_SECRET`: Spotify OAuth client secret.

---

## Scheduler
- **Library**: `flask_apscheduler`
- **Task**: Runs periodic jobs (e.g., Spotify user data processing).
- **Example**:
  - A job runs every 20 minutes to perform dynamic tasks.

---

## Error Handling
- **401 Unauthorized**:
  - Triggered when a user tries to access a protected route without logging in.
- **404 Not Found**:
  - Triggered when a requested page does not exist.

---

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   export FLASK_SECRET_KEY="your_secret_key"
   export DB_URI="your_database_uri"
   export SPOTIFY_CLIENT_ID="your_spotify_client_id"
   export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
   ```
3. Run the application:
   ```bash
   python web.py
   ```

---

## Future Improvements
- Add support for more OAuth providers.
- Enhance error handling and logging.
- Optimize LLM integration for faster responses.