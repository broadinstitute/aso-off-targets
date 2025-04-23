Here's a comprehensive `README.md` for your ASO Off-Target Checker application:

```markdown
# ASO Off-Target Checker

A Flask web application for checking antisense oligonucleotide (ASO) off-target effects using NCBI BLAST.

![Screenshot of ASO Off-Target Checker](screenshot.png) *(Example screenshot - add your own later)*

## Features

- **Sequence Analysis**: Check ASO sequences for potential off-target binding
- **Multiple Species Support**: 
  - Human (*Homo sapiens*, taxid: 9606)
  - Mouse (*Mus musculus*, taxid: 10090)
  - Rat (*Rattus norvegicus*, taxid: 10116)
- **Customizable Parameters**: Adjustable E-value and mismatch thresholds
- **Downloadable Results**: Export results in tab-delimited text format
- **User-Friendly Interface**: Clean, responsive web interface with collapsible advanced options

## Prerequisites

Before running the application, ensure you have:

1. **NCBI BLAST+** installed locally
   - Download from: [https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download](https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download)
   
2. **BLAST Databases** set up:
   - Requires `refseq_select_rna` database
   - Can be downloaded using NCBI's `update_blastdb.pl` script

3. **Python 3.7+** with the following packages (install via `requirements.txt`)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/aso-offtarget-checker.git
   cd aso-offtarget-checker
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up BLASTDB environment variable** (critical for BLAST to find databases):
   ```bash
   export BLASTDB=/path/to/your/blast/databases
   ```
   *Note: Add this to your shell configuration file (e.g., `.bashrc`, `.zshrc`) to make it persistent.*

4. Verify BLAST installation:
   ```bash
   blastn -version
   ```

## Usage

### Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at:
```
http://localhost:8080/check-aso
```

### Using the Web Interface

1. **Enter ASO Sequence**:
   - Input your ASO sequence (DNA only, ACGTN characters)
   - Default example sequence provided

2. **Select Species**:
   - Choose from Human, Mouse, or Rat

3. **Advanced Options** (click to expand):
   - **E-value threshold**: Default = 1000 (higher values return more results)
   - **Max mismatches**: Default = 4 (maximum allowed mismatches)

4. **Run Analysis**:
   - Click "Run BLAST" to start the search
   - Results typically appear within seconds to minutes depending on query length

5. **Download Results**:
   - After analysis, click "Download Results" to save as text file
   - Filename includes species and timestamp for easy identification

## Configuration

### Environment Variables

For proper BLAST operation, these environment variables may need configuration:

```bash
# Path to BLAST databases (REQUIRED)
export BLASTDB=/path/to/blast/databases

# Optional: Increase number of threads for BLAST
export BLASTNUM_THREADS=4
```

### Application Settings

Modify `app.py` for these options:

- Change default port (currently 8080)
- Adjust default sequence parameters
- Modify BLAST command options (e.g., `-num_alignments`)

## Troubleshooting

### Common Issues

1. **BLAST Database Not Found**:
   ```
   Error: BLAST database not found
   ```
   - Solution: Verify `BLASTDB` environment variable points to correct directory
   - Ensure required databases (refseq_select_rna) are present

2. **Invalid Sequence Error**:
   - Only ACGTN characters allowed
   - Sequences are automatically converted to uppercase

3. **No Results Found**:
   - Try increasing E-value threshold
   - Increase maximum allowed mismatches
   - Verify your sequence doesn't contain invalid characters

## Technical Details

### BLAST Parameters

The application uses these BLASTN parameters by default:
```bash
blastn \
  -task blastn-short \
  -db refseq_select_rna \
  -outfmt 5 `# XML file` \ 
  -evalue [user_specified] \
  -num_alignments 5000 \
  -taxids [selected_species_taxid]
```

### Data Processing

1. XML output from BLAST is parsed using Python's ElementTree
2. Results are filtered by:
   - Frame = 1 (forward strand only)
   - User-specified mismatch threshold
3. Alignment visualization shows:
   - Query sequence
   - Midline (match indicators)
   - Hit sequence

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NCBI for BLAST software and databases
- Flask for web framework
- Pandas for data processing
```

### Key Notes About BLASTDB:

1. **Critical Requirement**: I've emphasized the need to set the `BLASTDB` environment variable in multiple sections since this is a common point of failure.

2. **Troubleshooting Section**: Added specific guidance for database-related errors.

3. **Installation Instructions**: Included clear steps for verifying BLAST installation.

4. **Technical Details**: Explained the BLAST parameters being used so users understand the analysis.

5. **Visual Cues**: Left a placeholder for a screenshot (you should add an actual screenshot later).

This README provides comprehensive documentation while keeping the BLASTDB requirement prominent. Users should have all necessary information to install, configure, and troubleshoot the application.
