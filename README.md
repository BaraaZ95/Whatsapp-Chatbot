# Project Title

WhatsApp Chatbot for Real Estate Negotiations

## Overview

This project is a WhatsApp chatbot designed to negotiate with real estate agents in Dubai. It leverages scraped data from Bayut.com to provide information. The scraper code is available [here](https://github.com/BaraaZ95/Bayut-scraper). The backend is built using Flask, with ngrok used for port exposure. Twilio's WhatsApp API is employed for sending and receiving messages, and LangChain with OpenAI's ChatGPT is used for communication with real estate agents.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running the chatbot, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/BaraaZ95/Your-Repository.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Your-Repository
    ```

3. Build the Docker containers:

    ```bash
    docker-compose build
    ```

## Usage

To run the WhatsApp chatbot, follow these steps:

1. Start the Docker containers:

    ```bash
    docker-compose up
    ```

2. Access the chatbot on WhatsApp.

3. Interact with the chatbot and negotiate with real estate agents.

## License

This project is licensed under the [MIT License](LICENSE).
