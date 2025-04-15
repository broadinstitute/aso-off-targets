# ASO Off-Target Checker (Web-Based)

This is a simple web application built with Python Flask to check potential off-targets of Anti-Sense Oligonucleotides (ASOs) in the human genome using remote NCBI BLAST.

## Overview

The application provides a user-friendly web interface where users can:

1.  **Input their ASO sequence.**
2.  **(Optional)** Specify an E-value threshold for BLAST results.
3.  **(Optional)** Specify a minimum percentage identity for filtering BLAST hits.
4.  **Run a remote NCBI BLASTN search** against the human RefSeq RNA database (`refseq_rna`) to find potential off-targets.
5.  **View the BLAST results** directly in the browser.
6.  **Download the raw tabular BLAST results** as a text file.

## Prerequisites

To run this application locally for development or testing, you need:

* **Python 3.x** installed on your system.
* **pip** (Python package installer) installed.

## Setup and Local Execution

1.  **Clone or download the repository** (if you have the code in a repository). If you've been following the previous steps, you should have `app.py` and a `templates` folder with `index.html`.

2.  **Navigate to the project directory** in your terminal or command prompt.

3.  **Install Flask:**
    ```bash
    pip install Flask
    ```

4.  **Run the Flask development server:**
    ```bash
    python app.py
    ```

5.  **Open your web browser** and go to `http://127.0.0.1:5000/`.

## Deployment (e.g., on AWS Elastic Beanstalk)

This application can be deployed to various web hosting platforms. The previous discussion mentioned AWS Elastic Beanstalk as a potentially free-tier option. Here's a general outline for deployment:

1.  **Package your application:** Create a ZIP file containing `app.py` and the `templates` folder.

2.  **Choose a hosting platform:** Select a platform that supports Python web applications (e.g., AWS Elastic Beanstalk, Heroku, PythonAnywhere).

3.  **Follow the platform's deployment instructions:** Each platform will have its own specific steps for deploying a Flask application. This usually involves creating an application on their service and uploading your packaged code.

4.  **Environment configuration (if needed):** Some platforms might require specific environment configurations.

## Usage

1.  Open the web application in your browser.
2.  In the "Enter your ASO sequence" text area, paste the sequence you want to analyze.
3.  **(Optional)** Adjust the "E-value threshold" and "Minimum % Identity" if you have specific requirements. Lower E-values and higher identity thresholds will result in more stringent filtering.
4.  Click the "Run BLAST" button.
5.  The results from the remote NCBI BLAST search will be displayed below the form. Each hit will show information like Query ID, Subject ID, % Identity, Alignment Length, E-value, and Bit Score.
6.  If results are present, a "Download Results as Text File" button will appear, allowing you to save the raw tabular BLAST output to a `.txt` file.

## Important Notes

* **Remote BLAST:** This application uses NCBI's servers to perform the BLAST search. Therefore, an active internet connection is required.
* **Database:** The search is performed against the human RefSeq RNA database (`refseq_rna`) and is limited to human sequences (`-taxid 9606`).
* **Performance:** The speed of the BLAST search depends on the length of your sequence and the load on NCBI's servers.
* **Interpretation of Results:** The results provide potential off-target binding sites based on sequence similarity. Further analysis and experimental validation are crucial to confirm actual off-target effects.
* **No Chemical Modifications:** This simple implementation does not account for any chemical modifications that might be present in your ASO, which can significantly affect binding affinity and specificity.
* **Error Handling:**
