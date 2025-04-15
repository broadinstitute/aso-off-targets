from flask import Flask, render_template, request, send_file
import subprocess
import os
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        aso_sequence = request.form['aso_sequence']
        evalue = request.form.get('evalue', '0.01')
        identity_threshold = request.form.get('identity', '80')

        if aso_sequence:
            results_file = run_remote_blast(aso_sequence, evalue)
            if results_file:
                results = process_blast_results(results_file, float(identity_threshold))
                os.remove(results_file)  # Clean up the temporary file

    return render_template('index.html', results=results)

def run_remote_blast(sequence, evalue):
    """Runs a remote NCBI BLASTN search and saves the results to a temporary file."""
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt")
        output_path = temp_file.name
        temp_file.close()

        command = [
            'blastn',
            '-query', '-',  # Read query from stdin
            '-db', 'refseq_rna',
            '-out', output_path,
            '-outfmt', '6',
            '-evalue', str(evalue),
            '-remote',
            '-taxid', '9606'  # Human sequences only
        ]

        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=sequence)

        if process.returncode == 0:
            return output_path
        else:
            print(f"BLAST error: Return code {process.returncode}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    except Exception as e:
        print(f"Error running BLAST: {e}")
        return None

def process_blast_results(blast_file, identity_threshold):
    """Reads the BLAST results file and filters by identity."""
    results = []
    try:
        with open(blast_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 12:
                    identity = float(parts[2])
                    if identity >= identity_threshold:
                        results.append({
                            'query_id': parts[0],
                            'subject_id': parts[1],
                            'identity': identity,
                            'alignment_length': int(parts[3]),
                            'mismatches': int(parts[4]),
                            'gap_opens': int(parts[5]),
                            'query_start': int(parts[6]),
                            'query_end': int(parts[7]),
                            'subject_start': int(parts[8]),
                            'subject_end': int(parts[9]),
                            'evalue': float(parts[10]),
                            'bit_score': float(parts[11])
                        })
    except FileNotFoundError:
        return "Error: BLAST results file not found."
    except Exception as e:
        return f"Error processing results: {e}"
    return results

@app.route('/download_results')
def download_results():
    results_data = request.args.get('results_data')
    if results_data:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(results_data)
            temp_file_path = tmp_file.name
        return send_file(temp_file_path, as_attachment=True, download_name='blast_results.txt')
    return "No results to download."

if __name__ == '__main__':
    app.run(debug=True)
