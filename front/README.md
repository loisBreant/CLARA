# CLARA Frontend

This repository contains the frontend application for the CLARA project, built with Next.js.

## Local Development

To get the frontend running on your local machine, follow these steps:

### Prerequisites

Ensure you have the following installed:

*   Node.js (v18 or later recommended)
*   pnpm (recommended package manager)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/clara-front.git # Replace with actual repo URL
    cd clara-front
    ```

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```

### Running the Development Server

1.  **Start the development server:**
    ```bash
    pnpm run dev
    ```
    The application will be accessible at `http://localhost:3000`.

## Docker Deployment

You can also run the frontend application using Docker. This is useful for consistent environments or deployment.

### Prerequisites

*   Docker installed on your system.

### Building the Docker Image

1.  **Build the Docker image:**
    ```bash
    docker build -t clara-frontend .
    ```
    This command builds an image named `clara-frontend`.

### Running the Docker Container

1.  **Run the Docker container:**
    ```bash
    docker run -p 3000:3000 clara-frontend
    ```
    This will start the frontend application inside a Docker container and map port `3000` from the container to port `3000` on your host machine. You can then access the application in your browser at `http://localhost:3000`.

