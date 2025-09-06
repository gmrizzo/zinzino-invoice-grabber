# Zinzino Invoice Grabber

This project is a Python script that automates the process of downloading paid invoices from your Zinzino account. It uses Selenium to log in, navigate to your orders, and save the invoices as PDF files.

## Features

-   Logs into your Zinzino account with your credentials.
-   Navigates to the "Aufträge" (Orders) page.
-   Filters for "BEZAHLT" (Paid) invoices.
-   Downloads invoices from a specific month.
-   Can be run locally or within a Docker container.

## Installation and Configuration

### Prerequisites

-   Python 3
-   Docker (optional, for containerized execution)

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/zinzino-invoice-grabber.git
    cd zinzino-invoice-grabber
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your credentials:**
    Create a `.env` file in the project root and add your Zinzino credentials. You can add multiple accounts.

    ```
    USERNAME_1=your_username_1
    PASSWORD_1=your_password_1
    USERNAME_2=your_username_2
    PASSWORD_2=your_password_2
    ```

    You can also specify a month to download invoices from. If not specified, it will download invoices from the previous month. The format is `MM.YYYY`.

    ```
    MONTH=08.2025
    ```

## Usage

### Running the script locally

To run the script, simply execute the `main.py` file:

```bash
python main.py
```

The downloaded invoices will be saved in the `pdf_rechnungen` directory.

### Running with Docker

You can also build and run the script within a Docker container.

1.  **Build the Docker image:**
    ```bash
    docker build -t zinzino-invoice-grabber .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run --rm -v $(pwd)/pdf_rechnungen:/app/pdf_rechnungen zinzino-invoice-grabber
    ```

