from flask import Flask, render_template, request, send_file, session
import subprocess
import os
import tempfile
import xml.etree.ElementTree as ET
import pandas as pd
import io
import time

app = Flask(__name__)

@app.route('/check-aso', methods=['GET', 'POST'])
def index():
    results_html = None
    results_data = None
    if request.method == 'POST':
        aso_sequence = request.form.get('aso_sequence', 'CACTTTGTGAGTATTC').upper()
        evalue = request.form.get('evalue', '1000')
        max_mismatch = int(request.form.get('identity', '4'))
        species = request.form.get('species', 'human')  # Get selected species

        # Map species to taxid
        taxid_map = {
            'human': '9606',
            'mouse': '10090',
            'rat': '10116'
        }
        taxid = taxid_map.get(species, '9606')  # Default to human

        if aso_sequence:
            if not all(c in 'ACGTN' for c in aso_sequence):
                return render_template('index.html', 
                                    error="Invalid sequence - only ACGTN characters allowed")
            
            blast_xml = run_remote_blast_xml(aso_sequence, evalue, taxid)
            if blast_xml:
                results_df = parse_blast_xml(blast_xml, len(aso_sequence), max_mismatch)
                results_df, results_html = format_results_to_html(results_df)
                
                if not results_df.empty:
                    output = io.StringIO()
                    output.write("\t".join([
                        "Index", "Name", "Accession", "Mismatch", "Alignment"
                    ]) + "\n")
                    
                    for i, row in results_df.iterrows():
                        output.write("\t".join([
                            str(row.get('Index', '')),
                            str(row.get('Name', '')),
                            str(row.get('Accession', '')),
                            str(row.get('Mismatch', '')),
                            str(row.get('Alignment', '')).replace('<br>', ' ')
                        ]) + "\n")
                    
                    results_data = output.getvalue()
                
                os.remove(blast_xml)

    return render_template('index.html', 
                         results_html=results_html,
                         results_data=results_data,
                         selected_species=request.form.get('species', 'human'))  # Pass selected species back

def run_remote_blast_xml(sequence, evalue, taxid='9606'):
    """Runs BLAST with XML output format"""
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".xml")
        output_path = temp_file.name
        temp_file.close()

        command = [
            'blastn',
            '-query', '-',
            '-db', 'refseq_select_rna',
            '-task', 'blastn-short',
            '-num_alignments', '5000',
            '-out', output_path,
            '-outfmt', '5',  # XML format
            '-evalue', str(evalue),
            '-taxids', str(taxid)  # Now using parameter
        ]

        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=sequence)

        if process.returncode == 0:
            return output_path
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    except Exception as e:
        print(f"Error running BLAST: {e}")
        return None

def parse_blast_xml(xml_file, query_length, max_mismatch):
    """Parse BLAST XML output and return DataFrame"""
    hit_info_list = []
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for iteration in root.findall('.//Iteration'):
            for hit in iteration.findall('.//Hit'):
                hit_def = hit.findtext('Hit_def')
                hit_accession = hit.findtext('Hit_accession')
                
                for hsp in hit.findall('.//Hsp'):
                    identity = int(hsp.findtext('Hsp_identity'))
                    mismatch = query_length - identity
                    
                    if mismatch > max_mismatch:
                        continue
                        
                    hit_frame = int(hsp.findtext('Hsp_hit-frame'))
                    
                    if hit_frame != 1:
                        continue
                        
                    hit_info = {
                        "Hit_Definition": hit_def,
                        "Hit_Accession": hit_accession,
                        "Identity": identity,
                        "Mismatch": mismatch,
                        "Query_Sequence": hsp.findtext('Hsp_qseq'),
                        "Hit_Sequence": hsp.findtext('Hsp_hseq'),
                        "Midline": hsp.findtext('Hsp_midline'),
                        "E_Value": float(hsp.findtext('Hsp_evalue')),
                        "Bit_Score": float(hsp.findtext('Hsp_bit-score'))
                    }
                    hit_info_list.append(hit_info)
                    
        return pd.DataFrame(hit_info_list)
        
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()

def format_results_to_html(df):
    """Format the results DataFrame into HTML"""
    if df.empty:
        return "<p>No significant hits found based on your criteria.</p>"
    
    # Extract gene names from Hit_Definition
    df['Name'] = df['Hit_Definition'].str.extract(r".*\(([a-zA-Z0-9]+)\),.*")
    df['Accession'] = df['Hit_Accession']
    
    # Create alignment strings
    df['Alignment'] = df.apply(lambda x: f"{x['Query_Sequence']}\n{x['Midline']}\n{x['Hit_Sequence']}", axis=1)
    
    # Sort and select columns
    df = df.sort_values(['Mismatch', 'Name'])
    df = df.assign(Index=range(1, len(df)+1))
    df = df[['Index', 'Name', 'Accession', 'Mismatch', 'Alignment']]
    
    # Convert newlines to HTML line breaks in Alignment column
    df['Alignment'] = df['Alignment'].apply(lambda x: x.replace('\n', '<br>'))
    
    # Generate HTML table
    html_table = df.to_html(classes='blast-results', index=False, escape=False)
    
    # Create complete HTML with proper styling
    html_output = f"""
    <div class="blast-results-container">
        {html_table}
    </div>
    <style>
        .blast-results {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-family: Arial, sans-serif;
        }}
        .blast-results th {{
            background-color: #f2f2f2;
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        .blast-results td {{
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: top;
        }}
        .blast-results tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        /* Target the Alignment column specifically */
        .blast-results td:nth-child(5) {{
            font-family: 'Courier New', Courier, monospace;
            white-space: pre-wrap;
        }}
        /* Style for line breaks in the alignment */
        .blast-results td br {{
            display: block;
            content: "";
            margin: 2px 0;
        }}
    </style>
    """
    
    return df, html_output

@app.route('/download_results')
def download_results():
    # Get the raw tab-delimited data and species from the form
    results_data = request.args.get('results_data', '')
    species = request.args.get('species', 'human')
    
    if not results_data:
        return "No results to download"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(results_data)
        temp_path = tmp_file.name
    
    # Generate download filename with species and timestamp
    filename = f"blast_results_{species}_{time.strftime('%Y%m%d-%H%M%S')}.txt"
    
    # Send the file for download
    return send_file(
        temp_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/plain'
    )

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)